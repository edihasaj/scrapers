import logging

import asyncio

import aiohttp as aiohttp

from download import download_data

logging.basicConfig(level=logging.DEBUG)


async def main():
    logging.info('Starting the application')

    async with aiohttp.ClientSession() as session:
        await download_data(session)

    logging.info('Finished downloading')


loop = asyncio.get_event_loop()
asyncio.run(main())
loop.run_forever()
loop.close()
