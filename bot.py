import logging
import subprocess
import threading
import os  
import platform 
import sys
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Словарь для активных процессов: chat_id -> {"process": subprocess, "thread": threading.Thread}
active_games = {}

def run_game_and_get_output(chat_id, user_choice):
    """
    Запускает игру как subprocess с флагом --single, отправляет выбор и читает вывод.
    Возвращает результат для показа в Telegram.
    """
    try:
        # Определяем путь к Python: сначала sys.executable, fallback для разных ОС
        python_exe = sys.executable  # Основной вариант: использует текущий Python
        if not os.path.exists(python_exe):  # Если не найден, fallback по ОС
            os_name = platform.system()
            if os_name == "Darwin":  # MacOS
                python_exe = "/usr/local/bin/python3"  # Ваш путь
            elif os_name == "Windows":
                python_exe = "python.exe"  # Или полный путь, если нужно
            elif os_name == "Linux":
                python_exe = "python3"
            else:
                raise Exception(f"Unsupported OS: {os_name}")

        # Путь к TestProgram.py: в той же папке, что и скрипт
        game_path = os.path.join(os.path.dirname(__file__), "TestProgram.py")
        if not os.path.exists(game_path):
            raise Exception(f"TestProgram.py not found at {game_path}")
        
        # Запускаем subprocess с флагом --single для однократной игры
        process = subprocess.Popen(
            [python_exe, game_path, "--single"],  # Флаг --single
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Отправляем выбор пользователя сразу
        process.stdin.write(user_choice + "\n")
        process.stdin.flush()
        
        # Небольшая пауза, чтобы игра обработала ввод
        time.sleep(0.1)
        
        # Читаем весь вывод игры
        result_output = ""
        while True:
            line = process.stdout.readline()
            if not line:
                break
            result_output += line
        
        # Ждём завершения процесса
        process.wait()
        
        return result_output.strip()  # Возвращаем весь вывод для показа
    except Exception as e:
        return f"Error running game: {str(e)}"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик /start.
    """
    await update.message.reply_text("Welcome to Rock, Paper, Scissors! Use /play to start.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик /play: запускает игру и просит выбор.
    """
    chat_id = update.effective_chat.id
    await update.message.reply_text("Starting game... Choose your action: paper, rock, or scissors.")
    context.user_data['waiting_for_choice'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик сообщений: отправляет выбор в subprocess и показывает результат.
    """
    chat_id = update.effective_chat.id
    if context.user_data.get('waiting_for_choice'):
        user_choice = update.message.text.strip().lower()
        if user_choice in ["paper", "rock", "scissors"]:  # Простая проверка, без логики игры
            # Запускаем игру в отдельном потоке, чтобы не блокировать бота
            def game_thread():
                result = run_game_and_get_output(chat_id, user_choice)
                # После получения результата сохраняем результат
                active_games[chat_id]['result'] = result
            
            thread = threading.Thread(target=game_thread)
            active_games[chat_id] = {'thread': thread, 'result': None}
            thread.start()
            
            # Ждём завершения с таймаутом
            thread.join(timeout=5)  # 5 секунд таймаут
            result = active_games[chat_id].get('result', "Game timed out.")
            
            # Проверяем на пустой результат
            if not result.strip():
                result = "Error: No output from game. Check TestProgram.py."
            
            await update.message.reply_text(result)
            context.user_data['waiting_for_choice'] = False
            del active_games[chat_id]  # Очищаем
        else:
            await update.message.reply_text("Invalid choice. Choose paper, rock, or scissors.")
    else:
        await update.message.reply_text("Use /play to start playing.")

def main():
    """
    Основная функция.
    """
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    application = ApplicationBuilder().token("").build() # Вставьте ваш токен здесь
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
