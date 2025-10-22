from telethon import TelegramClient
import asyncio
import json
import sys

def load_config(config_path='config.json'):
    """Загружает конфигурацию из JSON файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл конфигурации '{config_path}' не найден!")
        print("Создайте config.json на основе config_example.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в JSON файле: {e}")
        sys.exit(1)

async def send_message():
    """Отправляет сообщение в указанный чат от вашего аккаунта"""
    
    # Загружаем конфиг
    config = load_config()
    
    api_id = config.get('api_id')
    api_hash = config.get('api_hash')
    phone_number = config.get('phone_number')
    
    if not all([api_id, api_hash, phone_number]):
        print("❌ Ошибка: Не заданы API_ID, API_HASH или PHONE_NUMBER в config.json")
        print("\nИнструкция:")
        print("1. Откройте https://my.telegram.org")
        print("2. Войдите с вашим номером телефона")
        print("3. Перейдите в 'API development tools'")
        print("4. Создайте приложение и получите API_ID и API_HASH")
        print("5. Заполните их в config.json")
        return
    
    # Создаем клиент
    session_name = config.get('session_name', 'session')
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        await client.start(phone=phone_number)
        print("✅ Успешно подключено к Telegram!")
        print(f"👤 Вы вошли как: {(await client.get_me()).first_name}")
        
        # Запрашиваем данные для отправки
        print("\n" + "="*50)
        chat_input = input("📝 Введите username чата, ID или номер телефона получателя (например: @username, -1001234567890, или +79991234567): ").strip()
        
        print("💬 Введите текст сообщения (для завершения ввода нажмите Enter на пустой строке):")
        message_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            message_lines.append(line)
        message_text = "\n".join(message_lines)
        
        if not chat_input or not message_text:
            print("❌ Чат и сообщение не могут быть пустыми!")
            return
        
        # Отправляем сообщение
        print(f"\n📤 Отправка сообщения...")
        await client.send_message(chat_input, message_text)
        print("✅ Сообщение успешно отправлено!")
        
        # Спрашиваем, хочет ли отправить еще
        while True:
            more = input("\n🔄 Отправить еще одно сообщение? (y/n): ").strip().lower()
            if more in ['n', 'no', 'нет', '']:
                break
            elif more in ['y', 'yes', 'да']:
                print("\n💬 Введите текст следующего сообщения (для завершения ввода нажмите Enter на пустой строке):")
                message_lines = []
                while True:
                    line = input()
                    if line.strip() == "":
                        break
                    message_lines.append(line)
                message_text = "\n".join(message_lines)
                
                if message_text.strip():
                    print(f"📤 Отправка сообщения...")
                    await client.send_message(chat_input, message_text)
                    print("✅ Сообщение успешно отправлено!")
                else:
                    print("❌ Пустое сообщение, пропускаем...")
            else:
                print("❌ Введите 'y' (да) или 'n' (нет)")
        
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        await client.disconnect()
        print("\n👋 Отключено от Telegram")

def main():
    """Главная функция"""
    print("="*50)
    print("🤖 Telegram Message Sender Bot")
    print("="*50)
    
    try:
        asyncio.run(send_message())
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)

if __name__ == "__main__":
    main()
