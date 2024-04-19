import json

import requests

import config
import libs.kinopoisk as KP

kp = KP.KP()
kp.api_key = config.KINOPOISK_API_KEY


# Нормалиировка текста
def normalize(text):
    # trim, to lower, replace
    text = text.strip().lower().replace("ё", "е")
    return text


def get_search_data(search_query: str):
    kp_data = KP.Search().search_by_keyword(search_query)["films"]

    tv_series = []
    films = []
    others = []
    used_ids = []

    for i in range(len(kp_data)):
        # if nameRu is set
        if "nameRu" in kp_data[i]:
            find_title = normalize(kp_data[i]["nameRu"]).find(normalize(search_query))

            if find_title != -1:
                year = kp_data[i]["year"] if "year" in kp_data[i] else ""
                poster = kp_data[i]["posterUrl"] if "posterUrl" in kp_data[i] else ""
                print(poster)

                if kp_data[i]["filmId"] not in used_ids:
                    if kp_data[i]["type"] == "FILM":
                        films.append(
                            {
                                "id": kp_data[i]["filmId"],
                                "title": kp_data[i]["nameRu"],
                                "type": "Фильм",
                                "date": year,
                                "image": poster,
                            }
                        )
                    elif kp_data[i]["type"] == "TV_SERIES":
                        tv_series.append(
                            {
                                "id": kp_data[i]["filmId"],
                                "title": kp_data[i]["nameRu"],
                                "type": "Сериал",
                                "date": year,
                                "image": poster,
                            }
                        )
                    else:
                        if kp_data[i]["type"] == "MINI_SERIES":
                            ctype = "Мини-сериал"
                        else:
                            ctype = kp_data[i]["type"]
                        others
                        films.append(
                            {
                                "id": kp_data[i]["filmId"],
                                "title": kp_data[i]["nameRu"],
                                "type": ctype,
                                "date": year,
                                "image": poster,
                            }
                        )
                    used_ids.append(kp_data[i]["filmId"])
    others = sorted(others, key=lambda x: x["date"], reverse=True)
    return (films, tv_series, others)


def get_details_info(kp_id: str):
    data = KP.Search().get_details(int(kp_id))

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


def get_player_iframe(kp_id: str):
    data = requests.get(f"https://kinobox.tv/api/players?kinopoisk={kp_id}").json()
    return (data, json.dumps(data))


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
