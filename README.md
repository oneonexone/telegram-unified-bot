# 🤖 Telegram Unified Bot

Universal Telegram bot for automated messaging and message forwarding.

## ✨ Features

- 📤 **Auto-messaging** - Send messages to chats/channels on schedule
- 📬 **Message forwarding** - Forward incoming DMs to another account (without marking as read!)
- 🔄 **Message rotation** - Rotate between multiple messages
- ⚡ **FloodWait protection** - Automatic interval adjustment
- 🎯 **DM-only mode** - Forward only private messages, ignore groups
- 🌈 **Cross-platform** - Works on Windows, Linux, macOS

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. Create `config.json` from example:
```bash
cp config_example.json config.json
```

2. Get API credentials from https://my.telegram.org

3. Fill in `config.json`:
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash",
  "phone_number": "+1234567890",
  
  "send_enabled": true,
  "target_chat": "@username",
  "message_file": "messages",
  "rotation_mode": "sequential",
  "interval_seconds": 3600,
  
  "forward_enabled": true,
  "forward_to": "@your_second_account"
}
```

### First Run (Authorization)

```bash
python bot.py
```

Enter the code from Telegram. This creates `session.session` file.

### Run the Bot

```bash
python unified_bot.py --config config.json
```

## 📁 Project Structure

```
telegram_bot/
├── unified_bot.py          # Main bot
├── bot.py                  # Interactive mode (for first auth)
├── config.json             # Your configuration
├── config_example.json     # Configuration example
├── messages/               # Folder with messages for rotation
│   ├── message1.txt
│   ├── message2.txt
│   └── message3.txt
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration Options

### Send Mode

```json
{
  "send_enabled": true,
  "target_chat": "@username",
  "message_file": "messages",
  "rotation_mode": "sequential",
  "interval_seconds": 3600
}
```

- `target_chat` - Username, chat ID, or invite link
- `message_file` - Single file or folder with multiple .txt files
- `rotation_mode` - `sequential` (in order) or `random`
- `interval_seconds` - Interval between messages

### Forward Mode

```json
{
  "forward_enabled": true,
  "forward_to": "@your_account"
}
```

Forwards all incoming DMs to specified account **without marking as read**.

## 🎯 Use Cases

- 📢 **Channel management** - Auto-post to channels
- 🔔 **Notification forwarding** - Read messages from another device
- 💼 **Client management** - Never miss a message
- 📊 **Marketing automation** - Schedule promotional messages
- 🔄 **Multi-account sync** - Keep accounts in sync

## 🛡️ Features

### FloodWait Protection
Automatically adjusts intervals when Telegram rate-limits.

### Message Rotation
Support for multiple messages with sequential or random rotation.

### Privacy-Focused
Forwards messages without marking original as read.

### Stable Connection
Auto-reconnection with configurable retries and timeouts.

## 📋 Requirements

- Python 3.7+
- Telegram account
- API credentials from https://my.telegram.org

## 🔧 Advanced Usage

### Multiple Message Files

1. Copy example folder:
```bash
cp -r messages_example messages
# or on Windows: xcopy messages_example messages /E /I
```

2. Edit message files:
```
messages/
├── message1.txt
├── message2.txt
└── message3.txt
```

3. Configure in `config.json`:
```json
"message_file": "messages"
```

Bot will rotate between them automatically.

### Server Deployment

**Linux (systemd):**
```bash
chmod +x install_service.sh
./install_service.sh
sudo systemctl start telegram_bot
```

**Background (screen/tmux/nohup):**
```bash
chmod +x start_background.sh
./start_background.sh
```

## 🤝 Contributing

Pull requests are welcome! Feel free to:
- Report bugs
- Suggest features
- Improve documentation

## 📄 License

MIT License - feel free to use for any purpose.

## 💬 Contact

- Telegram: [@yykssa](https://t.me/yykssa)
- Issues: [GitHub Issues](https://github.com/yourusername/telegram-unified-bot/issues)

## ⚠️ Disclaimer

Use responsibly. Don't spam. Respect Telegram's Terms of Service.

---

**Made with ❤️ by oneonecode**


