import time
import os
import argparse

from forecast import make_forcast


def main():
    parser = argparse.ArgumentParser("A tool for producing plots from ncep wave data")
    parser.add_argument("action", choices=["forecast"], help="Plot a forecast")
    parser.add_argument("station")
    parser.add_argument("-o", "--outdir", default="~/ncep-wave", help="Output directory")

    args = parser.parse_args()

    outdir = os.path.expanduser(args.outdir)

    if args.action == "forecast":
        print("Generating forecast")
        forecast_dir = os.path.join(outdir, "forecast", time.strftime("%Y-%m-%d"))
        make_forcast(args.station, forecast_dir)


if __name__ == "__main__":
    main()
