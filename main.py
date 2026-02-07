import os
import time
import ctypes
import requests
from colorama import Fore, Style, init
import os
import re
import sys
import time

init(autoreset=True)

def set_console_properties():
    if os.name == 'nt':
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.kernel32.SetConsoleTitleW("X-Raid Menu")
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 0x2) 

set_console_properties()

RESET_ALL = Style.RESET_ALL

tokens = []

def read_tokens_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                token = line.strip()
                if token:
                    tokens.append(token)

    else:
        with open(file_path, 'w') as file:
            pass  

def read_proxies_from_file(file_path):
    proxies = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                proxy = line.strip()
                if proxy:
                    proxies.append(proxy)
    else:
        with open(file_path, 'w') as file:
            pass  
    return proxies

def get_working_proxy(proxies):
    for proxy in proxies:
        if is_proxy_working(proxy):
            return proxy
    return None

def is_proxy_working(proxy):
    try:
        response = requests.get('https://discord.com/api/v9/', proxies={'http': proxy, 'https': proxy}, timeout=5)
        return response.status_code == 200
    except:
        return False

def banner():
    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 80
    
    banner_art = r"""
    ╦ ╦    ═╦═    ╦═╗ ╔═╗ ╦ ╔╦╗
    ╔╩╗     ╬     ╠╦╝ ╠═╣ ║  ║║
    ╩ ╩    ═╩═    ╩╚═ ╩ ╩ ╩ ╩═╝
    """
    
    banner_lines = banner_art.strip('\n').split('\n')
    
    print("")
    for line in banner_lines:
        stripped_line = line.lstrip()
        padding = max(0, (columns - len(stripped_line)) // 2)
        print(' ' * padding + Fore.LIGHTRED_EX + Style.BRIGHT + stripped_line + RESET_ALL)
    print("")
    
    subtitle = "» Advanced Discord Raid Tool «"
    subtitle_padding = max(0, (columns - len(subtitle)) // 2)
    print(' ' * subtitle_padding + Fore.RED + subtitle + RESET_ALL)
    print("")
    
    tokens_info = f"Токены: {Fore.LIGHTRED_EX}{Style.BRIGHT}{len(tokens)}{RESET_ALL} {Fore.LIGHTBLACK_EX}│{RESET_ALL} Прокси: {Fore.LIGHTRED_EX}{Style.BRIGHT}{len(proxies)}{RESET_ALL}"
    clean_info = strip_ansi_codes(tokens_info)
    info_padding = max(0, (columns - len(clean_info)) // 2)
    print(' ' * info_padding + tokens_info)
    print("")

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def strip_ansi_codes(text):
    """Удаляет ANSI escape-последовательности из строки"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def menu():
    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 80

    while True:
        clear_console()
        banner()
        
        ACCENT = Fore.RED + Style.BRIGHT
        HEADER = Fore.LIGHTRED_EX + Style.BRIGHT
        NUMBER = Fore.LIGHTRED_EX + Style.BRIGHT
        SEPARATOR = Fore.RED
        TEXT = Fore.LIGHTWHITE_EX
        EXIT_TEXT = Fore.LIGHTBLACK_EX
        
        menu_lines = []
        
        menu_lines.append(('header', f"{HEADER}{'═' * 60}{RESET_ALL}"))
        menu_lines.append(('header', f"{HEADER}{'☢  MAIN MENU ☢'.center(60)}{RESET_ALL}"))
        menu_lines.append(('header', f"{HEADER}{'═' * 60}{RESET_ALL}"))
        menu_lines.append(('empty', ''))
        
        options = [
            [('01', 'Info Token'), ('02', 'GuildInfo')],
            [('', ''), ('', '')],
            [('03', 'Scraper'), ('04', 'Invite Creator')],
            [('', ''), ('', '')],
            [('05', 'Joiner'), ('06', 'Leaver')],
            [('07', 'RuleAccepter'), ('08', 'ButtonClicker')],
            [('', ''), ('', '')],
            [('09', 'Onliner'), ('10', 'Spammer')],
            [('11', 'Spamthreadsall'), ('', '')],
            [('', ''), ('', '')],
            [('12', 'Nick Chooser'), ('13', 'HypeSquadChooser')],
            [('14', 'Typier'), ('', '')],
        ]
        
        for row in options:
            if row[0][0] == '':
                menu_lines.append(('empty', ''))
                continue
                
            left_num, left_text = row[0]
            right_num, right_text = row[1] if len(row) > 1 and row[1][0] else ('', '')
            
            left_part = f"{NUMBER}{left_num}{RESET_ALL} {SEPARATOR}▸{RESET_ALL} {TEXT}{left_text}{RESET_ALL}"
            
            if right_num:
                right_part = f"{NUMBER}{right_num}{RESET_ALL} {SEPARATOR}▸{RESET_ALL} {TEXT}{right_text}{RESET_ALL}"
                
                left_text_length = len(f"{left_num} ▸ {left_text}")
                spaces_needed = 34 - 4 - left_text_length
                
                line = f"    {left_part}{' ' * spaces_needed}{right_part}"
            else:
                line = f"    {left_part}"
            
            menu_lines.append(('option', line))
        
        menu_lines.append(('empty', ''))
        menu_lines.append(('separator', f"{SEPARATOR}{'─' * 60}{RESET_ALL}"))
        
        exit_line = f"    {EXIT_TEXT}00{RESET_ALL} {SEPARATOR}▸{RESET_ALL} {EXIT_TEXT}Exit{RESET_ALL}"
        menu_lines.append(('exit', exit_line))

        menu_padding = 0
        
        for line_type, line in menu_lines:
            if line_type == 'empty':
                print()
            else:
                clean_line = strip_ansi_codes(line)
                padding = max(0, (columns - len(clean_line)) // 2)
                print(' ' * (menu_padding or padding) + line)
                if not menu_padding:
                    menu_padding = padding

        prompt_text = "⟩⟩ Выберите пункт меню: "
        clean_prompt = strip_ansi_codes(prompt_text)
        prompt_padding = max(0, (columns - len(clean_prompt)) // 2)
        print()
        print(' ' * prompt_padding + ACCENT + '⟩⟩ ' + RESET_ALL + TEXT + 'Выберите пункт меню: ' + RESET_ALL, end='')
        
        choice = input().strip()

        if proxies:
            proxy = get_working_proxy(proxies)
            if proxy:
                os.environ['HTTP_PROXY'] = proxy
                os.environ['HTTPS_PROXY'] = proxy
        
        if choice in ['0', '00']:
            print(Fore.LIGHTBLACK_EX + "\n  Выход из программы..." + RESET_ALL)
            time.sleep(1)
            sys.exit(0)  
        
        LAUNCH_COLOR = Fore.LIGHTRED_EX + Style.BRIGHT
        ERROR_COLOR = Fore.RED
        
        module_map = {
            ('1', '01'): ("Info token", "src/info_token.py"),
            ('2', '02'): ("GuildInfo", "src/guild_info.py"),
            ('3', '03'): ("Scraper", "src/scraper.py"),
            ('4', '04'): ("Invite Creator", "src/invite_creator.py"),
            ('5', '05'): ("GuildJoiner", "src/joiner.py"),
            ('6', '06'): ("GuildLeaver", "src/leaver.py"),
            ('7', '07'): ("RuleAccepter", "src/rule_accepter.py"),
            ('8', '08'): ("ButtonClicker", "src/button_clicker.py"),
            ('9', '09'): ("Onliner", "src/onliner.py"),
            ('10'): ("Spammer", "src/spammer.py"),
            ('11',): ("Spamthreadsall", "src/spam_threads_all.py"),
            ('12',): ("Nick Chooser", "src/nick_chooser.py"),
            ('13',): ("HypeSquadChooser", "src/hype_squad_chooser.py"),
            ('14',): ("Typier", "src/typier.py"),
        }
        
        module_launched = False
        for choices, (name, path) in module_map.items():
            if choice in choices:
                clear_console()
                banner()
                print("\n" + ' ' * ((columns - 30) // 2) + LAUNCH_COLOR + f"⟩⟩ Запуск {name}..." + RESET_ALL)
                time.sleep(0.5)
                clear_console()
                banner()
                os.system(f"python {path}")
                module_launched = True
                break
        
        if not module_launched:
            print("\n" + ' ' * ((columns - 35) // 2) + ERROR_COLOR + "✖ Неверный выбор. Попробуйте снова." + RESET_ALL)
            time.sleep(1.5)

def format_option_line(line, number_color, bullet_color, text_color, border_color):
    """Форматирует строку опции меню с цветами"""
    parts = line.split('║')
    if len(parts) != 3:
        return border_color + line + RESET_ALL
    
    left_border = border_color + '║' + RESET_ALL
    right_border = border_color + '║' + RESET_ALL
    content = parts[1]
    
    colored_content = re.sub(
        r'(\d+)',
        lambda m: number_color + m.group(0) + RESET_ALL + text_color,
        content
    )
    
    colored_content = colored_content.replace('│', bullet_color + '│' + RESET_ALL + text_color)
    
    colored_content = text_color + colored_content + RESET_ALL
    
    return left_border + colored_content + right_border

if __name__ == "__main__":
    tokens_file = 'tokens.txt'
    proxies_file = 'proxies.txt'
    read_tokens_from_file(tokens_file)
    proxies = read_proxies_from_file(proxies_file)
    banner()
    menu()
