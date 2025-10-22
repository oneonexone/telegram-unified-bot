from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import asyncio
import json
import os
import sys
import argparse
import random

def set_terminal_color():
    """Меняет цвет терминала на зеленый (Windows)"""
    try:
        if os.name == 'nt':  # Windows
            os.system('color c')  # Зеленый на черном
        else:  # Linux/Mac
            print('\033[32m')  # Зеленый цвет
    except:
        pass  # Если не получается - не беда

def load_config(config_path='config.json'):
    """Загружает конфигурацию из JSON файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл конфигурации '{config_path}' не найден!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в JSON файле: {e}")
        sys.exit(1)

async def run_bot(config):
    """Запускает объединенного бота"""
    
    # Основные параметры
    api_id = config.get('api_id')
    api_hash = config.get('api_hash')
    phone_number = config.get('phone_number')
    
    if not all([api_id, api_hash, phone_number]):
        print("❌ Ошибка: api_id, api_hash, phone_number обязательны!")
        sys.exit(1)
    
    # Параметры отправки сообщений
    send_enabled = config.get('send_enabled', False)
    target_chat = config.get('target_chat')
    message_text = config.get('message')
    message_file = config.get('message_file')
    interval_seconds = config.get('interval_seconds', 3600)
    
    # Параметры пересылки входящих
    forward_enabled = config.get('forward_enabled', False)
    forward_to = config.get('forward_to')
    
    # Загружаем сообщения (один файл или папка с несколькими)
    messages_list = []
    
    if message_file:
        # Проверяем - это файл или папка?
        if os.path.isdir(message_file):
            # Это папка - загружаем все .txt файлы
            try:
                txt_files = sorted([f for f in os.listdir(message_file) if f.endswith('.txt')])
                for txt_file in txt_files:
                    file_path = os.path.join(message_file, txt_file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            messages_list.append(content)
                print(f"✅ Загружено {len(messages_list)} сообщений из папки '{message_file}'")
            except Exception as e:
                print(f"❌ Ошибка чтения папки '{message_file}': {e}")
        else:
            # Это файл - загружаем как обычно
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        messages_list.append(content)
            except Exception as e:
                print(f"❌ Ошибка чтения файла '{message_file}': {e}")
    elif message_text:
        messages_list.append(message_text)
    
    # Режим ротации
    rotation_mode = config.get('rotation_mode', 'sequential')  # sequential или random
    current_message_index = 0
    
    # Проверка режимов
    if not send_enabled and not forward_enabled:
        print("❌ Включите хотя бы один режим: send_enabled или forward_enabled")
        sys.exit(1)
    
    if send_enabled and not all([target_chat, (message_text or messages_list)]):
        print("❌ Для отправки нужны: target_chat и message (или message_file)")
        sys.exit(1)
    
    if forward_enabled and not forward_to:
        print("❌ Для пересылки нужен: forward_to")
        sys.exit(1)
    
    # Создаем клиент с увеличенными таймаутами
    session_name = config.get('session_name', 'session')
    client = TelegramClient(
        session_name, 
        api_id, 
        api_hash,
        connection_retries=5,  # Больше попыток переподключения
        retry_delay=3,  # Задержка между попытками
        timeout=30,  # Увеличенный таймаут
        auto_reconnect=True  # Автоматическое переподключение
    )
    
    # Обработчик входящих сообщений (БЕЗ ПРОЧТЕНИЯ!)
    if forward_enabled:
        @client.on(events.NewMessage(incoming=True))
        async def forward_handler(event):
            """Пересылает входящие сообщения НАПРЯМУЮ БЕЗ отметки о прочтении"""
            # Пропускаем сообщения из групп и каналов - ТОЛЬКО ЛС!
            if event.is_group or event.is_channel:
                return
            
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                sender_name = getattr(sender, 'first_name', 'Unknown')
                sender_username = getattr(sender, 'username', None)
                chat_title = getattr(chat, 'title', sender_name)
                
                # Формируем заголовок
                header = f"📨 От: {sender_name}"
                if sender_username:
                    header += f" (@{sender_username})"
                header += "\n"
                
                if hasattr(chat, 'title'):
                    header += f"💬 Чат: {chat_title}\n"
                
                header += f"{'='*40}\n"
                
                # Текст сообщения
                message_content = event.message.text or "[Медиа/Стикер/Файл]"
                full_message = header + message_content
                
                # Отправляем НАПРЯМУЮ (не помечая исходное как прочитанное)
                await client.send_message(forward_to, full_message)
                
                print(f"✅ Переслано от {sender_name}")
                
            except FloodWaitError as e:
                print(f"⏳ FloodWait: ждем {e.seconds} секунд перед следующей пересылкой...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"❌ Ошибка пересылки: {e}")
    
    # Функция периодической отправки
    async def send_periodically():
        """Отправляет сообщения с интервалом"""
        if not send_enabled:
            return
        
        nonlocal current_message_index
        current_interval = interval_seconds
        
        while True:
            try:
                # Выбираем сообщение для отправки
                if messages_list:
                    if rotation_mode == 'random':
                        current_text = random.choice(messages_list)
                        print(f"📤 Отправка сообщения (случайное из {len(messages_list)}) в '{target_chat}'...")
                    else:  # sequential
                        current_text = messages_list[current_message_index]
                        print(f"📤 Отправка сообщения ({current_message_index + 1}/{len(messages_list)}) в '{target_chat}'...")
                        current_message_index = (current_message_index + 1) % len(messages_list)
                else:
                    current_text = message_text
                    print(f"📤 Отправка сообщения в '{target_chat}'...")
                
                await client.send_message(target_chat, current_text)
                print(f"✅ Отправлено! Следующая отправка через {current_interval} сек.")
                
                # Сбрасываем интервал на исходный после успешной отправки
                current_interval = interval_seconds
                await asyncio.sleep(current_interval)
                
            except FloodWaitError as e:
                # Telegram требует подождать - адаптируем интервал
                wait_time = e.seconds
                print(f"⏳ FloodWait: требуется подождать {wait_time} секунд...")
                print(f"🔄 Адаптирую интервал: {interval_seconds} → {wait_time + 60} сек")
                
                current_interval = wait_time + 60  # Добавляем буфер 60 сек
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")
                await asyncio.sleep(current_interval)
    
    try:
        # Подключаемся
        await client.start(phone=phone_number)
        me = await client.get_me()
        
        print("="*60)
        print("🤖 Unified Telegram Bot")
        print("="*60)
        print(f"✅ Подключено")
        print(f"👤 Аккаунт: {me.first_name} (@{me.username})")
        print()
        
        if send_enabled:
            print(f"📤 Отправка: ВКЛЮЧЕНА → {target_chat} (каждые {interval_seconds} сек)")
        else:
            print(f"📤 Отправка: ВЫКЛЮЧЕНА")
        
        if forward_enabled:
            print(f"📬 Пересылка: ВКЛЮЧЕНА → {forward_to} (напрямую)")
        else:
            print(f"📬 Пересылка: ВЫКЛЮЧЕНА")
        
        print()
        print("🔄 Бот запущен! Нажмите Ctrl+C для остановки")
        print("="*60)
        print()
        
        # Запускаем обе задачи параллельно
        tasks = []
        
        if send_enabled:
            tasks.append(asyncio.create_task(send_periodically()))
        
        if forward_enabled:
            # Форвардер работает через events, просто ждем
            tasks.append(asyncio.create_task(client.run_until_disconnected()))
        else:
            # Если только отправка, просто ждем задачу
            if tasks:
                await tasks[0]
        
        # Ждем выполнения задач
        if len(tasks) > 1:
            await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\n⚠️ Остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()
        print("👋 Отключено")

def main():
    parser = argparse.ArgumentParser(description='Unified Telegram Bot')
    parser.add_argument('--config', default='config.json', help='Путь к конфигу')
    args = parser.parse_args()
    
    # Меняем цвет терминала
    set_terminal_color()
    
    config = load_config(args.config)
    asyncio.run(run_bot(config))

if __name__ == "__main__":
    main()
