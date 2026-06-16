import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

visited = set()


def is_directory_link(href):
    return href.endswith('/')


def download_file(url, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    print(f"Downloading: {url}")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def crawl(url, root_url, output_dir):
    if url in visited:
        return

    visited.add(url)

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href")

        if not href:
            continue

        if href in ["../", "/"]:
            continue

        full_url = urljoin(url, href)

        if not full_url.startswith(root_url):
            continue

        rel_path = unquote(
            urlparse(full_url).path[len(urlparse(root_url).path):]
        )

        local_path = os.path.join(output_dir, rel_path.lstrip("/"))

        if is_directory_link(href):
            crawl(full_url, root_url, output_dir)
        else:
            try:
                download_file(full_url, local_path)
            except Exception as e:
                print(f"Failed: {full_url} -> {e}")


def main():
    root_url = input("URL yang mau didownload: ").strip()
    output_dir = input("Folder tujuan download: ").strip()

    if not root_url.endswith("/"):
        root_url += "/"

    os.makedirs(output_dir, exist_ok=True)

    crawl(root_url, root_url, output_dir)

    print("\nSelesai.")


if __name__ == "__main__":
    main()
