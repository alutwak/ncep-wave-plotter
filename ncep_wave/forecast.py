import sys
import os
import time

import ncep_wave.terminal as term
from .data import fetch_latest_spectral_data
from .spectrum import Spectrum
from .plotter import plot_record
from .cache import make_forecast_path, set_latest_forecast, clean_up_cache


def make_forcast(station, outdir):
    this_hour = time.localtime()
    forecast_dir = make_forecast_path(station, forecast_time=this_hour, cache=outdir)
    latest_spec = fetch_latest_spectral_data()
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

    set_latest_forecast(station, this_hour, cache=outdir)
    clean_up_cache(cache=outdir)


def plot_binary_data(outdir, path=None):
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
