# 🤖 Unified Telegram Bot

Один бот для всего: отправка сообщений + пересылка входящих.

## ⚡ Быстрый старт

### 1. Установи зависимости:
```bash
pip install -r requirements.txt
```

### 2. Создай конфиг:
```bash
copy config_example.json config.json
notepad config.json
```

### 3. Заполни API данные:

Получи на https://my.telegram.org → API development tools

```json
{
  "api_id": 12345678,
  "api_hash": "твой_хеш",
  "phone_number": "+79991234567"
}
```

### 4. Первый запуск (авторизация):
```bash
python bot.py
```
Введи код из Telegram. Создастся файл `session.session`.

### 5. Настрой режимы работы:

#### Только отправка сообщений:
```json
{
  "send_enabled": true,
  "target_chat": "@username",
  "message_file": "message.txt",
  "interval_seconds": 3600,
  
  "forward_enabled": false
}
```

#### Только пересылка входящих:
```json
{
  "send_enabled": false,
  
  "forward_enabled": true,
  "forward_to": "me"
}
```

#### Оба режима одновременно:
```json
{
  "send_enabled": true,
  "target_chat": "@username",
  "message_file": "message.txt",
  "interval_seconds": 3600,
  
  "forward_enabled": true,
  "forward_to": "me"
}
```

### 6. Запуск:
```bash
python unified_bot.py --config config.json
```

## 🎯 Режимы работы

### 📤 Отправка сообщений
- Автоматически отправляет сообщения в указанный чат
- Интервал настраивается (в секундах)
- Текст из файла `message.txt`

### 📬 Пересылка входящих
- Все входящие сообщения пересылаются в "Избранное"
- **НЕ ПОМЕЧАЕТ как прочитанное!**
- Показывает от кого и из какого чата

## 🖥️ Запуск на сервере

### Windows:
```cmd
pythonw unified_bot.py --config config.json
```

### Linux (фон):
```bash
nohup python3 unified_bot.py --config config.json > bot.log 2>&1 &
```

### Linux (systemd):
```bash
chmod +x install_service.sh
./install_service.sh
sudo systemctl start telegram_bot
```

## 📝 Структура файлов

```
telegram_bot/
├── unified_bot.py          # Основной бот
├── bot.py                  # Для первой авторизации
├── config.json             # Твоя конфигурация
├── message.txt             # Текст для отправки
├── session.session         # Файл сессии (создается автоматически)
└── requirements.txt        # Зависимости
```

## ⚙️ Настройки конфига

| Параметр | Описание | Пример |
|----------|----------|---------|
| `api_id` | API ID | `12345678` |
| `api_hash` | API Hash | `"abc123"` |
| `phone_number` | Номер телефона | `"+79991234567"` |
| `session_name` | Имя файла сессии | `"session"` |
| `send_enabled` | Включить отправку | `true` / `false` |
| `target_chat` | Куда отправлять | `"@username"` или `"-100123"` |
| `message_file` | Файл с текстом | `"message.txt"` |
| `interval_seconds` | Интервал (секунды) | `3600` = 1 час |
| `forward_enabled` | Включить пересылку | `true` / `false` |
| `forward_to` | Куда пересылать | `"me"` = Избранное |

## ❓ FAQ

**Q: Как узнать ID чата?**  
A: Используй @getidsbot или @userinfobot

**Q: Как остановить бота?**  
A: Ctrl+C или `pkill -f unified_bot`

**Q: Входящие помечаются как прочитанные?**  
A: НЕТ! Бот просто пересылает, не читая.

**Q: Можно ли отправлять в несколько чатов?**  
A: Создай несколько config файлов и запусти несколько ботов.

**Q: Сколько ресурсов потребляет?**  
A: ~50 MB RAM, минимум CPU.

## 🚀 Готово!

Один бот - все функции! 🎉



