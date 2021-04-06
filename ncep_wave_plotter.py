import os
import argparse

from ncep_wave.forecast import make_forcast
from ncep_wave.cache import DEFAULT_CACHE
import ncep_wave.terminal as term


def main():
    parser = argparse.ArgumentParser("A tool for producing plots from ncep wave data")
    parser.add_argument("action", choices=["forecast"], help="Plot a forecast")
    parser.add_argument("station")
    parser.add_argument("-o", "--outdir", default=DEFAULT_CACHE, help="Output directory")

    args = parser.parse_args()

    outdir = os.path.expanduser(args.outdir)

    if args.action == "forecast":
        term.message("Generating forecast")
        make_forcast(args.station, outdir)


if __name__ == "__main__":
    main()
