# NCEP Wave Plotter

A (better?) replacement for the now-defunct NOAA NCEP spectral wave plots.

## Requirements

The `ncep-wave-plotter` requires Python 3.6 or later, along with the following python libraries:

* numpy (`python3 -m pip install numpy`)
* matplotlib (`python3 -m pip install matplotlib`)
* Flask (`python3 -m pip install Flask`)

## Installation

I'll write a decent install script at some point, but for right now, these commands should work:

```shell
python3 -m pip install virtualenv
virtualenv .wave-env
source .wave-env/bin/activate
cd <ncep-wave-plotter directory>
pip install .
```

## Quick Start

### Generating plots

To generate plots for the latest NCEP forecasts and store them in the default cache directory (the directory that the web
server reads from), from the `ncep-wave-plotter` directory run:

```shell
python3 ncep-wave-plotter.py forecast <station id>
```

The path for each plot generated will be printed to the terminal.

If you live on the Olympic Peninsula, then you probably want to use the Neah Bay station ID, which is 46087.

### Running a test web server

Once you have generated the plots for a station, you can instantiate a local web server to serve time-lapse animations of those
plots. From the `ncep-wave-plotter` directory run:

```shell
export FLASK_APP=ncep_forecast
export FLASK_ENV=development
flask run
```

Then, from your browser, navigate to `http://127.0.0.1:5000/forecast/<station id>`. If my web developer skills are not
absolutely horrible (which they probably are) then you should see some pretty fantastic spectral plots.


## Setting up a development server

There are many different options for running the NCEP Wave Plotter application on a development server, serveral of which
are discussed on the [Flask website](https://flask.palletsprojects.com/en/1.1.x/deploying/#deployment). The one that I've
been using is [Twisted](https://twistedmatrix.com). Once the `ncep-wave-plotter` project is installed, I've just been 
running the following command to start the `twistd` daemon:

```shell
twistd web --wsgi ncep_forecast.app
```

This runs a server on port 8080.

If you're running a continuous server, you will probably also want to keep your data up to date. I'm doing this with
the following `crontab` entry, which updates the data once an hour:

```shell
0 * * * * <path to ncep-wave-plotter> forecast 46087
```

### Adding the webserver to systemd

These instructions are derived from those found [here](https://twistedmatrix.com/documents/21.2.0/core/howto/systemd.html).

To start with, you will need to edit the `User` and `Group` parameters in the [ncep-forecast.service](ncep-forecast.service)
file to have the desired user and group for your system. The instructions above say to use the "nobody" user and group, but
this does not work for me and if you do a little googling, you'll likely read again and again that using "nobody" is strongly
discouraged. So the better plan would be to create a unique user for this service and give it a restrictive shell (`rbash`)
to keep it safe.

```shell
sudo cp ncep-forecast.service /etc/systemd/system/
sudo cp ncep-forecast.socket /etc/systemd/system/
sudo systemctl daemon-reload

# Start the socket
sudo systemctl start ncep-forecast.socket

# Check the socket's status
systemctl status ncep-forecast.socket

# Start the service
sudo systemctl start ncep-forecast.service

# Check the status
systemctl status ncep-forecast.service

# Make ncep-wave-forecast run on boot
sudo systemctl enable ncep-forecast.socket
sudo systemctl enable ncep-forecast.service
```

#### Updating the webserver

```shell
cd ncep-wave-plotter
sudo pip install .
suddo systemctl restart ncep-forecast.service
```

Happy surfing!
