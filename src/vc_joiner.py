import websocket
import json
import time
import os
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

class VCJoiner:
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

    def vcjoiner(self, token, server_id, channel_id):
        try:
            ws = websocket.WebSocket()
            ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
            ws.send(json.dumps({"op": 2, "d": {"token": token, "properties": {"$os": "windows", "$browser": "Discord", "$device": "desktop"}}}))
            ws.send(json.dumps({"op": 4, "d": {"guild_id": server_id, "channel_id": channel_id, "self_mute": False, "self_deaf": False}}))
            
            result = ws.recv()
            if result:
                token_short = token.split(".")[0]
                time_rn = datetime.now().strftime('%H:%M:%S')
                print(f"{Fore.GREEN}{time_rn} [Присоеденился] -> Успешно подключен {token_short}****")
            else:
                raise Exception(Fore.RED + "Нет ответа от сервера")
                
        except Exception as e:
            time_rn = datetime.now().strftime('%H:%M:%S')
            print(f"{Fore.RED}{time_rn} [Ошибка] -> Не удалось подключиться {token.split('.')[0]}**** - {str(e)}")

    def run_joiner(self, server_id, channel_id):
        for token in self.tokens:
            self.vcjoiner(token, server_id, channel_id)
        
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

if __name__ == '__main__':
    vc_joiner = VCJoiner()
    server_id = input(Fore.RED + "Введите SERVER ID: ")
    channel_id = input(Fore.RED + "Введите CHANNEL ID: ")
    vc_joiner.run_joiner(server_id, channel_id)