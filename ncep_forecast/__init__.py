import os

from flask import Flask, render_template, abort, send_file

from ncep_wave.cache import (
    Cache,
    DEFAULT_CACHE
)

CACHE_ENV = "NCEP_FORECAST_CACHE"


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", TESTING=True)

    cache_path = os.environ[CACHE_ENV] if CACHE_ENV in os.environ else DEFAULT_CACHE
    cache = Cache(cache_path, auto_clean=False)
    print(f"cache: {cache._index._index}")

    @app.route("/")
    def index():
        return render_template("index.html", stations=cache.stations)

    @app.route("/forecast/<station>")
    def station(station):
        return render_template("forecast.html", station=station)

    @app.route("/latest/<station>")
    def get_latest_forecast_run(station):
        latest = cache.get_latest_forecast_run_time(station)
        if latest is None:
            abort(404, f"No forecast available for station {station}")
        return {station: latest}

    @app.route("/forecast/times/<station>")
    def get_latest_forecast_times(station):
        spectrum_times = cache.latest_forecast_times(station)
        if spectrum_times is None:
            abort(404, f"No forecast available for station {station}")
        print(f"times: {spectrum_times}")
        return {station: spectrum_times}

    @app.route("/forecast/<station>/<fc_time>")
    def get_forecast(station, fc_time):
        spectrums = cache.get_latest_forecast(station)
        if spectrums is None:
            abort(404, f"No forecast available for {station} station")
        for spec in spectrums:
            if fc_time in spec:
                return send_file(spec, mimetype="image/png")
        abort(404, f"No forecast available for {station}/{fc_time}")

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    return app


app = create_app()
