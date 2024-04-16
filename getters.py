import json

import requests

import config
from cache import Cache


def get_url_data(url: str, headers: dict = None, session=None):
    return requests.get(url, headers=headers).text


def is_serial(iframe_url: str) -> bool:
    return True if iframe_url[iframe_url.find(".info/") + 6] == "s" else False


def is_video(iframe_url: str) -> bool:
    return True if iframe_url[iframe_url.find(".info/") + 6] == "v" else False


def get_serial_seasons(kp_id: str) -> dict:
    data = requests.get(
        config.API + "/tvseries/seasons", params={"kp_id": kp_id, "player": "all"}
    ).json()

    return data
    # return {"series_count": 10, "translations": [{"id": "0", "name": "Дубляж"}]}


def get_movie_links(kp_id: str):
    data = requests.get(
        config.API + "/movie/videos",
        params={"kp_id": kp_id, "player": "all"},
    ).json()

    return json.dumps(data)


def get_download_link_tv(
    kp_id: str, balancer: str, translation_name: str, season_num: int, seria_num: int
):
    data = requests.get(
        config.API + "/tvseries/videos?&season=1&series=1",
        params={
            "kp_id": kp_id,
            "player": balancer,
            "season": season_num,
            "series": seria_num,
        },
    ).json()

    # print all input data
    print(f"kp_id: {kp_id}")
    print(f"translation_name: {translation_name}")
    print(f"season_num: {season_num}")
    print(f"seria_num: {seria_num}")
    return "http://test.com/test"


def get_search_data(search_query: str, ch: Cache = None):
    data = requests.get(config.API + "/search", params={"query": search_query}).json()
    tv_series = []
    films = []
    others = []
    used_ids = []
    for item in data["results"]:
        if "kp_id" in item.keys() and item["kp_id"] not in used_ids:
            if item["type"] == "FILM":
                films.append(
                    {
                        "id": item["kp_id"],
                        "title": item["title"],
                        "type": "Фильм",
                        "date": item["year"],
                        "image": item["poster"],
                    }
                )
            elif item["type"] == "TV_SERIES":
                tv_series.append(
                    {
                        "id": item["kp_id"],
                        "title": item["title"],
                        "type": "Сериал",
                        "date": item["year"],
                        "image": item["poster"],
                    }
                )
            else:
                if item["type"] == "MINI_SERIES":
                    ctype = "Мини-сериал"
                else:
                    ctype = item["type"]
                others.append(
                    {
                        "id": item["kp_id"],
                        "title": item["title"],
                        "type": ctype,
                        "date": item["year"],
                        "image": item["poster"],
                    }
                )
            used_ids.append(item["kp_id"])
    others = sorted(others, key=lambda x: x["date"], reverse=True)

    return (films, tv_series, others)


def get_details_info(kp_id: str):
    data = requests.get(config.API + "/details", params={"kp_id": kp_id}).json()

    if data["type"] == "FILM":
        dtype = "Фильм"
    elif data["type"] == "TV_SERIES":
        dtype = "Сериал"
    else:
        dtype = data["type"]

    return {
        "title": data["nameRu"],
        "image": data["posterUrl"],
        "type": dtype,
        "year": data["year"],
        "description": data["description"],
        "leight": convert_min_to_str(data["filmLength"]),
        "genres": convert_array_to_str(data["genres"]),
        "countries": convert_array_to_str(data["countries"]),
        "imdbRating": data["ratingImdb"],
    }


def convert_min_to_str(min: int) -> str:
    # convert to 2h 30min
    h = int(min / 60)
    m = min % 60
    str = f"{h}h {m}min" if h > 0 else f"{m}min"
    return str


def convert_array_to_str(array: list) -> str:
    if not array:
        return ""

    result = []
    for item in array:
        key = next(iter(item.keys()))
        result.append(item[key].title())

    return ", ".join(result)
