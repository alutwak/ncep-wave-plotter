import os
import time
import glob

DEFAULT_CACHE = os.path.expanduser("~/.cache/ncep-wave/")
DEFAULT_IMAGE_CACHE = os.path.join(DEFAULT_CACHE, "forecast")
SPECTRUM_TIMESPEC = "%Y%m%d%H"


def make_forecast_path(station, cache=DEFAULT_IMAGE_CACHE):
    return os.path.join(cache, station, time.strftime("%Y-%m-%d"))


def set_latest_forecast(forecast_path):
    forecast_dir = os.path.dirname(forecast_path)
    latest = os.path.join(forecast_dir, "latest")
    if os.path.exists(latest):
        os.remove(latest)
    os.symlink(forecast_path, latest)


def get_latest_forecast_dir(station, cache=DEFAULT_IMAGE_CACHE):
    station_dir = os.path.join(cache, station)
    latest = os.path.join(station_dir, "latest")
    if os.path.exists(latest):
        return latest
    return None


def get_latest_forecast(station, cache=DEFAULT_IMAGE_CACHE):
    forecast_dir = get_latest_forecast_dir(station, cache)
    if forecast_dir is None:
        return None

    spectrums = glob.glob(os.path.join(forecast_dir, "*.spec.png"))
    spectrums.sort()
    return spectrums


def create_spectrum_path(forecast_dir, localtime):
    pathtime = time.strftime(SPECTRUM_TIMESPEC, localtime)
    return os.path.join(forecast_dir, f"{pathtime}.spec.png")


def get_spectrum_time(path):
    time_str = os.path.basename(path).replace(".spec.png", "")
    return time_str  # time.strptime(time_str, SPECTRUM_TIMESPEC)
