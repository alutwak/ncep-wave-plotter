import os
import time
import glob
import shutil
import json

import ncep_wave.terminal as term

DEFAULT_CACHE = os.path.expanduser("~/.cache/ncep-wave/")
SPECTRUM_TIMESPEC = "%Y%m%d%H"
FORECAST_TIMESPEC = "%Y-%m-%d-%H"


def create_spectrum_image_path(forecast_dir, localtime):
    pathtime = time.strftime(SPECTRUM_TIMESPEC, localtime)
    return os.path.join(forecast_dir, f"{pathtime}.spec.png")


def spec_path_to_time(path):
    time_str = os.path.basename(path).replace(".spec.png", "")
    return time_str


class Cache:

    class Index:

        def __init__(self, path, read_only=False):
            self._path = path
            self._updated = False
            self._read_only = read_only
            self._read()

        def __del__(self):
            if not self._read_only:
                self._write()

        def _read(self):
            if os.path.exists(self._path):
                with open(self._path) as f:
                    self._index = json.load(f)
            else:
                self._index = {}

        def _write(self):
            if self._updated and not self._read_only:
                # Only write if we've actually created an index
                with open(self._path, "w") as f:
                    json.dump(self._index, f, indent=2)

        @property
        def stations(self):
            return list(self._index.keys())

        def update_station(self, station, forecast_time,
                           name: str = None, location: (float, float) = None):
            forecast_time = Cache._strftime(forecast_time)
            if station in self._index:
                self._index[station]["latest"] = forecast_time
            else:
                self._index[station] = {"latest": forecast_time}
            if name is not None:
                self._index[station]["name"] = name
            if location is not None:
                self._index[station]["lat"] = location[0]
                self._index[station]["lon"] = location[1]
            self._updated = True

        def latest(self, station):
            try:
                return self._index[station]["latest"]
            except KeyError:
                return None

        def name(self, station):
            try:
                return self._index[station]["name"]
            except KeyError:
                return None

        def clean(self, stations_to_keep):
            for station in self.stations:
                if station not in stations_to_keep:
                    self._index.pop(station)

        @property
        def index(self):
            return self._index

    def __init__(self, path=DEFAULT_CACHE, auto_clean=None, read_only=False):
        self._path = path
        self._image_cache = os.path.join(path, "forecast")
        self._auto_clean = auto_clean
        self._read_only = read_only
        self.refresh()

    def __del__(self):
        if self._auto_clean:
            self.clean()

    @property
    def path(self):
        return self._path

    @property
    def image_cache(self):
        return self._image_cache

    @property
    def station_data(self):
        return self._index.index

    @staticmethod
    def _strftime(t=None):
        if t is None:
            return time.strftime(FORECAST_TIMESPEC)
        elif isinstance(t, time.struct_time) or isinstance(t, float) or isinstance(t, int):
            return time.strftime(FORECAST_TIMESPEC, t)
        elif not isinstance(t, str):
            raise AttributeError(f"Illegal time format: {t}")
        else:
            return t

    @staticmethod
    def _strptime(t: str):
        return time.strptime(t, FORECAST_TIMESPEC)

    @staticmethod
    def _make_index_entry(forecast_time, station_name):
        return {
            "name": station_name,
            "latest": Cache._strftime(forecast_time)
        }

    def refresh(self):
        self._index = Cache.Index(os.path.join(self._path, "index.json"),
                                  read_only=self._read_only)

    def forecast_path(self, station, forecast_time=None):
        forecast_time = Cache._strftime(forecast_time)
        return os.path.join(self.image_cache, station, forecast_time)

    def spectrum_path(self, station, forecast_time):
        return create_spectrum_image_path(
            self.forecast_path(station, forecast_time),
            time.localtime(forecast_time)
        )

    def update_index(self, station, forecast_time,
                     name: str = None, location: (float, float) = None):
        self._index.update_station(station, forecast_time, name, location)

    def get_latest_forecast_run_time(self, station):
        return self._index.latest(station)

    def get_station_name(self, station):
        return self._index.name(station)

    def _get_latest_forecast_dir(self, station):
        latest = self.get_latest_forecast_run_time(station)
        if latest is None:
            return latest
        return self.forecast_path(station, forecast_time=latest)

    def get_latest_forecast(self, station):
        forecast_dir = self._get_latest_forecast_dir(station)
        term.message(f"Latest forecast dir: {forecast_dir}")
        if forecast_dir is None:
            # Is this even possible?
            return None

        return sorted(glob.glob(os.path.join(forecast_dir, "*.spec.png")))

    def latest_forecast_times(self, station):
        forecast = self.get_latest_forecast(station)
        if forecast is None:
            return None
        return list(map(spec_path_to_time, forecast))

    def old_data(self):
        all_data = sorted(glob.glob(os.path.join(self._path, "gfs.*")))
        if len(all_data) == 0:
            return None, None
        old_days = all_data[:-1]
        latest_data = all_data[-1]
        old_runs = sorted(glob.glob(os.path.join(latest_data, "*")))[:-1]
        return old_days, old_runs

    def clean(self):
        # Clean up the data cache
        old_days, old_runs = self.old_data()
        if old_days is not None:
            for od in old_days:
                term.message(f"Removing old data directory {od}")
                shutil.rmtree(od, ignore_errors=True)
        if old_runs is not None:
            for run in old_runs:
                term.message(f"Removing old run directory {run}")
                shutil.rmtree(run, ignore_errors=True)

        # Clean up the image cache
        print(f"auto clean? {self._auto_clean}")
        if isinstance(self._auto_clean, (list, set)):
            keep_stations = self._auto_clean
        elif isinstance(self._auto_clean, dict):
            keep_stations = self._auto_clean.keys()
        else:
            keep_stations = self._index.stations

        print(f"keeping stations: {keep_stations}")

        station_caches = glob.glob(os.path.join(self.image_cache, "*"))
        for station in station_caches:
            if os.path.basename(station) in keep_stations:
                # Remove all but the most recent forecast
                forecasts = sorted(glob.glob(os.path.join(station, "*")))
                for forecast in forecasts[:-1]:
                    term.message(f"Removing old forecast {forecast}")
                    shutil.rmtree(forecast, ignore_errors=True)
            else:
                # Remove the whole folder
                print(f"Removing station: {station}")
                shutil.rmtree(station)

        # Clean up index
        self._index.clean(keep_stations)
