from io import BytesIO

import requests
from PIL import Image

HEADERS = {
    'authority': 'eduson.academy',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Tue, 01 Aug 2023 08:54:02 GMT',
    'if-none-match': '"125e4b-601d8b0436a47-gzip"',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "YaBrowser";v="23"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.912 Yowser/2.5 Safari/537.36',
}


def get_image_size_in_pixels(url: str):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    width, height = image.size

    return width, height


def healthcheck_url(url: str):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return True
