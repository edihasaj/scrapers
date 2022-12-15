import asyncio
import logging

from download import download_data

logging.basicConfig(level=logging.DEBUG)


async def main():
    logging.info('Starting the application')
    await download_data()
    logging.info('Finished downloading')


loop = asyncio.get_event_loop()
asyncio.run(main())
loop.run_forever()
loop.close()
