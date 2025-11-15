from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import asyncio
import json
import os
import sys
import argparse
import random

def set_terminal_color():
    """Меняет цвет терминала на красный (Windows)"""
    try:
        if os.name == 'nt':  # Windows
            os.system('color c')  # красный цвет
        else:  # Linux/Mac
            print('\033[32m')  # 
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
    
    # Загружаем конфигурацию для проверки доступности режимов
    chats_config = config.get('chats', [])
    forward_to = config.get('forward_to')
    
    # Интерактивный выбор режима работы
    print("\n" + "="*60)
    print("🤖 Выберите режим работы:")
    print("="*60)
    print("1️⃣  Только рассылка сообщений")
    print("2️⃣  Только пересылка входящих сообщений")
    print("3️⃣  Вместе (рассылка + пересылка)")
    print("="*60)
    
    while True:
        choice = input("\n👉 Ваш выбор (1/2/3): ").strip()
        
        if choice == '1':
            # Только рассылка
            if not chats_config:
                print("❌ Ошибка: для рассылки нужен массив 'chats' в конфиге")
                sys.exit(1)
            send_enabled = True
            forward_enabled = False
            print("✅ Выбран режим: Только рассылка")
            break
            
        elif choice == '2':
            # Только пересылка
            if not forward_to:
                print("❌ Ошибка: для пересылки нужен 'forward_to' в конфиге")
                sys.exit(1)
            send_enabled = False
            forward_enabled = True
            print("✅ Выбран режим: Только пересылка")
            break
            
        elif choice == '3':
            # Вместе
            if not chats_config:
                print("❌ Ошибка: для рассылки нужен массив 'chats' в конфиге")
                sys.exit(1)
            if not forward_to:
                print("❌ Ошибка: для пересылки нужен 'forward_to' в конфиге")
                sys.exit(1)
            send_enabled = True
            forward_enabled = True
            print("✅ Выбран режим: Рассылка + Пересылка")
            break
            
        else:
            print("❌ Введите 1, 2 или 3")
    
    # Функция загрузки сообщений
    def load_messages(message_file=None, message_text=None):
        """Загружает сообщения из файла или папки"""
        messages_list = []
        
        if message_file:
            if os.path.isdir(message_file):
                try:
                    txt_files = sorted([f for f in os.listdir(message_file) if f.endswith('.txt')])
                    for txt_file in txt_files:
                        file_path = os.path.join(message_file, txt_file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                messages_list.append(content)
                except Exception as e:
                    print(f"❌ Ошибка чтения папки '{message_file}': {e}")
            else:
                try:
                    with open(message_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            messages_list.append(content)
                except Exception as e:
                    print(f"❌ Ошибка чтения файла '{message_file}': {e}")
        elif message_text:
            messages_list.append(message_text)
        
        return messages_list
    
    # Проверки уже выполнены выше при выборе режима
    
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
    
    # Функция периодической отправки для одного чата
    async def send_to_chat(chat_config, chat_index):
        """Отправляет сообщения в конкретный чат с заданным интервалом"""
        target_chat = chat_config.get('target_chat')
        message_file = chat_config.get('message_file')
        message_text = chat_config.get('message')
        rotation_mode = chat_config.get('rotation_mode', 'sequential')
        interval_seconds = chat_config.get('interval_seconds', 3600)
        
        # Загружаем сообщения для этого чата
        messages_list = load_messages(message_file, message_text)
        
        if not messages_list:
            print(f"❌ Чат #{chat_index + 1}: нет сообщений для отправки")
            return
        
        print(f"✅ Чат #{chat_index + 1} ({target_chat}): загружено {len(messages_list)} сообщений")
        
        current_message_index = 0
        current_interval = interval_seconds
        
        while True:
            try:
                # Выбираем сообщение для отправки
                if rotation_mode == 'random':
                    current_text = random.choice(messages_list)
                    print(f"📤 Чат #{chat_index + 1} → {target_chat}: отправка (случайное из {len(messages_list)})")
                else:  # sequential
                    current_text = messages_list[current_message_index]
                    print(f"📤 Чат #{chat_index + 1} → {target_chat}: отправка ({current_message_index + 1}/{len(messages_list)})")
                    current_message_index = (current_message_index + 1) % len(messages_list)
                
                await client.send_message(target_chat, current_text)
                print(f"✅ Чат #{chat_index + 1}: отправлено! Следующая через {current_interval} сек.")
                
                # Сбрасываем интервал на исходный после успешной отправки
                current_interval = interval_seconds
                await asyncio.sleep(current_interval)
                
            except FloodWaitError as e:
                # Telegram требует подождать - адаптируем интервал
                wait_time = e.seconds
                print(f"⏳ Чат #{chat_index + 1}: FloodWait {wait_time} сек...")
                print(f"🔄 Чат #{chat_index + 1}: адаптирую интервал {interval_seconds} → {wait_time + 60} сек")
                
                current_interval = wait_time + 60  # Добавляем буфер 60 сек
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Чат #{chat_index + 1}: ошибка отправки: {e}")
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
            print(f"📤 Отправка: ВКЛЮЧЕНА ({len(chats_config)} чатов)")
            for idx, chat in enumerate(chats_config):
                interval = chat.get('interval_seconds', 3600)
                print(f"   Чат #{idx + 1}: {chat.get('target_chat')} (каждые {interval} сек)")
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
        
        # Запускаем задачи параллельно
        tasks = []
        
        # Создаем задачу для каждого чата
        if send_enabled:
            for idx, chat_config in enumerate(chats_config):
                task = asyncio.create_task(send_to_chat(chat_config, idx))
                tasks.append(task)
        
        # Добавляем форвардер если включен
        if forward_enabled:
            tasks.append(asyncio.create_task(client.run_until_disconnected()))
        
        # Ждем выполнения всех задач
        if tasks:
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
