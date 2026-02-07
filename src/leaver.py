import time
import datetime
import requests
import threading
import os
from colorama import Fore, init

init(autoreset=True)

class GuildLeaver:
    def __init__(self):
        self.tokens = self.load_tokens()
        self.guild_id = None

    @staticmethod
    def load_tokens():
        if not os.path.exists("tokens.txt"):
            with open("tokens.txt", "w") as f:
                pass 

        with open("tokens.txt", "r") as f:
            return [token.strip() for token in f.readlines()]

    def leave_guild(self):
        self.guild_id = input(Fore.RED + "Введите ID гильдии: ")

        if not self.guild_id:
            print("Ошибка: поле ID гильдии не может быть пустым.")
            time.sleep(0.7)
            return

        apilink = f"https://discord.com/api/v9/users/@me/guilds/{self.guild_id}"
        threads = []

        for token in self.tokens:
            sesheaders = {"Authorization": token}

            t = threading.Thread(target=self.make_request, args=(apilink, sesheaders, token))
            threads.append(t)
            t.start()

            if len(threads) >= 10:
                for t in threads:
                    t.join()
                threads = []

        for t in threads:
            t.join()

        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def make_request(url, headers, token):
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f'{Fore.GREEN}[ + ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен: {token[:6]}... Успешно вышел из гильдии.')
        else:
            print(f'{Fore.RED}{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При выходе для токена, статус: {response.status_code}')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

if __name__ == "__main__":
    leaver = GuildLeaver()
    leaver.leave_guild()