import json
import sys
import os
import concurrent.futures
import time
from threading import Lock
from websocket import create_connection
from colorama import Fore, init
from datetime import datetime
import ssl, certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

init(autoreset=True)

class TokenManager:
    def __init__(self):
        self.tokens = self.load_tokens()

    @staticmethod
    def load_tokens():
        if not os.path.exists("tokens.txt"):
            with open("tokens.txt", "w") as f:
                pass

        with open("tokens.txt", "r") as f:
            return [token.strip() for token in f.readlines()]

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)
        self.clear_console()
        os.system('python main.py')

def Onliner():
    details = input(Fore.RED + "Детали: ")
    state = input(Fore.RED + "Состояние: ")
    name = input(Fore.RED + "Имя: ")
    platform = sys.platform
    output_lock = Lock()

    def token_onliner(token):
        try:
            ws_online = create_connection("wss://gateway.discord.gg/?encoding=json&v=9", sslopt={"context": ssl_context})
            response = ws_online.recv()
            ws_online.send(json.dumps({
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": platform,
                        "$browser": "RTB",
                        "$device": f"{platform} Device",
                    },
                    "presence": {
                        "game": {
                            "name": name,
                            "type": 0,
                            "details": details,
                            "state": state,
                        },
                        "status": "online",
                        "since": 0,
                        "activities": [],
                        "afk": False,
                    },
                },
                "s": None,
                "t": None
            }))

            with output_lock:
                print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Успешно: {token[:6]}...')
        except Exception as e:
            with output_lock:
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При изменении статуса, статус: {response.status}...')
                pass

    tokens = TokenManager().tokens

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
        executor.map(token_onliner, tokens)

    print(Fore.RED + 'Токены активированы и будут оставаться онлайн некоторое время.')

    input(Fore.RED + "Нажмите ENTER для возврата.")
    TokenManager().main_menu()

if __name__ == "__main__":
    Onliner()