# Music Downloader

Spotify playlist and album downloader with GUI and console versions.

---

## 🖥️ GUI Application

### Launching the GUI application

```bash
python gui_app.py
```

or on Windows:
```bash
run_gui.bat
```

Detailed GUI usage instructions: [GUI_README.md](GUI_README.md)

---

## 📝 Console Version

## Features

- ✅ Get all playlists from your Spotify profile
- ✅ Get all saved albums from your Spotify profile
- ✅ Download other users' playlists (public playlists)
- ✅ Support for playlists by URL or ID
- ✅ Download multiple playlists at once
- ✅ Automatic track search on hitmotop.com
- ✅ Download tracks in MP3 format
- ✅ Organize files into folders (Playlists/Albums)
- ✅ Download playlist and album covers
- ✅ Proper file renaming
- ✅ Support for downloading specific playlists/albums by ID

## Requirements

- Python 3.7 or higher
- Spotify account
- Spotify Developer App (to obtain API keys)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd "music downloader"
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the form:
   - **App name**: any name (e.g. "Music Downloader")
   - **App description**: application description
   - **Redirect URI**: `http://localhost:8888/callback`
   - Check the box "I understand and agree to Spotify's Developer Terms of Service"
5. Click "Save"
6. Copy **Client ID** and **Client Secret**

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Spotify API credentials
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

# Spotify username (your username from profile)
SPOTIFY_USERNAME=your_username

# Download settings
DOWNLOAD_DIR=downloads
MAX_RETRIES=3
REQUEST_DELAY=1
```

**How to find your Spotify username:**
1. Open Spotify in your browser
2. Go to your profile
3. Copy the username from the URL (e.g. if the URL is `https://open.spotify.com/user/username123`, then username = `username123`)

## Usage

### Download all playlists

```bash
python3 spotify_downloader.py --playlists
```

This will download all playlists from your Spotify profile. Each playlist will be saved in a separate folder with its cover.

### Download all saved albums

```bash
python3 spotify_downloader.py --albums
```

This will download all saved albums from your Spotify profile. Albums will be organized in folders: `Albums/Artist Name/Album Name/`

### Download a specific playlist by ID or URL

```bash
# By ID
python3 spotify_downloader.py --playlist-id 37i9dQZF1DXcBWIGoYBM5M

# By full link (works with other users' playlists)
# IMPORTANT: Always use quotes around the URL!
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ"
```

**How to find playlist ID or URL:**
1. Open the playlist in Spotify (web or app)
2. Click "..." (three dots) → "Share" → "Copy link to playlist"
3. Use either the full link or just the ID from the link

**Note:** The playlist must be public to be downloadable via your profile.

### Download multiple playlists by URL

```bash
python3 spotify_downloader.py --playlist-urls \
  "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ" \
  "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"
```

**Note:** Always use quotes around each URL so the shell does not interpret special characters (e.g. `?`).

This will download multiple playlists in sequence. Works with other users' playlists if they are public.

### Download a specific album by ID

```bash
python3 spotify_downloader.py --album-id 4uLU6hMCjMI75M1A2tKUQC
```

**How to find album ID:**
1. Open the album in Spotify (web or app)
2. Click "..." (three dots) → "Share" → "Copy link to album"
3. From the link `https://open.spotify.com/album/4uLU6hMCjMI75M1A2tKUQC` copy the ID: `4uLU6hMCjMI75M1A2tKUQC`

### Usage examples

```bash
# Download all playlists
python3 spotify_downloader.py --playlists

# Download all albums
python3 spotify_downloader.py --albums

# Download a specific playlist by ID
python3 spotify_downloader.py --playlist-id 37i9dQZF1DXcBWIGoYBM5M

# Download a specific playlist by URL (works with other users' playlists)
# IMPORTANT: Use quotes around the URL!
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ"

# Download multiple playlists by URL
python3 spotify_downloader.py --playlist-urls \
  "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ" \
  "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"

# Download a specific album
python3 spotify_downloader.py --album-id 4uLU6hMCjMI75M1A2tKUQC
```

## First run

On first run, the script will open a browser for Spotify authorization:

1. Log in to your Spotify account
2. Grant the application access
3. After authorization you will be redirected to `http://localhost:8888/callback`
4. Copy the full URL from the address bar
5. Paste the URL into the console when the script prompts you

After that, the token will be saved and you will not need to authorize again.

## Configuration

### Environment variables

- `SPOTIPY_CLIENT_ID` - Client ID from Spotify Developer Dashboard (required)
- `SPOTIPY_CLIENT_SECRET` - Client Secret from Spotify Developer Dashboard (required)
- `SPOTIFY_USERNAME` - Your Spotify username (required)
- `SPOTIPY_REDIRECT_URI` - Redirect URI (default: `http://localhost:8888/callback`)
- `DOWNLOAD_DIR` - Download folder (default: `downloads`)
- `MAX_RETRIES` - Number of retries on download error (default: 3)
- `REQUEST_DELAY` - Delay between requests in seconds (default: 1)
