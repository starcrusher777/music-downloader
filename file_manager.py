#!/usr/bin/env python3
"""
File Manager
Handles file downloads, directory creation, and file organization
"""

import os
import re
import time
import requests
from pathlib import Path
from typing import Optional
from PIL import Image
import io


class FileManager:
    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize file manager with base directory
        
        Args:
            session: Optional requests.Session to use for downloads (for cookies and headers)
        """
        self.base_dir = os.getenv('DOWNLOAD_DIR', 'downloads')
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.session = session if session else requests.Session()
        
        # Create base directory if it doesn't exist
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove invalid characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters for Windows/Linux/Mac
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def create_playlist_directory(self, playlist_name: str) -> str:
        """
        Create directory for a playlist
        
        Args:
            playlist_name: Name of the playlist
            
        Returns:
            Path to created directory
        """
        sanitized_name = self.sanitize_filename(playlist_name)
        playlist_dir = os.path.join(self.base_dir, 'Playlists', sanitized_name)
        Path(playlist_dir).mkdir(parents=True, exist_ok=True)
        return playlist_dir
    
    def create_album_directory(self, artist: str, album_name: str) -> str:
        """
        Create directory for an album
        
        Args:
            artist: Artist name
            album_name: Album name
            
        Returns:
            Path to created directory
        """
        sanitized_artist = self.sanitize_filename(artist)
        sanitized_album = self.sanitize_filename(album_name)
        album_dir = os.path.join(self.base_dir, 'Albums', sanitized_artist, sanitized_album)
        Path(album_dir).mkdir(parents=True, exist_ok=True)
        return album_dir
    
    def download_file(self, url: str, filepath: str) -> bool:
        """
        Download a file from URL
        
        Args:
            url: URL to download from
            filepath: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"  File already exists: {os.path.basename(filepath)}")
            return True
        
        # Улучшенные заголовки для имитации браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://rus.hitmotop.com/',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'Origin': 'https://rus.hitmotop.com',
        }
        
        # Добавляем задержку перед скачиванием
        delay = float(os.getenv('REQUEST_DELAY', 1))
        if delay > 0:
            time.sleep(delay)
        
        for attempt in range(self.max_retries):
            try:
                # Используем сессию для сохранения cookies
                response = self.session.get(url, headers=headers, timeout=30, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Download file
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Show progress for large files
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if downloaded % (1024 * 1024) == 0:  # Every MB
                                    print(f"  Progress: {percent:.1f}%", end='\r')
                
                print()  # New line after progress
                return True
                
            except requests.RequestException as e:
                # Если получили 403, попробуем обновить cookies
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 403:
                    if attempt < self.max_retries - 1:
                        print(f"  Got 403 Forbidden, refreshing cookies (attempt {attempt + 1}/{self.max_retries})...")
                        try:
                            # Обновляем cookies, посещая главную страницу
                            self.session.get('https://rus.hitmotop.com/', timeout=10)
                            time.sleep(1)  # Небольшая задержка
                        except:
                            pass
                        continue
                
                if attempt < self.max_retries - 1:
                    print(f"  Retry {attempt + 1}/{self.max_retries}...")
                    time.sleep(2)  # Задержка перед повтором
                    continue
                else:
                    print(f"  Download failed after {self.max_retries} attempts: {str(e)}")
                    return False
            except Exception as e:
                print(f"  Error downloading file: {str(e)}")
                return False
        
        return False
    
    def download_cover(self, image_url: str, directory: str, filename: str = 'cover.jpg'):
        """
        Download and save cover image
        
        Args:
            image_url: URL of the image
            directory: Directory to save image
            filename: Filename for the image
        """
        filepath = os.path.join(directory, filename)
        
        # Skip if already exists
        if os.path.exists(filepath):
            return
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Open image with PIL to ensure it's valid
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            
            # Save as JPEG
            img.save(filepath, 'JPEG', quality=90)
            print(f"  Cover downloaded: {filename}")
            
        except Exception as e:
            print(f"  Error downloading cover: {str(e)}")

