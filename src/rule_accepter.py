import requests
import os
from colorama import Fore, init
from datetime import datetime
import time

init(autoreset=True)

class RuleAccepter:
    def __init__(self, tokens_file='tokens.txt'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as f:
                f.write('')
            exit()
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]                
        return tokens

    def acceptrules(self, token, server_id):
        headers = {"Authorization": token}
        try:
            response = requests.get(f"https://discord.com/api/v10/guilds/{server_id}/member-verification?with_guild=false", headers=headers).json()
            result = requests.put(f"https://discord.com/api/v10/guilds/{server_id}/requests/@me", headers=headers, json=response)
            token_short = token.split(".")[0]
            time_rn = datetime.now().strftime('%H:%M:%S')
            if result.status_code == 201:
                print(f"{Fore.GREEN}{time_rn} [Успешно] -> Принято {token_short}****")
            else:
                print(f"{Fore.RED}{time_rn} [Ошибка] -> Неудачный {token_short}**** {result.text}")
        except Exception as e:
            time_rn = datetime.now().strftime('%H:%М:%S')
            print(f"{Fore.RED}{time_rn} [EXCEPTION] -> {str(e)}")

    def run_rule_accepter(self, server_id):
        for token in self.tokens:
            self.acceptrules(token, server_id)
        
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

if __name__ == "__main__":
    rule_accepter = RuleAccepter()
    server_id = input(Fore.RED + "Введите SERVER ID: ")
    rule_accepter.run_rule_accepter(server_id)