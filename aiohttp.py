"""
1. Make aiohttp.ClientSession to pass the coroutine for each url within tasks
	1.1 same effect as using asyncio.get_event_loop().create_task(async_function(arg))
2. Make timer using async_timeout context manager that will exit on timeout
3. Make response object via session.get()
4. Read response content as aiohttp.StreamReader object to allow chunk & write to disk
	4.1 aiofiles can be used to async write to disk
5. Release response StreamReader - don't rely on context manager
"""

import aiohttp
import asyncio
import async_timeout
import os


async def download_coroutine(session, url):
	with async_timeout.timeout(10):
		async with session.get(url) as response:
			filename = os.path.basename(url)
			with open(filename, 'wb') as f_handle:
				while True:
					chunk = await response.content.read(1024)
					if not chunk:
						break
					f_handle.write(chunk)
			return await response.release()


async def main(loop):
	urlz = [
		"http://www.irs.gov/pub/irs-pdf/f1040.pdf",
		"http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
		"http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
		"http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
		"http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"
	]

	async with aiohttp.ClientSession(loop=loop) as session:
		tasks = [download_coroutine(session, url) for url in urlz]
		await asyncio.gather(*tasks)


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main(loop))
