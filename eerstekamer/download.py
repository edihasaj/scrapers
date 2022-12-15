import logging
import os.path
import subprocess
import time
from os.path import exists

from bs4 import BeautifulSoup
from selenium import webdriver

logging.basicConfig(level=logging.DEBUG)
domain = "https://www.eerstekamer.nl"
archive_url = f"{domain}/verslag_debat_gemist?from=2006-01-01&to=2022-08-01"
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument("start-maximized")
driver = webdriver.Chrome("C:\\Users\\ediha\\chromedriver.exe", chrome_options=options)
CHUNK_SIZE = 1024 * 1024
SAVE_PATH = "C:\\Users\\ediha\\AppData\\Local\\Temp\\scriptix\\"


async def download_data():
    logging.info("Checking if path exists")
    if not os.path.exists(SAVE_PATH):
        os.mkdir(SAVE_PATH)

    logging.info("starting search and download")
    next_page = scrape_data(archive_url)
    while next_page:
        next_page = scrape_data(next_page)


def scrape_data(url):
    logging.info('loading page and getting links')

    links = []
    driver.get(url)
    time.sleep(1)

    links = get_links(links, driver.page_source)
    logging.info(f"found {len(links)} links")

    for link in links:
        logging.info(f"loading {link}")
        driver.get(link)
        time.sleep(1)

        video_link = get_video_link(driver.page_source)

        logging.info(f"link loaded {video_link}, downloading text")
        download_text_data(driver.page_source, link.split('/')[-2])

        logging.info(f"downloading audio {video_link}")
        download_audio_file(video_link, link.split('/')[-2])
        logging.info(f"finished {link}")

    logging.info('finished links, getting next page')
    next_page = get_next_page(driver.page_source)
    driver.quit()
    return next_page


def get_next_page(page_source: str):
    soup = BeautifulSoup(page_source, 'lxml')
    spans = soup.findAll('span')
    span_list = []

    for span in spans:
        if span.text == 'volgende':
            span_list.append(span['href'])

    if len(span_list) <= 0:
        logging.info('no next page')
        return

    return span_list[0]


def get_links(current_list: [str], page_source: str):
    soup = BeautifulSoup(page_source, 'lxml')
    links = soup.findAll('a', href=True)

    link_response_list = [domain + link['href'] for link in links if
                          link['href'].startswith('/verslag/') and link['href'] not in current_list]

    return link_response_list


def get_video_link(page_source: str):
    soup = BeautifulSoup(page_source, 'lxml')
    links = soup.findAll('a', href=True)
    link_list = []

    for link in links:
        if link['href'].startswith('https://login.spotr.media/eerstekamer/'):
            link_list.append(link['href'])

    if len(link_list) <= 0:
        logging.info('no video link')
        return

    return link_list[0]


def download_text_data(page_source: str, file_name: str):
    text = extract_text(page_source)
    if not text:
        logging.info('no text found')
        return

    if exists(f"{SAVE_PATH}{file_name}.txt"):
        logging.info(f"skipping {file_name}.txt as it exists")
        return

    with open(f"{SAVE_PATH}{file_name}.txt", "w", encoding="utf-8") as f:
        f.write(text)
        f.close()


def extract_text(page_source: str):
    soup = BeautifulSoup(page_source, 'lxml')
    main_content = soup.find('div', {"id": "main_content_wrapper"})
    return main_content.text


def download_audio_file(url: str, file_name: str):
    if not url:
        return

    if exists(f"{SAVE_PATH}{file_name}.mp3"):
        logging.info(f"skipping {file_name}.mp3 as it exists")
        return

    try:
        subprocess.check_output(
            ["C:\\Users\\ediha\\ffmpeg\\ffmpeg.exe", "-i", url, "-q:a", "0", "-map", "a",
             f"{SAVE_PATH}{file_name}.mp3"])
    except Exception as e:
        logging.error('Error with Img cmd tool {0}'.format(e))
