import sys
import os
import time

import ncep_wave.terminal as term
from .data import fetch_latest_spectral_data
from .spectrum import Spectrum
from .plotter import plot_record
from .cache import Cache


def make_forecast(station: str, name: str, cache: Cache):
    term.message(f"Generating forecast for station: {station}{(name if name else None)}")
    this_hour = time.localtime()
    forecast_dir = cache.forecast_path(station, forecast_time=this_hour)
    latest_spec = fetch_latest_spectral_data(cache.path)
    if latest_spec is None:
        term.message("Forecast failed")
        return

    spec_path = os.path.join(latest_spec, f"gfswave.{station}.spec")
    spectrum = Spectrum(spec_path)

    term.message("Generating spectrum plots...")
    term.info(f"--- {forecast_dir} ---")
    os.makedirs(forecast_dir, exist_ok=True)
    for rec in spectrum.records:
        plot_record(rec, forecast_dir)

    cache.update_index(station, this_hour, name)


def plot_binary_data(outdir: str, path: str = None):
    if path:
        fspec = open(path, "rb")
    else:
        fspec = sys.stdin.buffer
    spectrum = Spectrum(fspec)

    term.message("Generating spectrum plots...")
    term.info(f"--- {outdir} ---")
    os.makedirs(outdir, exist_ok=True)
    for rec in spectrum.records:
        plot_record(rec, outdir, join_ends=False, normalize_dirs=False)
