import os

from .data import fetch_latest_enp_data
from .spectrum import Spectrum
from .plotter import plot_record


def make_forcast(station, outdir):
    latest_enp = fetch_latest_enp_data()

    spec_path = os.path.join(latest_enp, f"enp.{station}.spec")
    spectrum = Spectrum(spec_path)

    os.makedirs(outdir, exist_ok=True)
    for rec in spectrum.records:
        plot_record(rec, outdir)
