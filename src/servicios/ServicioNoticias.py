import requests
import random
import json
from ..utils import relative_to


def load_file_json_news():
    noticias_path = relative_to(__file__,"../noticias.json")
    with open(noticias_path, "r") as fp:
        data = json.load(fp)
        return data


def save_file_json_news(my_dict):
    noticias_path = relative_to(__file__,"../noticias.json")
    with open(noticias_path, "w") as fp:
        json.dump(my_dict, fp)


def get_imagen(city):
    url = "https://bing-image-search1.p.rapidapi.com/images/search"
    count = 4
    params = {"q": city, "count": count, "mkt": "es-ES"}

    headers = {
        "X-RapidAPI-Key": "275bb62fcfmshe06f494e237a78cp174832jsn0dbb9c290237",
        "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=params)

    data = response.json()

    results = data["value"]

    index = random.randint(0, count - 1)
    img = results[index]

    return img["contentUrl"], img["thumbnailUrl"]


def NoticiasApi():
    API_KEY = "pub_7421c00b07c3b0a1ab68df5be83ae037be9f"
    datosObtenidos = requests.get(
        "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news&language=es&country=es"
    )
    datosFormatonJSON = datosObtenidos.json()

    if (not "totalResults" in datosFormatonJSON) or int(
        datosFormatonJSON.get("totalResults")
    ) <= 5:
        datosFormatonJSON = load_file_json_news()
    else:
        save_file_json_news(datosFormatonJSON)

    return datosFormatonJSON.get("results")