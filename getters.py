import requests
import json
from bs4 import BeautifulSoup as Soup
from base64 import b64decode
from cache import Cache


def convert_char(char: str):
    low = char.islower()
    alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if char.upper() in alph:
        ch = alph[(alph.index(char.upper()) + 13) % len(alph)]
        if low:
            return ch.lower()
        else:
            return ch
    else:
        return char


def convert(string: str):
    # Декодирование строки со ссылкой
    return "".join(map(convert_char, list(string)))


def get_url_data(url: str, headers: dict = None, session=None):
    return requests.get(url, headers=headers).text


def is_serial(iframe_url: str) -> bool:
    return True if iframe_url[iframe_url.find(".info/") + 6] == "s" else False


def is_video(iframe_url: str) -> bool:
    return True if iframe_url[iframe_url.find(".info/") + 6] == "v" else False


def generate_translations_dict(series_count: int, translations_div: Soup) -> dict:
    """Returns: {'series_count': series_count, 'translations': translations}"""
    if not isinstance(translations_div, Soup) and translations_div != None:
        translations = []
        for translation in translations_div:
            a = {}
            a["id"] = translation["value"]
            a["type"] = translation["data-translation-type"]
            if a["type"] == "voice":
                a["type"] = "Озвучка:  "
            elif a["type"] == "subtitles":
                a["type"] = "Субтитры: "
            a["name"] = translation.text
            translations.append(a)
    else:
        translations = [{"id": "0", "type": "Неизвестно: ", "name": "Неизвестно"}]

    return {"series_count": series_count, "translations": translations}


def get_link_to_serial_info(id: str, id_type: str, token: str):
    if id_type == "kinopoisk":
        serv = f"https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FkinopoiskID%3D{id}&token={token}&kinopoiskID={id}"
    else:
        raise ValueError("Неизвестный тип id")
    return get_url_data(serv)


def get_serial_info(id: str, id_type: str, token: str) -> dict:
    """Returns dict {'series_count': int, 'translations': [{'id': 'str', 'type': 'str', 'name': 'str'}, ...]}
    If series_count == 0, then it's a video (doesn't have series)
    """
    url = get_link_to_serial_info(id, id_type, token)
    url = json.loads(url)
    is_found = url["found"]
    if not is_found:
        raise FileNotFoundError
    else:
        url = url["link"]
        url = "https:" + url
        data = get_url_data(url)
        soup = Soup(data, "lxml")
        if is_serial(url):
            series_count = len(
                soup.find("div", {"class": "serial-series-box"})
                .find("select")
                .find_all("option")
            )
            try:
                translations_div = (
                    soup.find("div", {"class": "serial-translations-box"})
                    .find("select")
                    .find_all("option")
                )
            except:
                translations_div = None
            return generate_translations_dict(series_count, translations_div)
        elif is_video(url):
            series_count = 0
            try:
                translations_div = (
                    soup.find("div", {"class": "movie-translations-box"})
                    .find("select")
                    .find_all("option")
                )
            except AttributeError:
                translations_div = None
            return generate_translations_dict(series_count, translations_div)
        else:
            raise FileNotFoundError("NOT A VIDEO NOR A SERIAL!!!")


