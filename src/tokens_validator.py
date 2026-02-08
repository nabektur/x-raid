import requests
import threading
import os
import time
from colorama import Fore, init

init(autoreset=True)

class TokenValidator:
    def __init__(self):
        self.valid_tokens = []
        self.locked_tokens = []
        self.invalid_tokens = []
        self.lock = threading.Lock()
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

    def check_token(self, token):
        time_rn = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            response = requests.get('https://discord.com/api/v9/users/@me/library', headers={"Authorization": token})

            if response.status_code == 200:
                with self.lock:
                    self.valid_tokens.append(token)
            elif response.status_code == 403:
                with self.lock:
                    self.locked_tokens.append(token)
            elif response.status_code == 401:
                with self.lock:
                    self.invalid_tokens.append(token)
            else:
                with self.lock:
                    self.locked_tokens.append(token)
        except Exception as e:
            with self.lock:
                self.locked_tokens.append(token)

    def remove_invalid_tokens(self):
        with open("tokens.txt", "w", encoding="utf-8") as f:
            for token in self.valid_tokens + self.locked_tokens:
                f.write(token + "\n")

    def run_validator(self):
        threads = []
        for token in self.tokens:
            t = threading.Thread(target=self.check_token, args=(token,))
            threads.append(t)
            t.start()

            if len(threads) >= 1000:
                for t in threads:
                    t.join()
                threads = []

        for t in threads:
            t.join()

        print(f"{Fore.GREEN}✔ ДЕЙСТВИТЕЛЬНЫЕ   | {len(self.valid_tokens):03} | токены.")
        print(f"{Fore.YELLOW}⚠ ЗАБЛОКИРОВАННЫЕ  | {len(self.locked_tokens):03} | по email или телефону.")
        print(f"{Fore.RED}✖ НЕДЕЙСТВИТЕЛЬНЫЕ | {len(self.invalid_tokens):03} | токены")

        if self.invalid_tokens:
            confirm = input(Fore.YELLOW + "Вы хотите удалить недействительные токены из tokens.txt? (да/нет): ").strip().lower()
            if confirm == "да":
                self.remove_invalid_tokens()
                print(Fore.GREEN + "Недействительные токены удалены из tokens.txt.")

        input(Fore.RED + "Нажмите ENTER для возврата.")
        self.main_menu()

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)
        self.clear_console()
        os.system('python main.py')

if __name__ == "__main__":
    validator = TokenValidator()
    validator.run_validator()