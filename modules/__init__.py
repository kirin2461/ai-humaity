from .desktop_avatar import AvatarManager, DesktopAvatar
from .tts_engine import TTSEngine, TTSManager, TTSConfig, TTSStatus
from .telegram_integration import TelegramBot, TelegramManager, TelegramConfig
from .face_emotion import FaceEmotionDetector, FaceEmotionManager, FaceEmotionConfig, EmotionResult
from .calendar_integration import GoogleCalendarAPI, CalendarManager, CalendarConfig, CalendarEvent

__all__ = [
    'AvatarManager', 'DesktopAvatar',
    'TTSEngine', 'TTSManager', 'TTSConfig', 'TTSStatus',
    'TelegramBot', 'TelegramManager', 'TelegramConfig',
    'FaceEmotionDetector', 'FaceEmotionManager', 'FaceEmotionConfig', 'EmotionResult',
    'GoogleCalendarAPI', 'CalendarManager', 'CalendarConfig', 'CalendarEvent',
]
