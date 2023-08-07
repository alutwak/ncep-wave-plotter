import os
import sys
import yaml
import argparse

from ncep_wave.forecast import make_forcast, plot_binary_data
from ncep_wave.cache import DEFAULT_CACHE
import ncep_wave.terminal as term


def main():
    parser = argparse.ArgumentParser("A tool for producing plots from ncep wave data")
    parser.add_argument("action", choices=["forecast", "plot-binary"], help="Plot a forecast")
    parser.add_argument("-s", "--station", help="Station to generate plots for")
    parser.add_argument("-f", "--config", help="Config file with a list of stations to generate plots for")
    parser.add_argument("-i", "--input", default=None, help="Input file for binary data")
    parser.add_argument("-o", "--outdir", default=DEFAULT_CACHE, help="Output directory")

    args = parser.parse_args()

    outdir = os.path.expanduser(args.outdir)

    if args.action == "forecast":

        if args.station:
            stations = [args.station]
        elif args.config:
            config_path = os.path.expanduser(args.config)
            if not os.path.exists(config_path):
                term.message(f"{args.config} does not exist")
                sys.exit(1)
            with open(config_path) as f:
                stations = yaml.safe_load(f)
        else:
            term.message("ERROR: Either a station or a config file must be given")
            parser.print_help()
            sys.exit(1)

        term.message("Generating forecast")
        for station in stations:
            make_forcast(station, outdir)
    if args.action == "plot-binary":
        term.message("Plotting binary spectrum")
        plot_binary_data(args.outdir, args.input)


if __name__ == "__main__":
    main()
