import os

import ncep_wave.terminal as term
from .data import fetch_latest_enp_data
from .spectrum import Spectrum
from .plotter import plot_record
from .cache import set_latest_forecast


def make_forcast(station, outdir):
    latest_enp = fetch_latest_enp_data()

    spec_path = os.path.join(latest_enp, f"enp.{station}.spec")
    spectrum = Spectrum(spec_path)

    term.message("Generating spectrum plots...")
    term.info(f"--- {outdir} ---")
    os.makedirs(outdir, exist_ok=True)
    for rec in spectrum.records:
        plot_record(rec, outdir)

    set_latest_forecast(outdir)
