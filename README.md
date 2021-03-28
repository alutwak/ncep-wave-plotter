# NCEP Wave Plotter

A (better?) replacement for the now-defunct NOAA NCEP spectral wave plots.

## Requirements

The `ncep-wave-plotter` requires Python 3.6 or later, along with the following python libraries:

* numpy (`python3 -m pip install numpy`)
* matplotlib (`python3 -m pip install matplotlib`)
* Flask (`python3 -m pip install Flask`)

## Quick Start

### Generating plots

To generate plots for the latest NCEP forecasts and store them in the default cache directory (the directory that the web
server reads from), from the `ncep-wave-plotter` directory run:

```shell
python3 ncep-wave-plotter.py forecast <station id>
```

The path for each plot generated will be printed to the terminal.

If you live on the Olympic Peninsula, then you probably want to use the Neah Bay station ID, which is 46087.

### Running the web server

Once you have generated the plots for a station, you can instantiate a local web server to serve time-lapse animations of those
plots. From the `ncep-wave-plotter` directory run:

```shell
export FLASK_APP=ncep_forecast
export FLASK_ENV=development
flask run
```

Then, from your browser, navigate to `http://127.0.0.1:5000/forecast/<station id>`. If my web developer skills are not
absolutely horrible (which they probably are) then you should see some pretty fantastic web spectral plots. Happy surfing!
