# 🤖 AI Humanity

AI-компаньон с эмоциональным интеллектом и 3D аватаром.

## Установка
```bash
pip install -r requirements.txt
```

## Запуск
```bash
python main.py
```

## Возможности
- PAD модель эмоций
- Система прокачки навыков
- 3D аватар на рабочем столе (VRM/GLB/OBJ)
- Sci-Fi интерфейс

## Структура проекта
```
ai-humaity/
├── core/                    # Ядро AI
│   ├── emotion_engine.py    # PAD модель эмоций
│   ├── cognitive_cycle.py   # Когнитивный цикл
│   ├── skill_system.py      # Система навыков
│   ├── safety_system.py     # Система безопасности
│   └── autonomous_life.py   # Автономная жизнь
├── modules/                  # Модули
│   └── desktop_avatar.py    # 3D аватар
├── gui/                      # Интерфейс
│   ├── main_window_scifi.py # Главное окно
│   ├── styles_scifi.py      # Стили
│   └── skills_widget.py     # Виджет навыков
├── config/                   # Конфигурация
│   └── settings.py          # Настройки API
├── assets/                   # Ресурсы
│   └── avatar_sprites/      # Спрайты аватара
├── main.py                   # Точка входа
├── requirements.txt          # Зависимости
└── README.md
```

## Лицензия
MIT
