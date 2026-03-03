#!/bin/bash
# Примеры использования скрипта для скачивания плейлистов
# ВАЖНО: Всегда используйте кавычки вокруг URL, чтобы shell не интерпретировал специальные символы

# Скачать один плейлист по URL (ОБЯЗАТЕЛЬНО в кавычках!)
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ"

# Скачать другой плейлист по URL
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"

# Скачать оба плейлиста за раз
python3 spotify_downloader.py --playlist-urls \
  "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ" \
  "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"
