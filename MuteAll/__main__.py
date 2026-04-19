import time
from MuteAll import bot

if __name__ == "__main__":
    while True:
        try:
            bot.run()
        except Exception as e:
            print("Error:", e)
            print("Reiniciando en 5 segundos...")
            time.sleep(5)
