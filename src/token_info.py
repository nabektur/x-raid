import os
import requests
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

def Info():
    token = input(f"{Fore.RED}Введите TOKEN: {Fore.RESET}")

    if not token:
        print(f"{Fore.RED}Ошибка: Ввод не может быть пустым.")
        return

    headers = {"Authorization": token.strip()}
    try:
        r = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        if r.status_code != 200:
            print(f"{Fore.RED}Ошибка: Неверный токен или проблемы с подключением.")
            return

        user_data = r.json()
        badges = get_badges(user_data['flags'])

        userName = user_data['username'] + '#' + user_data['discriminator']
        userID = user_data['id']
        phone = user_data['phone']
        email = user_data['email']
        mfa = user_data['mfa_enabled']
        has_nitro, days_left = check_nitro(headers)

        print(f'''{Fore.RED}MAIL{Fore.RESET}: {email}
{Fore.RED}PHONE{Fore.RESET}: {phone}
{Fore.RED}2FA{Fore.RESET}: {mfa}
{Fore.RED}USER ID{Fore.RESET}: {userID}
{Fore.RED}USER{Fore.RESET}: {userName}
{Fore.RED}NITRO{Fore.RESET}: {has_nitro} / {days_left if has_nitro else "0"} days
{Fore.RED}BADGES{Fore.RESET}: {badges}''')

        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        clear_console()
        os.system('python main.py')
            
    except Exception as e:
        print(f"{Fore.RED}Ошибка: {e}")

def get_badges(flags):
    badges = []
    badge_dict = {
        1: "Staff",
        2: "Partner",
        4: "Hypesquad Event",
        8: "Green Bughunter",
        64: "Bravery",
        128: "Brilliance",
        256: "Balance",
        512: "Early Supporter",
        16384: "Gold BugHunter",
        131072: "Verified Bot Developer"
    }
    for key, value in badge_dict.items():
        if flags & key:
            badges.append(value)
    return ", ".join(badges) if badges else "None"

def check_nitro(headers):
    res = requests.get('https://discordapp.com/api/v9/users/@me/billing/subscriptions', headers=headers)
    nitro_data = res.json()
    has_nitro = bool(len(nitro_data) > 0)

    if has_nitro:
        d1 = datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        d2 = datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%м-%dT%H:%M:%S")
        days_left = abs((d2 - d1).days)
        return True, days_left
    return False, 0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    Info()