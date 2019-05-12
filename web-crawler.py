import asyncio
import aiohttp
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import time


class Limiter:
    def __init__(self, rps):
        self.count = 0
        self.rps = rps
        self.start = datetime.now()

    async def __aenter__(self):
        print(self.count)
        if self.count == 0:
            self.start = datetime.now()

        self.count = self.count + 1
        timer = (datetime.now() - self.start).total_seconds()

        if self.count == self.rps and timer < 1:
            time.sleep(1 - timer)
            self.count = 0
            print(f"Сплю {1-timer}")

        elif timer >= 1:
            self.count = 0

    async def __aexit__(self, *args):
        pass


async def fetch_url(session, queue, unique_url, es, limit, error_log):
    while True:
        url = await queue.get()
        print("Беру")
        async with limit:
            try:
                async with session.get(url) as response:

                    data = await response.read()
                    html = BeautifulSoup(data, 'html.parser')

                    for link in html.find_all('a') + html.find_all('link'):
                        link = urljoin(url, link.get('href'))
                        if link.startswith('https://docs.python.org/') and link not in unique_url.keys():
                            queue.put_nowait(link)
                            print("Кладу найденные url")

                    unique_url[url] = datetime.now()
                    es.index(index="crawler", doc_type='info', body={
                        'site': url,
                        'texts': html.get_text(),
                        'timestamp': unique_url[url]
                    })
                    print("Кладу текст")
            except Exception:
                error_log[url] = datetime.now()



async def main():
    url = 'https://docs.python.org/'
    tasks = list()
    unique_url = dict(url=str(datetime.now()))
    queue = asyncio.Queue()
    es = Elasticsearch()
    limit = Limiter(10)
    error_log = {}
    queue.put_nowait(url)

    async with aiohttp.ClientSession() as session:
        for i in range(15):
            task = asyncio.create_task(fetch_url(session, queue, unique_url, es, limit, error_log))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())