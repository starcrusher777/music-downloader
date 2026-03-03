
### Запуск GUI приложения:

```bash
python gui_app.py
```

или на Windows:
```bash
run_gui.bat
```

Подробная инструкция по использованию GUI приложения: [GUI_README.md](GUI_README.md)

---

## 📝 Консольная версия

## Возможности

- ✅ Получение всех плейлистов из вашего профиля Spotify
- ✅ Получение всех сохраненных альбомов из вашего профиля Spotify
- ✅ Скачивание плейлистов других пользователей (публичные плейлисты)
- ✅ Поддержка работы с плейлистами по URL или ID
- ✅ Скачивание нескольких плейлистов за раз
- ✅ Автоматический поиск треков на hitmotop.com
- ✅ Скачивание треков в формате MP3
- ✅ Организация файлов по папкам (Playlists/Albums)
- ✅ Скачивание обложек плейлистов и альбомов
- ✅ Корректное переименование файлов
- ✅ Поддержка скачивания конкретных плейлистов/альбомов по ID

## Требования

- Python 3.7 или выше
- Аккаунт Spotify
- Spotify Developer App (для получения API ключей)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd "music downloader"
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка Spotify API

1. Перейдите на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Войдите в свой аккаунт Spotify
3. Нажмите "Create App"
4. Заполните форму:
   - **App name**: любое имя (например, "Music Downloader")
   - **App description**: описание приложения
   - **Redirect URI**: `http://localhost:8888/callback`
   - Отметьте чекбокс "I understand and agree to Spotify's Developer Terms of Service"
5. Нажмите "Save"
6. Скопируйте **Client ID** и **Client Secret**

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Spotify API credentials
SPOTIPY_CLIENT_ID=ваш_client_id
SPOTIPY_CLIENT_SECRET=ваш_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

# Spotify username (ваш username из профиля)
SPOTIFY_USERNAME=ваш_username

# Настройки скачивания
DOWNLOAD_DIR=downloads
MAX_RETRIES=3
REQUEST_DELAY=1
```

**Как найти свой Spotify username:**
1. Откройте Spotify в браузере
2. Перейдите в свой профиль
3. Скопируйте username из URL (например, если URL `https://open.spotify.com/user/username123`, то username = `username123`)

## Использование

### Скачать все плейлисты

```bash
python3 spotify_downloader.py --playlists
```

Это скачает все плейлисты из вашего профиля Spotify. Каждый плейлист будет сохранен в отдельную папку с обложкой.

### Скачать все сохраненные альбомы

```bash
python3 spotify_downloader.py --albums
```

Это скачает все сохраненные альбомы из вашего профиля Spotify. Альбомы будут организованы по папкам: `Albums/Artist Name/Album Name/`

### Скачать конкретный плейлист по ID или URL

```bash
# По ID
python3 spotify_downloader.py --playlist-id 37i9dQZF1DXcBWIGoYBM5M

# По полной ссылке (работает с плейлистами других пользователей)
# ВАЖНО: Всегда используйте кавычки вокруг URL!
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ"
```

**Как найти ID плейлиста или URL:**
1. Откройте плейлист в Spotify (веб-версия или приложение)
2. Нажмите "..." (три точки) → "Share" → "Copy link to playlist"
3. Используйте либо полную ссылку, либо только ID из ссылки

**Важно:** Плейлист должен быть публичным, чтобы его можно было скачать через ваш профиль.

### Скачать несколько плейлистов по URL

```bash
python3 spotify_downloader.py --playlist-urls \
  "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ" \
  "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"
```

**Важно:** Всегда используйте кавычки вокруг каждого URL, чтобы shell не интерпретировал специальные символы (например, `?`).

Это скачает несколько плейлистов подряд. Работает с плейлистами других пользователей, если они публичные.

### Скачать конкретный альбом по ID

```bash
python3 spotify_downloader.py --album-id 4uLU6hMCjMI75M1A2tKUQC
```

**Как найти ID альбома:**
1. Откройте альбом в Spotify (веб-версия или приложение)
2. Нажмите "..." (три точки) → "Share" → "Copy link to album"
3. Из ссылки `https://open.spotify.com/album/4uLU6hMCjMI75M1A2tKUQC` скопируйте ID: `4uLU6hMCjMI75M1A2tKUQC`

### Примеры использования

```bash
# Скачать все плейлисты
python3 spotify_downloader.py --playlists

# Скачать все альбомы
python3 spotify_downloader.py --albums

# Скачать конкретный плейлист по ID
python3 spotify_downloader.py --playlist-id 37i9dQZF1DXcBWIGoYBM5M

# Скачать конкретный плейлист по URL (работает с плейлистами других пользователей)
# ВАЖНО: Используйте кавычки вокруг URL!
python3 spotify_downloader.py --playlist-id "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ"

# Скачать несколько плейлистов по URL
python3 spotify_downloader.py --playlist-urls \
  "https://open.spotify.com/playlist/4DmELrQMOuWomBtcauF4g0?si=JiKpLwpxQ6KogeZ9fOFhoQ" \
  "https://open.spotify.com/playlist/2XgT2Ci5DLfnxjfZlK7Ulw?si=pLrRL06JSeuEB6v4wFSY6A"

# Скачать конкретный альбом
python3 spotify_downloader.py --album-id 4uLU6hMCjMI75M1A2tKUQC
```

## Первый запуск

При первом запуске скрипт откроет браузер для авторизации в Spotify:

1. Войдите в свой аккаунт Spotify
2. Разрешите доступ приложению
3. После авторизации вы будете перенаправлены на `http://localhost:8888/callback`
4. Скопируйте полный URL из адресной строки
5. Вставьте URL в консоль, когда скрипт попросит

После этого токен будет сохранен и повторная авторизация не потребуется.

## Настройки

### Переменные окружения

- `SPOTIPY_CLIENT_ID` - Client ID из Spotify Developer Dashboard (обязательно)
- `SPOTIPY_CLIENT_SECRET` - Client Secret из Spotify Developer Dashboard (обязательно)
- `SPOTIFY_USERNAME` - Ваш Spotify username (обязательно)
- `SPOTIPY_REDIRECT_URI` - URI для редиректа (по умолчанию: `http://localhost:8888/callback`)
- `DOWNLOAD_DIR` - Папка для скачивания (по умолчанию: `downloads`)
- `MAX_RETRIES` - Количество попыток при ошибке скачивания (по умолчанию: 3)
- `REQUEST_DELAY` - Задержка между запросами в секундах (по умолчанию: 1)