import os
import time
import glob
import shutil
import json

import ncep_wave.terminal as term

DEFAULT_CACHE = os.path.expanduser("~/.cache/ncep-wave/")
SPECTRUM_TIMESPEC = "%Y%m%d%H"
FORECAST_TIMESPEC = "%Y-%m-%d-%H"


def get_image_cache(cache=DEFAULT_CACHE):
    return os.path.join(cache, "forecast")


def get_cache_index(cache=DEFAULT_CACHE):
    return os.path.join(cache, "index.json")


def make_forecast_path(station, forecast_time=None, cache=DEFAULT_CACHE):
    if forecast_time is None:
        forecast_time = time.strftime(FORECAST_TIMESPEC)
    elif isinstance(forecast_time, time.struct_time):
        forecast_time = time.strftime(FORECAST_TIMESPEC, forecast_time)
    elif isinstance(forecast_time, float) or isinstance(forecast_time, int):
        forecast_time = time.strftime(FORECAST_TIMESPEC, forecast_time)
    elif not isinstance(forecast_time, str):
        raise AttributeError(f"Illegal forecast time: {forecast_time}")

    image_cache = get_image_cache(cache)
    return os.path.join(image_cache, station, forecast_time)


def set_latest_forecast(station, forecast_time, cache=DEFAULT_CACHE):
    # Read the existing index, if it exists
    findex = get_cache_index(cache)
    if os.path.exists(findex):
        with open(findex) as f:
            index = json.load(f)
    else:
        index = {}

    # Set latest forecast time
    index[station] = time.strftime(FORECAST_TIMESPEC, forecast_time)
    with open(findex, "w") as f:
        json.dump(index, f)


def get_latest_forecast_run_time(station, cache=DEFAULT_CACHE):
    findex = get_cache_index(cache)

    try:
        # Read index
        with open(findex, "r") as f:
            index = json.load(f)

        term.message(f"Latest forecast run time: {index[station]}")
        return index[station]
    except (FileNotFoundError, KeyError):
        return None


def get_latest_forecast_dir(station, cache=DEFAULT_CACHE):
    latest = get_latest_forecast_run_time(station, cache=cache)
    return make_forecast_path(station, forecast_time=latest, cache=cache)


def get_latest_forecast(station, cache=DEFAULT_CACHE):
    forecast_dir = get_latest_forecast_dir(station, cache)
    term.message(f"Latest forecast dir: {forecast_dir}")
    if forecast_dir is None:
        return None

    return sorted(glob.glob(os.path.join(forecast_dir, "*.spec.png")))


def create_spectrum_path(forecast_dir, localtime):
    pathtime = time.strftime(SPECTRUM_TIMESPEC, localtime)
    return os.path.join(forecast_dir, f"{pathtime}.spec.png")


def get_spectrum_time(path):
    time_str = os.path.basename(path).replace(".spec.png", "")
    return time_str


def clean_up_cache(cache=DEFAULT_CACHE):
    # Clean up the data cache
    old_days = sorted(glob.glob(os.path.join(cache, "gfs.*")))
    for od in old_days[:-1]:
        term.message(f"Removing old data directory {od}")
        shutil.rmtree(od, ignore_errors=True)
    old_runs = sorted(glob.glob(os.path.join(old_days[-1], "*")))
    for run in old_runs[:-1]:
        term.message(f"Removing old run directory {run}")
        shutil.rmtree(run, ignore_errors=True)

    # Clean up the image cache
    image_cache = get_image_cache(cache)
    station_caches = glob.glob(os.path.join(image_cache, "*"))
    for station in station_caches:
        forecasts = sorted(glob.glob(os.path.join(station, "*")))
        for forecast in forecasts[:-1]:
            term.message(f"Removing old forecast {forecast}")
            shutil.rmtree(forecast, ignore_errors=True)
