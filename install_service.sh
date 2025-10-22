#!/bin/bash

# Установка Telegram бота как systemd службы (Linux)

echo "🚀 Установка Telegram Bot"

CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

# Создаем service файл
cat > /tmp/telegram_bot.service << EOF
[Unit]
Description=Telegram Unified Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/unified_bot.py --config $CURRENT_DIR/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Установка
sudo cp /tmp/telegram_bot.service /etc/systemd/system/telegram_bot.service
sudo systemctl daemon-reload
sudo systemctl enable telegram_bot.service

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Команды:"
echo "  sudo systemctl start telegram_bot"
echo "  sudo systemctl stop telegram_bot"
echo "  sudo systemctl status telegram_bot"
echo "  sudo journalctl -u telegram_bot -f"
echo ""
