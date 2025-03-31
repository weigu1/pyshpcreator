#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Check links in local homepage directory

import os
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep

class CheckLinks:
    """ Check links in local homepage directory """
    def __init__(self, local_directory):
        self.local_directory = local_directory
        self.headers = {  # Headers to mimic a browser request
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com',
            'DNT': '1',  # Do Not Track Request Header
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

    def fetch_url(self, url, retries=3, backoff_factor=0.3):
        """Fetch a URL with retries and exponential backoff."""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=5)
                return response
            except requests.RequestException as e:
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    print(f"Retrying in {sleep_time} seconds for URL: {url} due to error: {e}")
                    sleep(sleep_time)
                else:
                    print(f"Failed to fetch URL: {url} after {retries} attempts due to error: {e}")
                    raise e

    def check_links(self):
        """Check all links in local HTML files, report their status and save to file."""
        csv_file = "broken_links_in" + self.local_directory.replace("/", "_") + ".csv"
        broken_links = []
        text = f"Checking links in all HTML files in folder {self.local_directory}"
        "\nThis may take some time!"
        print(text)
        nr_of_files = 0
        for root, dirs, files in os.walk(self.local_directory):
            nr_of_files = nr_of_files + len(files)
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
                                    code = self.fetch_url(url).status_code
                                    if code >= 400:
                                        broken_links.append((file_path, url, code))
                                        text = f"{file_path}\t{url}\t{code}"
                                        print(text)
                                except requests.RequestException as e:
                                    broken_links.append((file_path, url, e))
                                    text = f"{file_path}\t{url} - Error: {e}"
                                    print(text)
                            else:                                        # Handle local file paths
                                local_link_path = os.path.join(root, url)
                                if not os.path.exists(local_link_path):
                                    if not "#link" in local_link_path:
                                        broken_links.append((file_path, local_link_path, "-"))
                                        text = f"{file_path}\t{local_link_path}"
                                        print(text)
        if broken_links:
            text = "Broken links found:\n\n" + "\n".join([f"{file}\t{url}\t{code}" for file, url, code in broken_links])
            text += f"\n\nFinished checking links in {nr_of_files} files!"
            # Save a file in the pyshpcreator directory
            with open(csv_file, "w") as broken_links_file:
                broken_links_file.write(text)
            text += f"\n\nThe result is in a csv-file in the working folder: {csv_file}"
            print(text)
        else:
            text = "No broken links found."
            print(text)
        return text

### main ####
def main():
    """setup and start mainloop"""
    print ('Argument list: ', sys.argv)
    local_directory = "/savit/www.weigu/other_projects/"
    if len(sys.argv) == 2:
        local_directory = sys.argv[1]

    cl = CheckLinks(local_directory)
    cl.check_links()

if __name__ == '__main__':
    main()

