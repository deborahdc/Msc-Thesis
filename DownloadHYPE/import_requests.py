import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
from tqdm import tqdm

base_url = 'http://exporter.nsc.liu.se/0648b52567ab455fb9f6d4e290a5df0f/'

def get_links(url):
    print(f"Fetching links from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('?') and not href.startswith('Parent Directory'):
            links.append(href)
    return links

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    local_filename = os.path.join(dest_folder, os.path.basename(url))
    print(f"Downloading {url} to {local_filename}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        with open(local_filename, 'wb') as f, tqdm(
            desc=local_filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
    print(f"Downloaded {local_filename}")

def download_all_files(base_url, current_url, dest_folder, visited_urls):
    print(f"Processing directory {current_url}")
    if current_url in visited_urls:
        return
    visited_urls.add(current_url)

    links = get_links(current_url)
    for link in links:
        full_url = urljoin(current_url, link)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:  # Ensure we stay within the same domain
            if full_url.endswith('/'):
                new_dest_folder = os.path.join(dest_folder, link.strip('/'))
                download_all_files(base_url, full_url, new_dest_folder, visited_urls)
            else:
                download_file(full_url, dest_folder)

# Initialize the set to keep track of visited URLs
visited_urls = set()
# Start downloading all files
download_all_files(base_url, base_url, './downloaded_data', visited_urls)
