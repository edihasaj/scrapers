import logging
import os.path
import subprocess
from os.path import exists

import aiohttp

from get_video_links import get_links_for_download

logging.basicConfig(level=logging.DEBUG)
CHUNK_SIZE = 1024 * 1024
SAVE_PATH = "/data/tweedekamer/content/"
domain = "https://debatgemist.tweedekamer.nl"
debates_archive_url = f"{domain}/debatten"


async def download_data(session: aiohttp.ClientSession):
    logging.info("Checking if path exists")
    if not os.path.exists(SAVE_PATH):
        os.mkdir(SAVE_PATH)

    logging.info("getting the download links")
    links = get_links_for_download()

    logging.info("downloading the files")
    for item in links:
        if 'video' in item:
            file_name = item['video'][-19:-4]
        else:
            file_name = item['transcript'][-19:-4]

        if 'video' in item:
            download_video_file(item['video'], file_name)
        if 'transcript' in item:
            await download_transcript_file(session, item['transcript'], item['link'], file_name)

    return links


def download_video_file(url: str, file_name: str):
    if exists(f"{SAVE_PATH}{file_name}.mp3"):
        logging.info(f"skipping {file_name}.mp3")
        return

    try:
        subprocess.check_output(
            ["ffmpeg", "-i", url, "-q:a", "0", "-map", "a", f"{SAVE_PATH}{file_name}.mp3"])
    except Exception as e:
        logging.error('Error with Img cmd tool {0}'.format(e))


async def download_transcript_file(session: aiohttp.ClientSession, url: str, page: str,
                                   file_name: str):
    if exists(f"{SAVE_PATH}{file_name}.txt"):
        logging.info(f"skipping {file_name}.txt")
        return

    form_data = aiohttp.FormData()
    form_data.add_field("debate_file_options", url)
    form_data.add_field("op", "download")
    form_data.add_field("form_id", "debatgemist_download_video_form")

    async with session.post(page, data=form_data) as response:
        logging.info(f"writing {file_name}.txt")
        with open(f"{SAVE_PATH}{file_name}.txt", 'wb') as outfile:
            async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                outfile.write(chunk)
        logging.info(f"done writing {file_name}.txt")
