import asyncio

import aiohttp as aiohttp

from download import download_data


async def main():
    print("Starting the application")

    async with aiohttp.ClientSession() as session:
        await download_data(session)

    print("Finished downloading")


loop = asyncio.get_event_loop()
asyncio.run(main())
loop.run_forever()
loop.close()
