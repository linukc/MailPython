import asyncio
import aiohttp
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime


async def fetch_url(session, queue, unique_url, es, semaphore):
    while True:
        url = await queue.get()

        async with session.get(url) as response:
            data = await response.read()
            await semaphore.acquire()
            html = BeautifulSoup(data, 'html.parser')

            for link in html.find_all('a') + html.find_all('link'):
                link = urljoin(url, link.get('href'))
                if link.startswith('https://docs.python.org/') and link not in unique_url.keys():
                    queue.put_nowait(link)

            unique_url[url] = datetime.now()
            es.index(index="crawler", doc_type='info', body={
                'site': url,
                'texts': html.get_text(),
                'timestamp': unique_url[url]
            })
        semaphore.release()


async def main(rps):
    url = 'https://docs.python.org/'
    tasks = list()
    unique_url = dict(url=str(datetime.now()))
    queue = asyncio.Queue()
    es = Elasticsearch()
    semaphore = asyncio.Semaphore(value=rps)

    queue.put_nowait(url)
    async with aiohttp.ClientSession() as session:
        for i in range(100):
            task = asyncio.create_task(fetch_url(session, queue, unique_url, es, semaphore))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(10))
