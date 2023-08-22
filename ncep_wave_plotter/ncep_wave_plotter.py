import os
import sys
import yaml
import argparse

from ncep_wave.forecast import make_forecast, plot_binary_data
from ncep_wave.config import Config
from ncep_wave.cache import Cache, DEFAULT_CACHE
import ncep_wave.terminal as term


def main():
    parser = argparse.ArgumentParser("A tool for producing plots from ncep wave data")
    parser.add_argument("action", choices=["forecast", "plot-binary"], help="Plot a forecast")
    parser.add_argument("-s", "--station", help="Station to generate plots for")
    parser.add_argument("-n", "--station_name", default=None, help="Optional name for the station")
    parser.add_argument("-f", "--config", help="Config file with a list of stations to generate plots for")
    parser.add_argument("-i", "--input", default=None, help="Input file for binary data")
    parser.add_argument("-o", "--outdir", default=DEFAULT_CACHE, help="Output directory")

    args = parser.parse_args()

    outdir = os.path.expanduser(args.outdir)

    if args.action == "forecast":

        if args.station:
            stations = [{args.station: args.station_name}]
            term.message(f"station: {args.station}")
        elif args.config:
            try:
                config = Config(args.config)
                stations = config.stations
            except FileNotFoundError:
                term.message(f"{args.config} does not exist")
                sys.exit(1)
        else:
            term.message("ERROR: Either a station or a config file must be given")
            parser.print_help()
            sys.exit(1)

        cache = Cache(outdir)

        for station, name in stations.items():
            make_forecast(station, name, cache)
    if args.action == "plot-binary":
        term.message("Plotting binary spectrum")
        plot_binary_data(args.outdir, args.input)


if __name__ == "__main__":
    main()
