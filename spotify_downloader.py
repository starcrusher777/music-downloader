#!/usr/bin/env python3
"""
Spotify Playlist/Album Downloader
Downloads playlists and albums from Spotify by searching and downloading from hitmotop.com
"""

import os
import sys
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from hitmotop_parser import HitmotopParser
from file_manager import FileManager

# Load environment variables
load_dotenv()


class SpotifyDownloader:
    def __init__(self, log_callback=None):
        """
        Initialize Spotify API client and download components
        
        Args:
            log_callback: Optional callback function for logging (takes message string)
        """
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8888/callback')
        self.username = os.getenv('SPOTIFY_USERNAME')
        self.log_callback = log_callback
        
        if not all([self.client_id, self.client_secret, self.username]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USERNAME"
            )
        
        # Initialize Spotify client
        # Scope для доступа к публичным плейлистам других пользователей
        scope = "user-library-read playlist-read-private playlist-read-collaborative"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope
        ))
        
        # Initialize download components
        # Используем сессию из парсера для FileManager, чтобы сохранять cookies
        self.parser = HitmotopParser()
        self.file_manager = FileManager(session=self.parser.session)
    
    def _log(self, message: str):
        """Внутренний метод для логирования"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
        
    def get_user_playlists(self) -> List[Dict]:
        """Get all playlists from user's profile"""
        self._log("Fetching playlists from Spotify...")
        playlists = []
        results = self.sp.current_user_playlists(limit=50)
        
        while results:
            playlists.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        self._log(f"Found {len(playlists)} playlists")
        return playlists
    
    def get_user_albums(self) -> List[Dict]:
        """Get all saved albums from user's profile"""
        self._log("Fetching saved albums from Spotify...")
        albums = []
        results = self.sp.current_user_saved_albums(limit=50)
        
        while results:
            albums.extend([item['album'] for item in results['items']])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        self._log(f"Found {len(albums)} saved albums")
        return albums
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from a playlist"""
        tracks = []
        results = self.sp.playlist_tracks(playlist_id, limit=100)
        
        while results:
            tracks.extend([
                item['track'] for item in results['items'] 
                if item['track'] is not None
            ])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        return tracks
    
    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from an album"""
        results = self.sp.album_tracks(album_id, limit=50)
        tracks = []
        
        while results:
            tracks.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        return tracks
    
    def download_playlist(self, playlist: Dict):
        """Download all tracks from a playlist"""
        playlist_id = playlist['id']
        playlist_name = self.file_manager.sanitize_filename(playlist['name'])
        playlist_image = playlist['images'][0]['url'] if playlist['images'] else None
        
        self._log(f"\n{'='*60}")
        self._log(f"Processing playlist: {playlist['name']}")
        self._log(f"{'='*60}")
        
        # Get tracks
        tracks = self.get_playlist_tracks(playlist_id)
        self._log(f"Found {len(tracks)} tracks in playlist")
        
        # Create playlist directory
        playlist_dir = self.file_manager.create_playlist_directory(playlist_name)
        
        # Download cover image
        if playlist_image:
            self.file_manager.download_cover(playlist_image, playlist_dir, 'cover.jpg')
        
        # Download each track
        downloaded = 0
        failed = 0
        
        for idx, track in enumerate(tracks, 1):
            if not track:
                continue
                
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            search_query = f"{artists} {track_name}"
            
            self._log(f"\n[{idx}/{len(tracks)}] Searching for: {search_query}")
            
            try:
                download_url = self.parser.search_and_get_download_url(search_query)
                if download_url:
                    filename = self.file_manager.sanitize_filename(f"{artists} - {track_name}.mp3")
                    filepath = os.path.join(playlist_dir, filename)
                    
                    if self.file_manager.download_file(download_url, filepath):
                        self._log(f"✓ Downloaded: {filename}")
                        downloaded += 1
                    else:
                        self._log(f"✗ Failed to download: {filename}")
                        failed += 1
                else:
                    self._log(f"✗ Track not found on hitmotop.com")
                    failed += 1
            except Exception as e:
                self._log(f"✗ Error: {str(e)}")
                failed += 1
        
        self._log(f"\n{'='*60}")
        self._log(f"Playlist '{playlist_name}' completed:")
        self._log(f"  Downloaded: {downloaded}")
        self._log(f"  Failed: {failed}")
        self._log(f"{'='*60}\n")
    
    def download_album(self, album: Dict):
        """Download all tracks from an album"""
        album_id = album['id']
        album_name = self.file_manager.sanitize_filename(album['name'])
        album_artist = ', '.join([artist['name'] for artist in album['artists']])
        album_image = album['images'][0]['url'] if album['images'] else None
        
        self._log(f"\n{'='*60}")
        self._log(f"Processing album: {album_artist} - {album_name}")
        self._log(f"{'='*60}")
        
        # Get tracks
        tracks = self.get_album_tracks(album_id)
        self._log(f"Found {len(tracks)} tracks in album")
        
        # Create album directory
        album_dir = self.file_manager.create_album_directory(album_artist, album_name)
        
        # Download cover image
        if album_image:
            self.file_manager.download_cover(album_image, album_dir, 'cover.jpg')
        
        # Download each track
        downloaded = 0
        failed = 0
        
        for idx, track in enumerate(tracks, 1):
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            search_query = f"{artists} {track_name}"
            
            self._log(f"\n[{idx}/{len(tracks)}] Searching for: {search_query}")
            
            try:
                download_url = self.parser.search_and_get_download_url(search_query)
                if download_url:
                    filename = self.file_manager.sanitize_filename(f"{artists} - {track_name}.mp3")
                    filepath = os.path.join(album_dir, filename)
                    
                    if self.file_manager.download_file(download_url, filepath):
                        self._log(f"✓ Downloaded: {filename}")
                        downloaded += 1
                    else:
                        self._log(f"✗ Failed to download: {filename}")
                        failed += 1
                else:
                    self._log(f"✗ Track not found on hitmotop.com")
                    failed += 1
            except Exception as e:
                self._log(f"✗ Error: {str(e)}")
                failed += 1
        
        self._log(f"\n{'='*60}")
        self._log(f"Album '{album_name}' completed:")
        self._log(f"  Downloaded: {downloaded}")
        self._log(f"  Failed: {failed}")
        self._log(f"{'='*60}\n")
    
    def download_all_playlists(self):
        """Download all user playlists"""
        playlists = self.get_user_playlists()
        
        for playlist in playlists:
            try:
                self.download_playlist(playlist)
            except Exception as e:
                print(f"Error downloading playlist '{playlist['name']}': {str(e)}")
                continue
    
    def download_all_albums(self):
        """Download all user saved albums"""
        albums = self.get_user_albums()
        
        for album in albums:
            try:
                self.download_album(album)
            except Exception as e:
                print(f"Error downloading album '{album['name']}': {str(e)}")
                continue
    
    @staticmethod
    def extract_playlist_id_from_url(url: str) -> Optional[str]:
        """
        Extract playlist ID from Spotify URL
        
        Args:
            url: Spotify playlist URL (e.g., https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=...)
            
        Returns:
            Playlist ID or None if URL is invalid
        """
        # Pattern для URL вида: https://open.spotify.com/playlist/{ID} или spotify:playlist:{ID}
        patterns = [
            r'playlist/([a-zA-Z0-9]+)',
            r'spotify:playlist:([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Если не найден паттерн, возможно это уже ID
        if re.match(r'^[a-zA-Z0-9]+$', url.strip()):
            return url.strip()
        
        return None
    
    def download_specific_playlist(self, playlist_id_or_url: str):
        """
        Download a specific playlist by ID or URL
        
        Args:
            playlist_id_or_url: Playlist ID or full Spotify URL
        """
        try:
            # Извлекаем ID из URL, если это URL
            playlist_id = self.extract_playlist_id_from_url(playlist_id_or_url)
            
            if not playlist_id:
                self._log(f"Error: Invalid playlist ID or URL: {playlist_id_or_url}")
                return
            
            self._log(f"Fetching playlist with ID: {playlist_id}")
            playlist = self.sp.playlist(playlist_id, market=None)
            self.download_playlist(playlist)
        except Exception as e:
            self._log(f"Error: {str(e)}")
            self._log(f"Make sure the playlist is public and the ID/URL is correct.")
    
    def download_specific_album(self, album_id: str):
        """Download a specific album by ID"""
        try:
            album = self.sp.album(album_id)
            self.download_album(album)
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download Spotify playlists and albums from hitmotop.com'
    )
    parser.add_argument(
        '--playlists',
        action='store_true',
        help='Download all user playlists'
    )
    parser.add_argument(
        '--albums',
        action='store_true',
        help='Download all user saved albums'
    )
    parser.add_argument(
        '--playlist-id',
        type=str,
        help='Download specific playlist by ID or URL'
    )
    parser.add_argument(
        '--playlist-urls',
        type=str,
        nargs='+',
        help='Download multiple playlists by URLs (space-separated)'
    )
    parser.add_argument(
        '--album-id',
        type=str,
        help='Download specific album by ID'
    )
    
    args = parser.parse_args()
    
    try:
        downloader = SpotifyDownloader()
        
        if args.playlist_urls:
            # Скачиваем несколько плейлистов по URL
            print(f"Downloading {len(args.playlist_urls)} playlists...")
            for idx, url in enumerate(args.playlist_urls, 1):
                print(f"\n{'='*60}")
                print(f"Playlist {idx}/{len(args.playlist_urls)}")
                print(f"{'='*60}")
                downloader.download_specific_playlist(url)
        elif args.playlist_id:
            downloader.download_specific_playlist(args.playlist_id)
        elif args.album_id:
            downloader.download_specific_album(args.album_id)
        elif args.playlists:
            downloader.download_all_playlists()
        elif args.albums:
            downloader.download_all_albums()
        else:
            print("Please specify what to download:")
            print("  --playlists      : Download all playlists")
            print("  --albums         : Download all saved albums")
            print("  --playlist-id    : Download specific playlist (ID or URL)")
            print("  --playlist-urls  : Download multiple playlists (space-separated URLs)")
            print("  --album-id       : Download specific album")
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

