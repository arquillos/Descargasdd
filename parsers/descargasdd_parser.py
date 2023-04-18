import hashlib
import logging

from bs4 import BeautifulSoup
import configparser
import requests

from rich import print

from parsers import controlcc_parser


def get_ethan_controlcc_link(episode: int, enlaces: str) -> str:
    # Parse the links code from eth@n user posts
    # Example (código):
    # Episodio 1
    # https://controlc.com/c0152470ç
    # https://www.keeplinks.org/p15/6397c3333f45e
    episode_number = 'Episodio ' + str(episode)
    return enlaces.split(episode_number)[1].replace('\r', '').split('\n')[1]


def get_bryan_122_controlcc_link(episode: int, season: str, enlaces: str) -> str:
    # Parse the links code from Bryan_122@n user posts
    # Example (código):
    # 3x01 - Más cerca
    #
    # https://www.keeplinks.org/p63/6412d397757b7
    # https://controlc.com/a07ac639
    # http://safelinking.com/HqZ4iNQ3x01
    episode_prefix: str = 'x0' if episode < 10 else 'x'
    episode_number = season + episode_prefix + str(episode)
    return enlaces.split(episode_number + ' - ')[1].split('\n')[3]


def get_control_cc_link_from_textbox(soup, tv_programs: configparser.ConfigParser, section: str) -> (str, int):
    enlaces = soup.select(tv_programs[section]['title_selector'])[0].text
    new_episode: int = int(tv_programs[section]["episode"]) + 1
    control_cc_link: str = get_ethan_controlcc_link(new_episode, enlaces) if enlaces.startswith('Episodio') \
        else get_bryan_122_controlcc_link(new_episode, tv_programs[section]['season'], enlaces)

    logging.debug(f'Links to Episode {str(new_episode)}, control cc link: {control_cc_link}')

    return control_cc_link, new_episode


def descargasdd_scrape(config: configparser.ConfigParser, tv_programs: configparser.ConfigParser) -> list[str]:
    username = config['Site']['username']
    password = config['Site']['password']
    url = config['Site']['url'] + config['Site']['login']
    logging.info(f'Username: {username}, Password: {password}, URL: {url}')

    # Login
    logging.info(f'Login into the site')
    with requests.Session() as ss:
        ss.post(url, {
            'vb_login_username': username,
            'vb_login_password': password,
            'vb_login_md5password': hashlib.md5(password.encode()).hexdigest(),
            'vb_login_md5password_utf': hashlib.md5(password.encode("utf-8")).hexdigest(),
            'cookieuser': 1,
            'do': 'login',
            's': '',
            'securitytoken': 'guest'
        })

        logging.info(f'Checking the series')
        episodes_list: list[str] = []
        for section in tv_programs.sections():
            if not tv_programs[section].getboolean('skip'):
                config_title = tv_programs[section]["title"]
                print(f'[bold]TV program[/bold]: {config_title}')
                logging.info(f'TV program: {config_title}')

                # Get th TV program page source
                page = ss.get(tv_programs[section]['url'])
                soup = BeautifulSoup(page.content, "html.parser")
                logging.debug(f'TV program soup: {soup}')

                logging.info(f'Getting the title')
                title = soup.select('#pagetitle > h1 > span')[0].text

                # Check title
                if title == config_title:
                    print(f'\t[bold red]No new episode...[/bold red]')
                    logging.info(f'\tNo new episode...')
                else:
                    print(f'\t[bold green]New episode found[/bold green]:' + title)
                    logging.info(f'\tNew episode found: ' + title)

                    control_cc_link, new_episode = get_control_cc_link_from_textbox(soup, tv_programs, section)
                    episodes: list[str] = controlcc_parser.controlcc_scrape(control_cc_link)

                    print(f'\tEpisode links {str(new_episode)}: {episodes}')
                    logging.info(f'\tEpisode links {str(new_episode)}: {episodes}')
                    episodes_list.extend(episodes)
            else:
                logging.info(f'Skipping series: {config_title}')
        return episodes_list
