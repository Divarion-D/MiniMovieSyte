from flask import Flask, render_template, request, redirect, abort, session, send_file
from flask_socketio import SocketIO
from flask_mobility import Mobility
import getters
from json import load
import config
import os

app = Flask(__name__)
Mobility(app)
socketio = SocketIO(app)

app.config["SECRET_KEY"] = config.APP_SECRET_KEY

with open("translations.json", "r") as f:
    # Используется для указания озвучки при скачивании файла
    translations = load(f)

if config.USE_SAVED_DATA or config.SAVE_DATA:
    from cache import Cache

    ch = Cache(config.SAVED_DATA_FILE, config.SAVING_PERIOD, config.CACHE_LIFE_TIME)
ch_save = config.SAVE_DATA
ch_use = config.USE_SAVED_DATA


@app.route("/")
def index():
    return render_template(
        "index.html",
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


@app.route("/", methods=["POST"])
def index_form():
    data = dict(request.form)
    if "kinopoisk_id" in data.keys():
        return redirect(f"/download/kp/{data['kinopoisk_id']}/")
    elif "name" in data.keys():  # name = Kodik
        return redirect(f"/search/name/{data['name']}/")
    else:
        return abort(400)


@app.route("/change_theme/", methods=["POST"])
def change_theme():
    # Костыль для смены темы
    if "is_dark" in session.keys():
        session["is_dark"] = not (session["is_dark"])
    else:
        session["is_dark"] = True
    return redirect(request.referrer)


@app.route("/search/<string:db>/<string:query>/")
def search_page(db, query):
    if db == "name":
        try:
            # Попытка получить данные с кодика
            s_data = getters.get_search_data(query, ch if ch_save or ch_use else None)
            return render_template(
                "search.html",
                films=s_data[0],
                tv_series=s_data[1],
                others=s_data[2],
                is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
            )
        except:
            return render_template(
                "search.html",
                is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
            )
    else:
        # Другие базы не поддерживаются (возможно в будующем будут)
        return abort(400)


@app.route("/download/<string:id>/")
def download_choose_translation(id):
    cache_used = False
    if ch_use and ch.is_id("sh" + id):
        # Проверка кеша на наличие данных
        cached = ch.get_data_by_id("sh" + id)
        name = cached["title"]
        pic = cached["image"]
        score = cached["score"]
        dtype = cached["type"]
        date = cached["date"]
        status = cached["status"]
    if not cache_used:
        try:
            # Попытка получить данные
            data = getters.get_details_info(id)
            name = data["title"]
            pic = data["image"]
            dtype = data["type"]
            date = data["date"]
            status = data["status"]
        except:
            name = "Неизвестно"
            pic = config.IMAGE_AGE_RESTRICTED
        finally:
            if ch_save and not ch.is_id("sh" + id):
                # Записываем данные в кеш если их там нет
                ch.add_id(
                    "sh" + id,
                    name,
                    pic,
                    data["status"] if data else "Неизвестно",
                    data["date"] if data else "Неизвестно",
                    data["type"] if data else "Неизвестно",
                )

    try:
        # Получаем данные о наличии переводов
        serial_seasons = getters.get_serial_seasons(id)
    except Exception as ex:
        return f"""
        <h1>По данному запросу нет данных</h1>
        {f'<p>Exception type: {ex}</p>' if config.DEBUG else ''}
        """
    return render_template(
        "info.html",
        title=name,
        image=pic,
        seasons=serial_seasons,
        id=id,
        dtype=dtype,
        date=date,
        status=status,
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


@app.route("/watch/movie/<string:kp_id>/")
def watch_movie(kp_id):
    try:
        # Попытка получить данные
        data = getters.get_details_info(kp_id)
        title = data["title"]
        poster = data["image"]
        year = data["year"]
        leight = data["leight"]
        description = data["description"]
        genres = data["genres"]
        countries = data["countries"]
        rating = data["imdbRating"]
    except Exception as ex:
        print(ex)
        title = "Неизвестно"
        poster = config.IMAGE_NOT_FOUND

    files = getters.get_movie_links(kp_id)
    firtfile = {}
    for balancer in files:
        if files[balancer]:
            for translation_name in files[balancer]:
                firtfile = {
                    "translation": translation_name,
                    "files": files[balancer][translation_name],
                }
                break

    print(firtfile)

    return render_template(
        "movie.html",
        kp_id=kp_id,
        poster=poster,
        title=title,
        description=description,
        genres=genres,
        countries=countries,
        year=year,
        rating=rating,
        leight=leight,
        files=files,
        firtfile=firtfile,
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


@app.route("/watch/<string:kp_id>/")
def watch1(kp_id):
    try:
        # Попытка получить данные
        data = getters.get_details_info(kp_id)
        name = data["title"]
        poster = data["image"]
        dtype = data["type"]
        date = data["date"]
        status = data["status"]
    except Exception as ex:
        print(ex)
        name = "Неизвестно"
        poster = config.IMAGE_AGE_RESTRICTED

    seasons = getters.get_serial_seasons(kp_id)

    return render_template(
        "watch.html",
        title=name,
        image=poster,
        kp_id=kp_id,
        dtype=dtype,
        date=date,
        status=status,
        seria=1,
        series=10,
        data=f"{1}-{1}",
        seasons=seasons,
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


@app.route("/watch/<string:kp_id>/<string:data>/<string:data2>/")
@app.route("/watch/<string:kp_id>/<string:data>/<string:data2>/<string:quality>")
def watch(kp_id, data, data2, quality="720"):
    try:
        data = data.split("-")
        balancer = data[0]
        translation_name = data[1]

        data = data2.split("-")
        season = int(data2[0])
        seria = int(data[1])

        seasons = getters.get_serial_seasons(kp_id)[balancer]

        # get seasons
        for i in range(len(seasons)):
            if seasons[i]["name"] == translation_name:
                seasons = seasons[i]["seasons"]
                break

        if season == 0 and seria == 0:
            for i in seasons:
                for j in seasons[i]:
                    season = int(i)
                    seria = int(j)
                    break
                break

        # Получаем данные с сервера
        straight_url = getters.get_download_link_tv(
            kp_id, balancer, translation_name, season, seria
        )
        url = f"/download/{kp_id}/{'-'.join(data)}/{quality}-{seria}"  # Ссылка на скачивание через этот сервер
        return render_template(
            "watch.html",
            url=url,
            season=season,
            seria=seria,
            kp_id=kp_id,
            data="-".join(data),
            series=10,
            quality=quality,
            straight_url=straight_url,
            is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
        )
    except Exception as ex:
        print(ex)
        return abort(404)


@app.route("/resources/<string:path>")
def resources(path: str):
    if os.path.exists(f"resources\\{path}"):  # Windows-like
        return send_file(f"resources\\{path}")
    elif os.path.exists(f"resources/{path}"):  # Unix
        return send_file(f"resources/{path}")
    else:
        return abort(404)


@app.route("/favicon.ico")
def favicon():
    return send_file(config.FAVICON_PATH)


if __name__ == "__main__":
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG)
