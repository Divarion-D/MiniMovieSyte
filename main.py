import os

from flask import Flask, abort, redirect, render_template, request, send_file, session
from flask_mobility import Mobility
from flask_socketio import SocketIO

import config
import getters

app = Flask(__name__)
Mobility(app)
socketio = SocketIO(app)

app.config["SECRET_KEY"] = config.APP_SECRET_KEY


@app.route("/")
def index():
    return render_template(
        "index.html",
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


@app.route("/handler/", methods=["POST"])
def handler():
    data = dict(request.form)
    if "name" in data.keys():
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
            s_data = getters.get_search_data(query)
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


@app.route("/watch/<string:kp_id>/")
def watch(kp_id):
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

    iframe = getters.get_player_iframe(kp_id)

    for players in iframe[0]:
        if players:
            if players["iframeUrl"]:
                firstUrlIframe = players["iframeUrl"]
                break

    return render_template(
        "watch.html",
        kp_id=kp_id,
        poster=poster,
        title=title,
        description=description,
        genres=genres,
        countries=countries,
        year=year,
        rating=rating,
        leight=leight,
        iframe=iframe[1],
        firstUrlIframe=firstUrlIframe,
        is_dark=session["is_dark"] if "is_dark" in session.keys() else False,
    )


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
    socketio.run(
        app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
