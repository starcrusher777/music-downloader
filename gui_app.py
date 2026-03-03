#!/usr/bin/env python3
"""
Spotify Music Downloader - GUI Application
Красивое Windows приложение для скачивания музыки из Spotify
"""

import os
import sys
import threading
import queue
from typing import Optional
import customtkinter as ctk
from tkinter import messagebox, filedialog
from dotenv import load_dotenv, set_key, find_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_downloader import SpotifyDownloader

# Загружаем переменные окружения
load_dotenv()

# Настройка темы CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LogHandler:
    """Класс для обработки логов в GUI"""
    def __init__(self, log_queue: queue.Queue, log_textbox: ctk.CTkTextbox):
        self.log_queue = log_queue
        self.log_textbox = log_textbox
        self.process_queue()
    
    def process_queue(self):
        """Обработка очереди логов"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_textbox.insert("end", message + "\n")
                self.log_textbox.see("end")
        except queue.Empty:
            pass
        finally:
            # Планируем следующую проверку
            self.log_textbox.after(100, self.process_queue)


class SpotifyDownloaderGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Spotify Music Downloader")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Переменные
        self.downloader: Optional[SpotifyDownloader] = None
        self.is_downloading = False
        self.log_queue = queue.Queue()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Проверяем настройки при запуске
        self.check_settings()
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        
        # Заголовок
        title_label = ctk.CTkLabel(
            self.root,
            text="🎵 Spotify Music Downloader",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            self.root,
            text="Скачивайте плейлисты и альбомы из Spotify",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Основной контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Вкладки
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка: Скачивание
        self.download_tab = self.tabview.add("📥 Скачивание")
        self.create_download_tab()
        
        # Вкладка: Настройки
        self.settings_tab = self.tabview.add("⚙️ Настройки")
        self.create_settings_tab()
        
        # Вкладка: Логи
        self.logs_tab = self.tabview.add("📋 Логи")
        self.create_logs_tab()
    
    def create_download_tab(self):
        """Создание вкладки скачивания"""
        
        # Инструкция
        info_label = ctk.CTkLabel(
            self.download_tab,
            text="Вставьте URL плейлиста или альбома Spotify:",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10), padx=20)
        
        # Поле ввода URL
        self.url_entry = ctk.CTkEntry(
            self.download_tab,
            placeholder_text="https://open.spotify.com/playlist/...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(fill="x", padx=20, pady=10)
        
        # Кнопка добавления URL
        add_button = ctk.CTkButton(
            self.download_tab,
            text="➕ Добавить URL",
            command=self.add_url_to_list,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        add_button.pack(pady=5, padx=20)
        
        # Список URL
        list_label = ctk.CTkLabel(
            self.download_tab,
            text="Список для скачивания:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        list_label.pack(pady=(20, 5), padx=20)
        
        # Фрейм для списка и кнопок
        list_frame = ctk.CTkFrame(self.download_tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Список URL с прокруткой
        self.url_listbox = ctk.CTkTextbox(
            list_frame,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.url_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Кнопки управления списком
        list_buttons_frame = ctk.CTkFrame(list_frame)
        list_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        clear_button = ctk.CTkButton(
            list_buttons_frame,
            text="🗑️ Очистить",
            command=self.clear_url_list,
            width=120,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        clear_button.pack(side="left", padx=5)
        
        remove_button = ctk.CTkButton(
            list_buttons_frame,
            text="➖ Удалить выбранное",
            command=self.remove_selected_url,
            width=150,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        remove_button.pack(side="left", padx=5)
        
        # Прогресс-бар
        self.progress_label = ctk.CTkLabel(
            self.download_tab,
            text="Готов к работе",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=(10, 5), padx=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.download_tab)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_bar.set(0)
        
        # Кнопка скачивания
        self.download_button = ctk.CTkButton(
            self.download_tab,
            text="🚀 Начать скачивание",
            command=self.start_download,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#3B82F6", "#2563EB"),
            hover_color=("#2563EB", "#1D4ED8")
        )
        self.download_button.pack(pady=20, padx=20)
        
        # Статистика
        stats_frame = ctk.CTkFrame(self.download_tab)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Скачано: 0 | Ошибок: 0",
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack(pady=10)
    
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        
        settings_label = ctk.CTkLabel(
            self.settings_tab,
            text="Настройки Spotify API",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_label.pack(pady=(20, 10), padx=20)
        
        info_text = ctk.CTkLabel(
            self.settings_tab,
            text="Получите ключи на https://developer.spotify.com/dashboard",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_text.pack(pady=(0, 20), padx=20)
        
        # Client ID
        client_id_label = ctk.CTkLabel(
            self.settings_tab,
            text="Client ID:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        client_id_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.client_id_entry = ctk.CTkEntry(
            self.settings_tab,
            placeholder_text="Введите Client ID",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.client_id_entry.pack(fill="x", padx=20, pady=5)
        self.client_id_entry.insert(0, os.getenv('SPOTIPY_CLIENT_ID', ''))
        
        # Client Secret
        client_secret_label = ctk.CTkLabel(
            self.settings_tab,
            text="Client Secret:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        client_secret_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.client_secret_entry = ctk.CTkEntry(
            self.settings_tab,
            placeholder_text="Введите Client Secret",
            height=35,
            font=ctk.CTkFont(size=12),
            show="*"
        )
        self.client_secret_entry.pack(fill="x", padx=20, pady=5)
        self.client_secret_entry.insert(0, os.getenv('SPOTIPY_CLIENT_SECRET', ''))
        
        # Username
        username_label = ctk.CTkLabel(
            self.settings_tab,
            text="Spotify Username:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        username_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            self.settings_tab,
            placeholder_text="Введите ваш Spotify username",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.username_entry.pack(fill="x", padx=20, pady=5)
        self.username_entry.insert(0, os.getenv('SPOTIFY_USERNAME', ''))
        
        # Папка для скачивания
        download_dir_label = ctk.CTkLabel(
            self.settings_tab,
            text="Папка для скачивания:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        download_dir_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        dir_frame = ctk.CTkFrame(self.settings_tab)
        dir_frame.pack(fill="x", padx=20, pady=5)
        
        self.download_dir_entry = ctk.CTkEntry(
            dir_frame,
            placeholder_text="Выберите папку",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.download_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.download_dir_entry.insert(0, os.getenv('DOWNLOAD_DIR', 'downloads'))
        
        browse_button = ctk.CTkButton(
            dir_frame,
            text="📁 Обзор",
            command=self.browse_folder,
            width=100,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        browse_button.pack(side="right")
        
        # Задержка между запросами
        delay_label = ctk.CTkLabel(
            self.settings_tab,
            text="Задержка между запросами (секунды):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        delay_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.delay_entry = ctk.CTkEntry(
            self.settings_tab,
            placeholder_text="1",
            height=35,
            width=100,
            font=ctk.CTkFont(size=12)
        )
        self.delay_entry.pack(anchor="w", padx=20, pady=5)
        self.delay_entry.insert(0, os.getenv('REQUEST_DELAY', '1'))
        
        # Кнопка сохранения
        save_button = ctk.CTkButton(
            self.settings_tab,
            text="💾 Сохранить настройки",
            command=self.save_settings,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#10B981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        save_button.pack(pady=20, padx=20)
    
    def create_logs_tab(self):
        """Создание вкладки логов"""
        
        logs_label = ctk.CTkLabel(
            self.logs_tab,
            text="Журнал операций",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        logs_label.pack(pady=(20, 10), padx=20)
        
        # Текстовое поле для логов
        self.log_textbox = ctk.CTkTextbox(
            self.logs_tab,
            font=ctk.CTkFont(size=11, family="Courier"),
            wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Кнопка очистки логов
        clear_logs_button = ctk.CTkButton(
            self.logs_tab,
            text="🗑️ Очистить логи",
            command=self.clear_logs,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        clear_logs_button.pack(pady=10, padx=20)
        
        # Инициализируем обработчик логов
        self.log_handler = LogHandler(self.log_queue, self.log_textbox)
    
    def log(self, message: str):
        """Добавление сообщения в лог"""
        self.log_queue.put(message)
    
    def clear_logs(self):
        """Очистка логов"""
        self.log_textbox.delete("1.0", "end")
        self.log("Логи очищены")
    
    def add_url_to_list(self):
        """Добавление URL в список"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL плейлиста или альбома")
            return
        
        # Проверяем, что это валидный URL Spotify
        if "spotify.com" not in url and "spotify:" not in url:
            messagebox.showerror("Ошибка", "Это не похоже на URL Spotify")
            return
        
        # Добавляем в список
        current_text = self.url_listbox.get("1.0", "end-1c")
        if current_text:
            self.url_listbox.insert("end", "\n" + url)
        else:
            self.url_listbox.insert("end", url)
        
        self.url_entry.delete(0, "end")
        self.log(f"Добавлен URL: {url[:50]}...")
    
    def clear_url_list(self):
        """Очистка списка URL"""
        self.url_listbox.delete("1.0", "end")
        self.log("Список URL очищен")
    
    def remove_selected_url(self):
        """Удаление выбранного URL"""
        try:
            # Получаем выделенный текст
            selected = self.url_listbox.selection_get()
            if selected:
                # Удаляем выделенный текст
                start = self.url_listbox.index("sel.first")
                end = self.url_listbox.index("sel.last")
                self.url_listbox.delete(start, end)
                self.log(f"Удален URL: {selected[:50]}...")
        except:
            messagebox.showinfo("Информация", "Выделите URL для удаления")
    
    def browse_folder(self):
        """Выбор папки для скачивания"""
        folder = filedialog.askdirectory()
        if folder:
            self.download_dir_entry.delete(0, "end")
            self.download_dir_entry.insert(0, folder)
    
    def check_settings(self):
        """Проверка настроек при запуске"""
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        username = os.getenv('SPOTIFY_USERNAME')
        
        if not all([client_id, client_secret, username]):
            self.log("⚠️ Настройки не заполнены. Перейдите во вкладку 'Настройки'")
            self.tabview.set("⚙️ Настройки")
    
    def save_settings(self):
        """Сохранение настроек в .env файл"""
        try:
            env_file = find_dotenv()
            if not env_file:
                env_file = os.path.join(os.getcwd(), '.env')
            
            client_id = self.client_id_entry.get().strip()
            client_secret = self.client_secret_entry.get().strip()
            username = self.username_entry.get().strip()
            download_dir = self.download_dir_entry.get().strip()
            delay = self.delay_entry.get().strip()
            
            if not all([client_id, client_secret, username]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
                return
            
            # Сохраняем настройки
            set_key(env_file, 'SPOTIPY_CLIENT_ID', client_id)
            set_key(env_file, 'SPOTIPY_CLIENT_SECRET', client_secret)
            set_key(env_file, 'SPOTIFY_USERNAME', username)
            set_key(env_file, 'DOWNLOAD_DIR', download_dir or 'downloads')
            set_key(env_file, 'REQUEST_DELAY', delay or '1')
            
            # Перезагружаем переменные окружения
            load_dotenv(override=True)
            
            messagebox.showinfo("Успех", "Настройки сохранены!")
            self.log("✅ Настройки успешно сохранены")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
            self.log(f"❌ Ошибка сохранения настроек: {str(e)}")
    
    def get_url_list(self):
        """Получение списка URL из текстового поля"""
        text = self.url_listbox.get("1.0", "end-1c").strip()
        if not text:
            return []
        
        urls = [url.strip() for url in text.split("\n") if url.strip()]
        return urls
    
    def start_download(self):
        """Запуск скачивания в отдельном потоке"""
        if self.is_downloading:
            messagebox.showinfo("Информация", "Скачивание уже выполняется")
            return
        
        urls = self.get_url_list()
        if not urls:
            messagebox.showwarning("Предупреждение", "Добавьте хотя бы один URL")
            return
        
        # Проверяем настройки
        if not all([os.getenv('SPOTIPY_CLIENT_ID'), os.getenv('SPOTIPY_CLIENT_SECRET'), os.getenv('SPOTIFY_USERNAME')]):
            messagebox.showerror("Ошибка", "Заполните настройки перед скачиванием!")
            self.tabview.set("⚙️ Настройки")
            return
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.download_thread, args=(urls,), daemon=True)
        thread.start()
    
    def download_thread(self, urls: list):
        """Поток для скачивания"""
        self.is_downloading = True
        self.download_button.configure(state="disabled", text="⏳ Скачивание...")
        
        try:
            self.log(f"🚀 Начало скачивания {len(urls)} плейлиста(ов)...")
            
            # Инициализируем downloader с callback для логов
            self.downloader = SpotifyDownloader(log_callback=self.log)
            
            total_downloaded = 0
            total_failed = 0
            
            for idx, url in enumerate(urls, 1):
                self.log(f"\n{'='*60}")
                self.log(f"Плейлист {idx}/{len(urls)}: {url[:50]}...")
                self.log(f"{'='*60}")
                
                self.progress_label.configure(text=f"Обработка плейлиста {idx}/{len(urls)}...")
                self.progress_bar.set(idx / len(urls))
                
                try:
                    # Скачиваем плейлист
                    self.downloader.download_specific_playlist(url)
                    total_downloaded += 1
                    self.log(f"✅ Плейлист {idx} успешно скачан")
                except Exception as e:
                    total_failed += 1
                    self.log(f"❌ Ошибка при скачивании плейлиста {idx}: {str(e)}")
            
            # Итоги
            self.log(f"\n{'='*60}")
            self.log(f"🎉 Скачивание завершено!")
            self.log(f"Успешно: {total_downloaded} | Ошибок: {total_failed}")
            self.log(f"{'='*60}")
            
            self.progress_label.configure(text=f"Завершено! Успешно: {total_downloaded} | Ошибок: {total_failed}")
            self.progress_bar.set(1.0)
            self.stats_label.configure(text=f"Скачано: {total_downloaded} | Ошибок: {total_failed}")
            
            messagebox.showinfo("Завершено", f"Скачивание завершено!\nУспешно: {total_downloaded}\nОшибок: {total_failed}")
            
        except Exception as e:
            error_msg = f"Критическая ошибка: {str(e)}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
        finally:
            self.is_downloading = False
            self.download_button.configure(state="normal", text="🚀 Начать скачивание")
            self.progress_bar.set(0)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    """Главная функция"""
    app = SpotifyDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()
