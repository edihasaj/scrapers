import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

domain = "https://debatgemist.tweedekamer.nl"
archive_urls = [f"{domain}/commissievergaderingen", f"{domain}/plenaire-debatten"]
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("chromedriver", chrome_options=options)


def get_links_for_download():
    logging.info('loading page and getting links')
    links = load_page_and_get_links()
    video_links = []

    logging.info('getting links inside the pages')
    for link in links:
        driver.get(link)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        inputs = soup.findAll('input', attrs={'name': 'debate_file_options'})
        video_link = {
            'link': link
        }

        for inputEl in inputs:

            value = inputEl.get('value')
            if 'download_' in value and '.mp4' in value:
                video_link['video'] = value[9:]
            else:
                video_link['transcript'] = value

        video_links.append(video_link)

    logging.info(f"{len(video_links)} links")
    driver.quit()
    return video_links


def load_page_and_get_links():
    video_links = []

    for link in archive_urls:
        load_page = 0
        driver.get(link)
        time.sleep(1)

        while load_page < 100:
            more_buttons = driver.find_elements(By.CLASS_NAME, "btn_show-more-options")
            for x in range(len(more_buttons)):
                if more_buttons[x].is_displayed():
                    driver.execute_script("arguments[0].click();", more_buttons[x])
                    time.sleep(2)

            load_page = load_page + 1

        video_links.extend(get_video_links(video_links, driver.page_source))

    return video_links


def get_video_links(current_list: [str], page_source: str):
    soup = BeautifulSoup(page_source, 'lxml')
    links = soup.findAll('a', href=True)

    video_links = [domain + link['href'] for link in links if
                   link['href'].startswith('/debatten') and link['href'] not in current_list]

    return video_links
