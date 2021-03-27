import os

import ncep_wave.terminal as term
from .data import fetch_latest_spectral_data
from .spectrum import Spectrum
from .plotter import plot_record
from .cache import set_latest_forecast


def make_forcast(station, outdir):
    latest_spec = fetch_latest_spectral_data()
    if latest_spec is None:
        term.message("Forecast failed")
        return

    spec_path = os.path.join(latest_spec, f"gfswave.{station}.spec")
    spectrum = Spectrum(spec_path)

    term.message("Generating spectrum plots...")
    term.info(f"--- {outdir} ---")
    os.makedirs(outdir, exist_ok=True)
    for rec in spectrum.records:
        plot_record(rec, outdir)

    set_latest_forecast(outdir)
