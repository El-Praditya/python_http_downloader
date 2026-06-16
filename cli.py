#!/usr/bin/env python3

import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

visited = set()
downloaded = 0
failed = 0

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_root_folder_name(url):
    path = urlparse(url).path.rstrip("/")

    if not path:
        return "download"

    return os.path.basename(path)


def is_directory_link(href):
    return href.endswith("/")


def download_file(url, local_path):
    global downloaded, failed

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        with requests.get(
            url,
            stream=True,
            headers=HEADERS,
            timeout=20
        ) as r:

            status = r.status_code

            if status != 200:
                print(
                    f"{RED}[{status} FAILED]{RESET} {url}"
                )
                failed += 1
                return

            with open(local_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            print(
                f"{GREEN}[{status} SUCCEED]{RESET} {url}"
            )

            downloaded += 1

    except Exception as e:
        print(
            f"{RED}[ERROR]{RESET} {url} -> {e}"
        )
        failed += 1


def crawl(url, root_url, output_dir):
    if url in visited:
        return

    visited.add(url)

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        r.raise_for_status()

    except Exception as e:
        print(
            f"{RED}[CRAWL ERROR]{RESET} {url} -> {e}"
        )
        return

    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href")

        if not href:
            continue

        if href in ("../", "/"):
            continue

        full_url = urljoin(url, href)

        if not full_url.startswith(root_url):
            continue

        rel_path = unquote(
            urlparse(full_url).path[
                len(urlparse(root_url).path):
            ]
        )

        local_path = os.path.join(
            output_dir,
            rel_path.lstrip("/")
        )

        if is_directory_link(href):
            crawl(
                full_url,
                root_url,
                output_dir
            )
        else:
            download_file(
                full_url,
                local_path
            )


def main():
    parser = argparse.ArgumentParser(
        description="Recursive HTTP Downloader"
    )

    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="Target URL"
    )

    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="Download location"
    )

    args = parser.parse_args()

    root_url = args.url.rstrip("/") + "/"

    folder_name = get_root_folder_name(args.url)

    final_output = os.path.join(
        args.path,
        folder_name
    )

    os.makedirs(final_output, exist_ok=True)

    print(
        f"{CYAN}[*] Target : {root_url}{RESET}"
    )
    print(
        f"{CYAN}[*] Save To: {final_output}{RESET}"
    )
    print()

    crawl(
        root_url,
        root_url,
        final_output
    )

    print("\n" + "=" * 50)
    print(
        f"{GREEN}Downloaded : {downloaded}{RESET}"
    )
    print(
        f"{RED}Failed     : {failed}{RESET}"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()
