"""Coqui XTTS v2 - Синтез речи"""
import os
import threading
import queue
import tempfile
import wave
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class TTSStatus(Enum):
    IDLE = "idle"
    LOADING = "loading"
    GENERATING = "generating"
    PLAYING = "playing"
    ERROR = "error"


@dataclass
class TTSConfig:
    """Конфигурация TTS"""
    model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    language: str = "ru"
    speaker_wav: Optional[str] = None  # Путь к образцу голоса для клонирования
    use_gpu: bool = True
    speed: float = 1.0
    temperature: float = 0.7
    output_dir: str = "temp_audio"


class TTSEngine:
    """Движок синтеза речи на базе Coqui XTTS v2"""
    
    def __init__(self, config: TTSConfig = None):
        self.config = config or TTSConfig()
        self.tts = None
        self.status = TTSStatus.IDLE
        self._audio_queue = queue.Queue()
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_playback = False
        self._is_initialized = False
        self._on_status_change: Optional[Callable[[TTSStatus], None]] = None
        
        # Создаём директорию для временных файлов
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def set_status_callback(self, callback: Callable[[TTSStatus], None]):
        """Установить callback для изменения статуса"""
        self._on_status_change = callback
    
    def _update_status(self, status: TTSStatus):
        """Обновить статус и вызвать callback"""
        self.status = status
        if self._on_status_change:
            self._on_status_change(status)
    
    def initialize(self) -> bool:
        """Инициализация модели XTTS v2"""
        if self._is_initialized:
            return True
        
        self._update_status(TTSStatus.LOADING)
        
        try:
            from TTS.api import TTS
            import torch
            
            # Определяем устройство
            device = "cuda" if self.config.use_gpu and torch.cuda.is_available() else "cpu"
            
            print(f"[TTS] Загрузка модели {self.config.model_name}...")
            print(f"[TTS] Устройство: {device}")
            
            # Загружаем модель
            self.tts = TTS(model_name=self.config.model_name).to(device)
            
            self._is_initialized = True
            self._update_status(TTSStatus.IDLE)
            print("[TTS] Модель загружена успешно!")
            return True
            
        except ImportError:
            print("[TTS] ОШИБКА: TTS не установлен. Выполните: pip install TTS")
            self._update_status(TTSStatus.ERROR)
            return False
        except Exception as e:
            print(f"[TTS] ОШИБКА инициализации: {e}")
            self._update_status(TTSStatus.ERROR)
            return False
    
    def synthesize(self, text: str, output_path: str = None) -> Optional[str]:
        """Синтезировать речь из текста"""
        if not self._is_initialized:
            if not self.initialize():
                return None
        
        if not text.strip():
            return None
        
        self._update_status(TTSStatus.GENERATING)
        
        try:
            # Генерируем путь для выходного файла
            if output_path is None:
                output_path = os.path.join(
                    self.config.output_dir,
                    f"speech_{hash(text) & 0xFFFFFFFF}.wav"
                )
            
            # Параметры генерации
            kwargs = {
                "text": text,
                "file_path": output_path,
                "language": self.config.language,
                "speed": self.config.speed,
            }
            
            # Если есть образец голоса для клонирования
            if self.config.speaker_wav and os.path.exists(self.config.speaker_wav):
                kwargs["speaker_wav"] = self.config.speaker_wav
            
            # Генерация
            self.tts.tts_to_file(**kwargs)
            
            self._update_status(TTSStatus.IDLE)
            return output_path
            
        except Exception as e:
            print(f"[TTS] ОШИБКА синтеза: {e}")
            self._update_status(TTSStatus.ERROR)
            return None
    
    def speak(self, text: str, blocking: bool = False):
        """Синтезировать и воспроизвести речь"""
        audio_path = self.synthesize(text)
        if audio_path:
            if blocking:
                self._play_audio_blocking(audio_path)
            else:
                self._audio_queue.put(audio_path)
                self._ensure_playback_thread()
    
    def speak_async(self, text: str, callback: Callable[[bool], None] = None):
        """Асинхронный синтез и воспроизведение"""
        def worker():
            success = False
            audio_path = self.synthesize(text)
            if audio_path:
                self._play_audio_blocking(audio_path)
                success = True
            if callback:
                callback(success)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _ensure_playback_thread(self):
        """Убедиться, что поток воспроизведения запущен"""
        if self._playback_thread is None or not self._playback_thread.is_alive():
            self._stop_playback = False
            self._playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
            self._playback_thread.start()
    
    def _playback_worker(self):
        """Рабочий поток воспроизведения"""
        while not self._stop_playback:
            try:
                audio_path = self._audio_queue.get(timeout=1.0)
                self._play_audio_blocking(audio_path)
            except queue.Empty:
                continue
    
    def _play_audio_blocking(self, audio_path: str):
        """Воспроизвести аудио (блокирующий вызов)"""
        if not os.path.exists(audio_path):
            return
        
        self._update_status(TTSStatus.PLAYING)
        
        try:
            # Пробуем разные методы воспроизведения
            if self._try_pygame(audio_path):
                pass
            elif self._try_playsound(audio_path):
                pass
            elif self._try_system_player(audio_path):
                pass
            else:
                print(f"[TTS] Аудио сохранено: {audio_path}")
        finally:
            self._update_status(TTSStatus.IDLE)
    
    def _try_pygame(self, audio_path: str) -> bool:
        """Воспроизведение через pygame"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            return True
        except:
            return False
    
    def _try_playsound(self, audio_path: str) -> bool:
        """Воспроизведение через playsound"""
        try:
            from playsound import playsound
            playsound(audio_path)
            return True
        except:
            return False
    
    def _try_system_player(self, audio_path: str) -> bool:
        """Воспроизведение через системный плеер"""
        try:
            import platform
            import subprocess
            
            system = platform.system()
            if system == "Windows":
                os.startfile(audio_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_path])
            else:  # Linux
                subprocess.run(["aplay", audio_path])
            return True
        except:
            return False
    
    def stop(self):
        """Остановить воспроизведение"""
        self._stop_playback = True
        try:
            import pygame
            pygame.mixer.music.stop()
        except:
            pass
    
    def set_speaker_voice(self, wav_path: str):
        """Установить образец голоса для клонирования"""
        if os.path.exists(wav_path):
            self.config.speaker_wav = wav_path
            print(f"[TTS] Установлен образец голоса: {wav_path}")
        else:
            print(f"[TTS] Файл не найден: {wav_path}")
    
    def set_language(self, language: str):
        """Установить язык синтеза"""
        supported = ["ru", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "nl", "cs", "ar", "zh-cn", "ja", "ko"]
        if language in supported:
            self.config.language = language
            print(f"[TTS] Язык: {language}")
        else:
            print(f"[TTS] Неподдерживаемый язык: {language}. Доступны: {supported}")
    
    def set_speed(self, speed: float):
        """Установить скорость речи (0.5 - 2.0)"""
        self.config.speed = max(0.5, min(2.0, speed))
    
    def cleanup(self):
        """Очистка временных файлов"""
        try:
            import shutil
            if os.path.exists(self.config.output_dir):
                shutil.rmtree(self.config.output_dir)
                os.makedirs(self.config.output_dir, exist_ok=True)
        except Exception as e:
            print(f"[TTS] Ошибка очистки: {e}")


class TTSManager:
    """Менеджер TTS для интеграции с AI Humanity"""
    
    def __init__(self, cognitive_cycle=None):
        self.cognitive = cognitive_cycle
        self.engine: Optional[TTSEngine] = None
        self.enabled = False
    
    def initialize(self, config: TTSConfig = None) -> bool:
        """Инициализация TTS"""
        self.engine = TTSEngine(config)
        success = self.engine.initialize()
        self.enabled = success
        return success
    
    def on_response(self, response: str):
        """Озвучить ответ AI"""
        if self.enabled and self.engine:
            # Очищаем текст от эмодзи и спецсимволов для лучшего синтеза
            clean_text = self._clean_text(response)
            if clean_text:
                self.engine.speak_async(clean_text)
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста для синтеза"""
        import re
        # Убираем эмодзи
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def toggle(self) -> bool:
        """Включить/выключить TTS"""
        if self.engine is None:
            self.initialize()
        self.enabled = not self.enabled
        return self.enabled
    
    def stop(self):
        """Остановить воспроизведение"""
        if self.engine:
            self.engine.stop()
