import configparser
import logging
import pyperclip

from parsers import descargasdd_parser

from rich import print

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("configuration/config.ini", 'UTF-8')
    series = configparser.ConfigParser()
    series.read("configuration/series.ini", 'UTF-8')

    logging.basicConfig(level=logging.DEBUG,
                        filename=config['Logging']['file_path'] + config['Logging']['file_name'],
                        filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    download_links: list[str] = descargasdd_parser.descargasdd_scrape(config, series)

    if download_links:
        print(f'[bold green]Links[/bold green]: {download_links}')
        logging.info(f'Links: {download_links}')
        pyperclip.copy(download_links.__str__())

