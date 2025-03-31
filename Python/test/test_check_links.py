import os
import requests
from bs4 import BeautifulSoup
import time

def check_links(local_dir):
    """Check all links in local HTML files, report their status and save to file."""
    csv_file = "broken_links_in_" + local_dir.replace("/", "_") + ".csv"
    broken_links = []
    print("Checking links in local HTML files...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    def fetch_url(url, retries=3, backoff_factor=0.3):
        """Fetch a URL with retries and exponential backoff."""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
                return response
            except requests.RequestException as e:
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    print(f"Retrying in {sleep_time} seconds for URL: {url} due to error: {e}")
                    time.sleep(sleep_time)
                else:
                    print(f"Failed to fetch URL: {url} after {retries} attempts due to error: {e}")
                    raise e

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    links = soup.find_all('a', href=True)
                    for link in links:
                        url = link['href']
                        if url.startswith(('http://', 'https://')):  # Check external links
                            try:
                                code = fetch_url(url).status_code
                                if code >= 400:
                                    broken_links.append((file_path, url, code))
                                    text = f"{file_path}\t{url}\t{code}"
                                    print(text)
                            except requests.RequestException as e:
                                broken_links.append((file_path, url, e))
                                text = f"{file_path}\t{url} - Error: {e}"
                                print(text)
                        else:  # Handle local file paths
                            local_link_path = os.path.join(root, url)
                            if not os.path.exists(local_link_path):
                                if not "#link" in local_link_path:
                                    broken_links.append((file_path, local_link_path, "-"))
                                    text = f"{file_path}\t{local_link_path}"
                                    print(text)
    if broken_links:
        text = "Broken links found:\n" + "\n".join([f"{file}\t{url}\t{code}" for file, url, code in broken_links])  # Changed line
        with open(csv_file, "w") as broken_links_file:
            broken_links_file.write(text)
        text = f"Finished checking links!"
        print(text)
    else:
        text = "No broken links found."
        print(text)

# Example usage
local_dir = "/savit/www.weigu/other_projects/"

check_links(local_dir)

