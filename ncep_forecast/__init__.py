
from flask import Flask, render_template, abort, send_file

from ncep_wave.cache import get_latest_forecast, get_spectrum_time


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev',
                            TESTING=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/forecast/<station>")
    def station(station):
        return render_template("forecast.html", station=station)

    @app.route("/latest/<station>")
    def get_latest_forecast_times(station):
        spectrums = get_latest_forecast(station)
        if spectrums is None:
            abort(404)
        times = [get_spectrum_time(spec) for spec in spectrums]
        return {station: times}

    @app.route("/forecast/<station>/<fc_time>")
    def get_forecast(station, fc_time):
        spectrums = get_latest_forecast(station)
        if spectrums is None:
            abort(404, f"No forecast available for {station} station")
        for spec in spectrums:
            if fc_time in spec:
                return send_file(spec, mimetype="image/png")
        abort(404, f"No forecast available for {station}/{fc_time}")

    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', "*")
        return response

    return app


app = create_app()
