from googlesearch import search
import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style, init
from tqdm import tqdm
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

FILE_EXTENSIONS = ['.txt', '.csv', '.html', '.json', '.js', '.php', '.pdf', '.zip', '.doc', '.sql']

def create_download_folder(base_url):
    domain = urlparse(base_url).netloc
    folder_path = os.path.join('downloads', domain)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_file(url, folder_path):
    try:
        response = requests.get(url, stream=True, verify=False)
        if response.status_code == 200:
            filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))
            file_size = int(response.headers.get('content-length', 0))

            with open(filename, 'wb') as file, tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                desc=f"{Fore.CYAN}Mengunduh{Style.RESET_ALL} {os.path.basename(filename)}",
                colour='green'
            ) as progress_bar:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

            print(f"{Fore.GREEN}✔ File berhasil diunduh: {filename}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Gagal mengunduh file: {url}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Error: {e}{Style.RESET_ALL}")

def scrape_website(base_url):
    folder_path = create_download_folder(base_url)
    try:
        response = requests.get(base_url, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        found_files = False

        for link in links:
            file_url = urljoin(base_url, link['href'])

            if any(file_url.endswith(ext) for ext in FILE_EXTENSIONS):
                download_file(file_url, folder_path)
                found_files = True

            elif file_url.endswith('/') and 'Parent Directory' not in link.text:
                print(f"{Fore.YELLOW}📂 Menelusuri folder: {file_url}{Style.RESET_ALL}")
                scrape_website(file_url)

        if not found_files:
            print(f"{Fore.YELLOW}⚠️ Tidak ada file yang ditemukan di situs ini.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}⚠️ Gagal mengakses situs: {e}{Style.RESET_ALL}")

def search_dork(target):
    print(f"{Fore.CYAN}🔎 Mencari menggunakan Google Dork...{Style.RESET_ALL}")
    queries = [
        f"site:{target} index of /",
        f"site:*.{target} index of /"
    ]
    urls = []
    
    for query in queries:
        urls.extend(list(search(query, num_results=10)))
    
    return urls

print(f"{Fore.CYAN}🔍 Masukkan URL target: {Style.RESET_ALL}")
target_url = input("➡️  ")

index_links = search_dork(target_url)

if index_links:
    print(f"{Fore.GREEN}✅ Dork berhasil menemukan {len(index_links)} hasil. Memulai unduhan...{Style.RESET_ALL}")
    for link in index_links:
        scrape_website(link)
else:
    print(f"{Fore.RED}❌ Tidak ada hasil ditemukan dengan Dork untuk: {target_url}{Style.RESET_ALL}")
