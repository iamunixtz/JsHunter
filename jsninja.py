import requests
import re
import argparse
import json
import signal
import sys
import os
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = r"""
     ____.         _______  .__            __        
    |    | ______  \      \ |__| ____     |__|____   
    |    |/  ___/  /   |   \|  |/    \    |  \__  \  
/\__|    |\___ \  /    |    \  |   |  \   |  |/ __ \_
\________/____  > \____|__  /__|___|  /\__|  (____  /
              \/          \/        \/\______|    \/ 
    """
    
    # Get the terminal width
    terminal_width = os.get_terminal_size().columns
    banner_lines = banner.strip().splitlines()

    # Print the banner with Instagram colors
    for i, line in enumerate(banner_lines):
        if i % 4 == 0:
            color = Fore.MAGENTA  # Purple
        elif i % 4 == 1:
            color = Fore.LIGHTMAGENTA_EX  # Pink
        elif i % 4 == 2:
            color = Fore.YELLOW  # Yellow
        else:
            color = Fore.LIGHTYELLOW_EX  # Orange
        print(color + line.center(terminal_width))

    quote = f"{Fore.CYAN}JSNinja - \"Hunting Bugs in JavaScript!\"{Style.RESET_ALL}"
    print(quote.center(terminal_width))

def extract_links_from_js(js_content):
    url_pattern = r'(https?://[^\s\'"<>]+)'
    return re.findall(url_pattern, js_content)

def extract_secrets(js_content):
    secret_patterns = {
        'AWS Access Key': r'(?i)AWS_Access_Key\s*:\s*[\'"]?([A-Z0-9]{20})[\'"]?',
        'AWS Secret Key': r'(?i)AWS_Secret_Key\s*:\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
        'Stripe Secret Key': r'(?i)Stripe_Secret_Key\s*:\s*[\'"]?([A-Za-z0-9]{24})[\'"]?',
        'GitHub Token': r'(?i)GitHub Token\s*:\s*[\'"]?([A-Za-z0-9]{36})[\'"]?',
        'Facebook Token': r'(?i)Facebook_Token\s*:\s*[\'"]?([A-Za-z0-9\.]+)[\'"]?',
        'Telegram Bot Token': r'(?i)Telegram Bot Token\s*:\s*[\'"]?([A-Za-z0-9:]+)[\'"]?',
        'Google Maps API Key': r'(?i)Google Maps API Key\s*:\s*[\'"]?([A-Za-z0-9_-]+)[\'"]?',
        'Google reCAPTCHA Key': r'(?i)Google reCAPTCHA Key\s*:\s*[\'"]?([A-Za-z0-9_-]+)[\'"]?',
        'API Key': r'(?i)API_Key\s*:\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
        'Secret Key': r'(?i)Secret_Key\s*:\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?',
        'Auth Domain': r'(?i)Auth_Domain\s*:\s*[\'"]?([A-Za-z0-9\-]+\.[a-z]{2,})[\'"]?',
        'Database URL': r'(?i)Database_URL\s*:\s*[\'"]?([^\'" ]+)[\'"]?',
        'Storage Bucket': r'(?i)Storage_Bucket\s*:\s*[\'"]?([^\'" ]+)[\'"]?',
        'Cloud Storage API Key': r'(?i)Cloud Storage API Key\s*:\s*[\'"]?([A-Za-z0-9_-]{32,})[\'"]?'
    }

    found_secrets = {}
    for key, pattern in secret_patterns.items():
        matches = re.findall(pattern, js_content)
        if matches:
            unique_matches = list(set(matches))
            found_secrets[key] = unique_matches

    # Add pattern for object notation
    object_pattern = r'(?i)const\s+[A-Z_]+_KEYS\s*=\s*\{([^}]+)\}'
    object_matches = re.findall(object_pattern, js_content)
    
    for match in object_matches:
        for line in match.split(','):
            line = line.strip()
            for key in secret_patterns.keys():
                if key.lower().replace(' ', '_') in line.lower():
                    value = re.search(r'\:\s*[\'"]?([^\'", ]+)[\'"]?', line)
                    if value:
                        found_secrets[key] = found_secrets.get(key, []) + [value.group(1)]

    return found_secrets


def signal_handler(sig, frame):
    choice = input(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Do you want to close JSNinja? (Y/N): ").strip().lower()
    if choice == 'y':
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Closing JSNinja...")
        sys.exit(0)
    else:
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Continuing execution...")

def main(input_file, output_file, look_for_secrets, look_for_urls, single_url):
    clear_screen()
    print_banner()

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    js_links = []
    if single_url:
        js_links.append(single_url)
    else:
        with open(input_file, 'r') as file:
            js_links = file.readlines()

    extracted_links = []
    all_secrets = {}

    for js_link in js_links:
        js_link = js_link.strip()
        if not js_link:
            continue
        
        try:
            response = requests.get(js_link, verify=False)
            response.raise_for_status()

            if look_for_urls:
                links = extract_links_from_js(response.text)
                extracted_links.extend(links)
                print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Extracted {len(links)} links from {js_link}{Style.RESET_ALL}")

                for link in links:
                    print(f"{Fore.GREEN}[+] {link}{Style.RESET_ALL}")
                if not links:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No URLs found in {js_link}{Style.RESET_ALL}")

            if look_for_secrets:
                secrets = extract_secrets(response.text)
                if secrets:
                    all_secrets[js_link] = secrets
                    print(f"{Fore.GREEN}[+] Secrets found in {js_link}: {json.dumps(secrets, indent=2)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No secrets found in {js_link}{Style.RESET_ALL}")

        except requests.exceptions.SSLError as ssl_err:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} SSL error while fetching {js_link}: {str(ssl_err)}")
        except requests.RequestException as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to fetch {js_link}: {str(e)}")

    if extracted_links and look_for_urls:
        with open(output_file, 'w') as out_file:
            for link in extracted_links:
                out_file.write(link + '\n')
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Links saved to {output_file}{Style.RESET_ALL}")

    if all_secrets and look_for_secrets:
        secrets_output_file = output_file.replace('.txt', '_secrets.json')
        with open(secrets_output_file, 'w') as secrets_file:
            json.dump(all_secrets, secrets_file, indent=2)
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Secrets saved to {secrets_output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)

    parser = argparse.ArgumentParser(description='Extract links and secrets from JavaScript files.')
    parser.add_argument('input_file', nargs='?', help='File containing JavaScript links')
    parser.add_argument('-o', '--output_file', default='extracted_links.txt', help='File to save extracted links')
    parser.add_argument('-u', '--url', help='Single JavaScript URL to fetch')
    parser.add_argument('--secrets', action='store_true', help='Look for secrets in JavaScript content')
    parser.add_argument('--urls', action='store_true', help='Extract URLs from JavaScript content')
    args = parser.parse_args()

    if args.url and args.input_file:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Please provide either an input file or a single URL, not both.")
        sys.exit(1)

    main(args.input_file, args.output_file, args.secrets, args.urls, args.url)
