#!/bin/bash

# Запуск бота в фоне (Linux)

echo "🚀 Запуск бота в фоне..."

if command -v screen &> /dev/null; then
    screen -dmS telegram_bot python3 unified_bot.py --config config.json
    echo "✅ Запущено в screen (подключиться: screen -r telegram_bot)"
elif command -v tmux &> /dev/null; then
    tmux new-session -d -s telegram_bot "python3 unified_bot.py --config config.json"
    echo "✅ Запущено в tmux (подключиться: tmux attach -t telegram_bot)"
else
    nohup python3 unified_bot.py --config config.json > bot.log 2>&1 &
    echo "✅ Запущено в фоне (логи: tail -f bot.log)"
fi
