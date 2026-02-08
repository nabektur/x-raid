import requests
import os
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

class GuildInfo:
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

    def get_guild_info(self, token, guild_id):
        headers = {"Authorization": token.strip()}
        response = requests.get(
            f"https://discord.com/api/guilds/{guild_id}",
            headers=headers,
            params={"with_counts": True}
        ).json()

        if 'owner_id' in response:
            owner_id = response['owner_id']
            owner = requests.get(
                f"https://discord.com/api/guilds/{guild_id}/members/{owner_id}",
                headers=headers,
                params={"with_counts": True}
            ).json()
            return response, owner
        return response, None

    def display_info(self, guild_id):
        for token in self.tokens:
            response, owner = self.get_guild_info(token, guild_id)
            if 'owner_id' in response:
                creation_date = datetime.fromtimestamp(((int(guild_id) >> 22) + 1420070400000) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                boost_count = response.get('premium_subscription_count', 'N/A')
                print(f'''{Fore.RED}MEMBER COUNT{Fore.RESET}: {response['approximate_member_count']} members
{Fore.RED}SERVER ID{Fore.RESET}: {response['id']}
{Fore.RED}SERVER NAME{Fore.RESET}: {response['name']}
{Fore.RED}OWNER NAME{Fore.RESET}: {owner['user']['username']}#{owner['user']['discriminator']}
{Fore.RED}OWNER ID{Fore.RESET}: {response['owner_id']}
{Fore.RED}REGION{Fore.RESET}: {response['region']}
{Fore.RED}BOOSTS{Fore.RESET}: {boost_count}
{Fore.RED}CREATION DATE{Fore.RESET}: {creation_date}''')
                break
        else:
            print(f"{Fore.RED}Ошибка: Неверные токены или проблемы с подключением.")

        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    guild_id = input(Fore.RED + "Введите идентификатор сервера: ")
    guild_info = GuildInfo()
    guild_info.display_info(guild_id)