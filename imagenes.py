from bing_image_downloader import downloader

import requests
from typing import Literal
import random

# city = "Sevilla"
# downloader.download(city,limit=1, output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60,)

# datosObtenidos = requests.get("https://api.unsplash.com/search/photos/?client_id=66cbsBHVCNy3Jko1NVoZAPg9b6_r3VUwsE3JjWvQzEo&query=Burgos")
# datosFormatonJSON = datosObtenidos.json()
# info = datosFormatonJSON.get("urls")


# print(info)


def get_imagen(
    city, size: Literal["Small", "Medium", "Large", "Wallpaper", "All"] = "Medium"
):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17"
    }
    q = city
    res = requests.get(
        f"https://search.brave.com/api/images?q={q}&source=web&size={size}&_type=Photo",
        headers=headers,
    )

    results = res.json()["results"]

    random_index = random.randint(0, 10)
    image = results[random_index]
    props = image["properties"]
    url, cached, thumb = props["url"], props["resized"], image["thumbnail"]["src"]

    print(url)


get_imagen("Burgos")
