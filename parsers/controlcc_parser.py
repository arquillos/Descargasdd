import logging

from bs4 import BeautifulSoup
import requests


def controlcc_scrape(url: str) -> list[str]:
    # 1. Get the initial control_cc code (it redirects to another controlcc page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    logging.debug(f'Control cc Soup: {soup}')
    final_link = soup.find(id="pasteFrame").get("src")
    logging.info(f'Final link to control_cc: {final_link}')

    # 2. Get the actual control_cc page
    response = requests.get(final_link)
    soup = BeautifulSoup(response.content, "html.parser")
    logging.debug(f'Control cc final Soup: {soup}')
    links = soup.find(id="thepaste").text
    logging.info(f'Links: {links}')

    # 3. Get the wetransfer links
    wetl_links = list(filter(lambda link: link.startswith('https://we.tl'), links.splitlines()))
    logging.info(f'we.tl links: {wetl_links}')
    return wetl_links