def get_download_link(
    id: str, id_type: str, seria_num: int, translation_id: str, token: str
):
    if id_type == "kinopoisk":
        serv = f"https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FkinopoiskID%3D{id}&token={token}&kinopoiskID={id}"
    else:
        raise ValueError("Неизвестный тип id")
    data = get_url_data(serv)
    url = json.loads(data)["link"]
    data = get_url_data("https:" + url)
    soup = Soup(data, "lxml")
    urlParams = data[data.find("urlParams") + 13 :]
    urlParams = json.loads(urlParams[: urlParams.find(";") - 1])
    if translation_id != "0" and seria_num != 0:
        # Обычный сериал (1+ серий)
        container = soup.find("div", {"class": "serial-translations-box"}).find(
            "select"
        )
        media_hash = None
        media_id = None
        for translation in container.find_all("option"):
            if translation.get_attribute_list("data-id")[0] == translation_id:
                media_hash = translation.get_attribute_list("data-media-hash")[0]
                media_id = translation.get_attribute_list("data-media-id")[0]
                break
        url = f"https://kodik.info/serial/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}"
        data = get_url_data(url)
        soup = Soup(data, "lxml")
    elif translation_id != "0" and seria_num == 0:
        # Видео с несколькими переводами
        container = soup.find("div", {"class": "movie-translations-box"}).find("select")
        media_hash = None
        media_id = None
        for translation in container.find_all("option"):
            if translation.get_attribute_list("data-id")[0] == translation_id:
                media_hash = translation.get_attribute_list("data-media-hash")[0]
                media_id = translation.get_attribute_list("data-media-id")[0]
                break
        url = f"https://kodik.info/video/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}"
        data = get_url_data(url)
        soup = Soup(data, "lxml")

    hash_container = soup.find_all("script")[4].text
    video_type = hash_container[hash_container.find(".type = '") + 9 :]
    video_type = video_type[: video_type.find("'")]
    video_hash = hash_container[hash_container.find(".hash = '") + 9 :]
    video_hash = video_hash[: video_hash.find("'")]
    video_id = hash_container[hash_container.find(".id = '") + 7 :]
    video_id = video_id[: video_id.find("'")]

    download_url = str(
        get_download_link_with_data(video_type, video_hash, video_id, urlParams)
    ).replace("https://", "")
    download_url = download_url[2:-26]  # :hls:manifest.m3u8

    return download_url


def get_download_link_with_data(
    video_type: str, video_hash: str, video_id: str, urlParams: dict
):
    params = {
        "hash": video_hash,
        "id": video_id,
        "type": video_type,
        "d": urlParams["d"],
        "d_sign": urlParams["d_sign"],
        "pd": urlParams["pd"],
        "pd_sign": urlParams["pd_sign"],
        "ref": "",
        "ref_sign": urlParams["ref_sign"],
        "bad_user": "true",
        "cdn_is_working": "true",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    post_link = get_post_link()
    data = requests.post(
        f"https://kodik.info{post_link}", data=params, headers=headers
    ).json()
    url = convert(data["links"]["360"][0]["src"])
    try:
        return b64decode(url.encode())
    except:
        return str(b64decode(url.encode() + b"==")).replace("https:", "")


def get_post_link():
    script_url = "https://kodik.info/assets/js/app.player_single.cc7c389aac31dd6a852172d9aa2d04092fb33d6fae18eb5a9fa2756c301ce900.js"
    data = requests.get(script_url).text
    url = data[data.find("$.ajax") + 30 : data.find("cache:!1") - 3]
    return b64decode(url.encode()).decode()


def get_search_data(search_query: str, token: str, ch: Cache = None):
    payload = {"token": token, "title": search_query}
    url = "https://kodikapi.com/search"
    data = requests.post(url, data=payload).json()
    items = []
    others = []
    used_ids = []
    for item in data["results"]:
        if "kinopoisk_id" in item.keys() and item["kinopoisk_id"] not in used_ids:
            if item["type"] == "foreign-movie":
                ctype = "Иностранный фильм"
            elif item["type"] == "foreign-serial":
                ctype = "Иностранный сериал"
            elif item["type"] == "russian-movie":
                ctype = "Русский фильм"
            elif item["type"] == "russian-serial":
                ctype = "Русский сериал"
            else:
                ctype = item["type"]
            others.append(
                {
                    "id": item["kinopoisk_id"],
                    "title": item["title"],
                    "type": ctype,
                    "date": item["year"],
                }
            )
            used_ids.append(item["kinopoisk_id"])

    others = sorted(others, key=lambda x: x["date"], reverse=True)
    return (items, others)


def is_good_quality_image(src: str) -> bool:
    if "preview" in src or "main_alt" in src:
        return False
    else:
        return True


if __name__ == "__main__":
    from config import KODIK_TOKEN

    print(get_download_link("749374", "kinopoisk", 1, "610", token=KODIK_TOKEN))
