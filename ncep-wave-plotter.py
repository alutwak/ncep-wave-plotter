import os
import argparse

from ncep_wave.forecast import make_forcast
from ncep_wave.cache import make_forecast_path, DEFAULT_IMAGE_CACHE
import ncep_wave.terminal as term


def main():
    parser = argparse.ArgumentParser("A tool for producing plots from ncep wave data")
    parser.add_argument("action", choices=["forecast"], help="Plot a forecast")
    parser.add_argument("station")
    parser.add_argument("-o", "--outdir", default=DEFAULT_IMAGE_CACHE, help="Output directory")

    args = parser.parse_args()

    outdir = os.path.expanduser(args.outdir)

    if args.action == "forecast":
        term.message("Generating forecast")
        forecast_dir = make_forecast_path(args.station, outdir)
        make_forcast(args.station, forecast_dir)


if __name__ == "__main__":
    main()
