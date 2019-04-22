import asyncio
import aiohttp
from aioelasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import time


async def fetch_url(str_task, url, session, queue, unique_url):
    while True:
        async with session.get(url) as response:
            data = await response.read()
            soup = BeautifulSoup(data, 'html.parser')

            for link in soup.find_all('a') + soup.find_all('link'):
                link = urljoin(url, link.get('href'))
                if link.startswith('https://docs.python.org/') and link not in unique_url.keys():
                    # print(f"{str_task} Кладу {link}")
                    queue.put_nowait(link)
                    unique_url[link] = str(datetime.now())

            if queue.empty():
                queue.task_done()
                # print('Закончил' + str_task)
            else:
                url = await queue.get()
                # print(f"{str_task} Беру {url}")


async def main(rps):
    url = 'https://docs.python.org/'
    tasks = list()
    unique_url = dict(url=str(datetime.now()))
    queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        for i in range(rps):
            str_task = 'task' + str(i)
            task = asyncio.create_task(fetch_url(str_task, url, session, queue, unique_url))
            tasks.append(task)

        await asyncio.gather(*tasks)
    # print(len(unique_url))

if __name__ == "__main__":
    # start = time.time()
    asyncio.run(main(10))
    # print(start-time.time())
