import logging
import os
import pathlib
import random
import re
import shutil
import urllib.parse
from typing import List, Final

import click
import js2py
from bs4 import BeautifulSoup

LOCAL_URL: Final = "http://localhost:63342"
GITHUB_URL: Final = "https://gareevaalice.github.io"
CHARACTERS: Final = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
KEY_LENGTH: Final = 16


def get_random_key() -> str:
    rand = random.SystemRandom()
    return "".join(rand.choice(CHARACTERS) for _ in range(KEY_LENGTH))


def validate_key(ctx, param, value):
    if value is not None:
        for k in value.strip():
            if k not in CHARACTERS:
                raise click.BadParameter(
                    f"Key must contain only {CHARACTERS} characters."
                )
        if len(value.strip()) != 16:
            raise click.BadParameter(
                f"Key must have a length of {KEY_LENGTH} characters."
            )
    return value


def get_all_files(original_path: str) -> List[str]:
    logging.info(f"Load all files from directory {original_path}")
    all_files = []
    for root, _, files in os.walk(pathlib.Path(original_path)):
        for filename in files:
            all_files.append(os.path.join(root, filename).replace("\\", "/"))
    return all_files


def encrypt_html(original_filename: str, key: str) -> str:
    def insert_script(js_src: str):
        script_tag = soup.new_tag("script")
        script_tag["src"] = js_src
        soup.html.insert(len(soup.html.contents), script_tag)

    with open(original_filename, "r", encoding="ISO-8859-1") as original_page:
        soup = BeautifulSoup(original_page.read(), "html.parser")
        original_title = soup.title.get_text()
        original_body = soup.body.decode_contents()

    _, tempfile = js2py.run_file("./js/CryptoJS.js")

    encrypted_title = tempfile.encrypt(original_title, key)
    soup.title.string.replace_with(encrypted_title)

    encrypted_body = soup.new_tag("body")
    encrypted_body.string = tempfile.encrypt(original_body, key)
    soup.body.replace_with(encrypted_body)

    insert_script("../../js/CryptoJS.js")
    insert_script("../../js/decode_page.js")

    return str(soup)


def add_links(filename: str, key: str) -> None:
    def link(url: str) -> str:
        params = urllib.parse.urlencode({"key": key})
        return f"{url}/blog/{filename}?{params}\n"

    logging.info(f"Add html links")
    with open("LINKS.txt", "a") as file_object:
        local_link = link(LOCAL_URL)
        github_link = link(GITHUB_URL)
        logging.info(
            f"---------------------------\n"
            f"LOCAL LINK: {local_link}"
            f"GITHUB LINK: {github_link}"
            f"---------------------------\n"
        )
        file_object.write(local_link)
        file_object.write(github_link)
        file_object.write("---------------------------\n")


def create_file(filename: str, inputs: str) -> None:
    logging.info(f"Create file {filename}")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(inputs)


def copy_file(original_filename: str, filename: str) -> None:
    logging.info(f"Copy file to {filename}")
    shutil.copyfile(original_filename, filename)


@click.command()
@click.option(
    "--path",
    required=True,
    help="Path to dir in original_pages/",
)
@click.option(
    "--key",
    default=get_random_key(),
    callback=validate_key,
    help="Key for encryption. Random generated if null."
)
def main(path: str, key: str) -> None:
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        level=logging.DEBUG
    )
    original_path = os.path.join("original_pages", path).replace("\\", "/")
    for original_filename in get_all_files(original_path):
        filename = re.sub(r"^original_", "", original_filename)
        if original_filename.endswith(".html"):
            logging.info(f"Found html file {original_filename} - encrypt it")
            encrypted_html = encrypt_html(original_filename, key)
            create_file(filename, encrypted_html)
            add_links(filename, key)
        else:
            logging.info(f"Found non html file {original_filename} - copy it")
            copy_file(original_filename, filename)


if __name__ == "__main__":
    main()
