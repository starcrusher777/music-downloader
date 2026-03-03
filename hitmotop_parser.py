#!/usr/bin/env python3
"""
Hitmotop.com Parser
Searches for tracks and extracts download URLs from hitmotop.com
"""

import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Optional
import os


class HitmotopParser:
    def __init__(self):
        """Initialize parser with session and headers"""
        self.base_url = "https://rus.hitmotop.com"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        self.delay = float(os.getenv('REQUEST_DELAY', 1))
        
        # Посещаем главную страницу для получения cookies
        try:
            self.session.get(self.base_url, timeout=10)
        except:
            pass  # Игнорируем ошибки при инициализации
    
    def search_tracks(self, query: str) -> list:
        """
        Search for tracks on hitmotop.com
        
        Args:
            query: Search query (artist + track name)
            
        Returns:
            List of track elements from search results
        """
        # Encode query for URL
        encoded_query = urllib.parse.quote(query)
        search_url = f"{self.search_url}?q={encoded_query}"
        
        try:
            print(f"  Searching: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # First, try to find download buttons directly (most reliable)
            download_buttons = soup.select('a.track__download-btn')
            if download_buttons:
                # Return parent elements or the buttons themselves
                tracks = []
                for btn in download_buttons:
                    # Try to get parent container, or use the button itself
                    parent = btn.find_parent(['div', 'li', 'article', 'section'])
                    tracks.append(parent if parent else btn)
                
                if tracks:
                    time.sleep(self.delay)
                    return tracks
            
            # If no download buttons found, try finding track containers
            tracks = []
            selectors = [
                '.track',
                '.track-item',
                '.search-result',
                '[class*="track"]',
                'div[class*="track"]',
                'li[class*="track"]',
            ]
            
            for selector in selectors:
                tracks = soup.select(selector)
                if tracks:
                    break
            
            # Add delay between requests
            time.sleep(self.delay)
            
            return tracks
            
        except requests.RequestException as e:
            print(f"  Error searching: {str(e)}")
            return []
    
    def get_download_url(self, track_element) -> Optional[str]:
        """
        Extract download URL from track element
        
        Args:
            track_element: BeautifulSoup element containing track info
            
        Returns:
            Download URL or None
        """
        try:
            # If the element itself is a download button
            if track_element.name == 'a' and 'track__download-btn' in track_element.get('class', []):
                href = track_element.get('href')
                if href:
                    return self._normalize_url(href)
            
            # Look for download button with class 'track__download-btn'
            download_btn = track_element.find('a', class_='track__download-btn')
            
            if download_btn and download_btn.get('href'):
                download_url = download_btn['href']
                return self._normalize_url(download_url)
            
            # Alternative: look for any link with 'get/music' in href
            links = track_element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'get/music' in href:
                    return self._normalize_url(href)
            
            return None
            
        except Exception as e:
            print(f"  Error extracting download URL: {str(e)}")
            return None
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL to full URL format
        
        Args:
            url: URL to normalize
            
        Returns:
            Full URL
        """
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.base_url}{url}"
        else:
            return f"{self.base_url}/{url}"
    
    def search_and_get_download_url(self, query: str) -> Optional[str]:
        """
        Search for a track and return its download URL
        
        Args:
            query: Search query (artist + track name)
            
        Returns:
            Download URL or None if not found
        """
        tracks = self.search_tracks(query)
        
        if not tracks:
            return None
        
        # Try to get download URL from first result
        # You might want to add more sophisticated matching here
        for track in tracks:
            download_url = self.get_download_url(track)
            if download_url:
                return download_url
        
        return None
    
    def get_track_info(self, track_element) -> dict:
        """
        Extract track information from element
        
        Args:
            track_element: BeautifulSoup element containing track info
            
        Returns:
            Dictionary with track information
        """
        info = {
            'title': None,
            'artist': None,
            'download_url': None
        }
        
        try:
            # Try to extract title and artist
            title_elem = track_element.find(class_='track__title') or track_element.find('h3') or track_element.find('h4')
            if title_elem:
                info['title'] = title_elem.get_text(strip=True)
            
            artist_elem = track_element.find(class_='track__artist') or track_element.find(class_='artist')
            if artist_elem:
                info['artist'] = artist_elem.get_text(strip=True)
            
            # Get download URL
            info['download_url'] = self.get_download_url(track_element)
            
        except Exception as e:
            print(f"  Error extracting track info: {str(e)}")
        
        return info

