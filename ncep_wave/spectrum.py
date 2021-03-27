import re
import time

import numpy as np

import ncep_wave.terminal as term

# '<Field ID>' <n freqs> <n dirs> <n points> '<grid name>'
#
# Indent 1: <freqs (Hz)> X nfreqs
#
# Indent 2: <directions (rads)> X ndirs
#
# <Time>
# '<station number>' <lat>-<lon> <d> <u10> <u10 dir> <crnt speed> <crnt dir>
#
# Indent 1: E(f, theta) X nfreqs*ndirs


def indent(f):
    ident = 0
    place = f.tell()
    char = f.read(1)
    while char == " " and char != "\n":
        ident += 1
        char = f.read(1)
    f.seek(place)
    return ident


class Spectrum:

    nfreqs = None
    ndirs = None
    freqs = None
    dirs = None
    records = None

    class Record:

        def __init__(self, rtime, pid, lat, lon, d, UA, UD, crnt, crnt_dir, freqs, dfreqs, dirs):
            self.rtime = rtime
            self.pid = pid
            self.lat = lat
            self.lon = lon
            self.depth = d      # Depth
            self.UA = UA        # Wind speed at 10m
            self.UD = UD        # Wind dir
            self.current = crnt
            self.crnt_dir = crnt_dir
            self.freqs = freqs
            self.dfreqs = dfreqs
            self.dirs = dirs
            self.data = None

        @property
        def hs(self):
            """ Hs is calculated as 4 * sqrt(E), where E is the spectrum integral

            (see Nondirectional and Directional Wave Data Analysis Procedures, sec 3.2.11)
            """
            # Integrate across directions
            dir_int = self.data.sum(axis=0) * 2*np.pi/len(self.dirs)

            # Bandwidths for the frequency bands
            bw = 0.5 * (self.dfreqs - 1/self.dfreqs) * self.freqs
            bw[-1] *= 0.5
            tailf = 0.25 * self.freqs[-1]

            E = np.dot(dir_int, bw) + tailf * dir_int[-1]
            return 4 * np.sqrt(E)

    def __init__(self, fspec_path):
        term.message(f"Parsing data in {fspec_path}")

        self.fspec = open(fspec_path)
        self._records = []
        self._parse_header()

    def location(self):
        """ Returns the location of the station
        """
        if len(self._records) == 0:
            record = next(self.records)
        else:
            record = self._records[0]
        return record.lat, record.lon

    def station(self):
        if len(self._records) == 0:
            record = next(self.records)
        else:
            record = self._records[0]
        return record.pid

    @property
    def records(self):
        self._records = []
        while True:
            rec = self._parse_record()
            if not rec:
                return
            self._records.append(rec)
            yield rec

    def _parse_header(self):
        """ Parses the header

        This captures:
        * n freqs
        * n dirs
        * n points (grid name is ignored)
        * Frequencies, and derives df
        * Directions
        """
        # Capture metadata
        line = self.fspec.readline().strip()
        m = re.fullmatch(r"'WAVEWATCH III SPECTRA' +([0-9]+) +([0-9]+) +([0-9]+).*", line)
        if not m:
            raise ValueError(f"Bad header format: {line}")
        self.nfreqs, self.ndirs, self.npoints = [int(val) for val in m.groups()]

        # Capture frequencies
        freqs = []
        while indent(self.fspec) == 1:
            freqs += [float(val) for val in self.fspec.readline().split()]
        if len(freqs) != self.nfreqs:
            raise ValueError(f"Wrong number of frequencies: {len(freqs)} != {self.nfreqs}\n {freqs}")
        self.freqs = np.array(freqs)

        # Calculate dfreqs
        df = self.freqs[1:]/self.freqs[:-1]
        self.df = np.append(df, df[-1])

        # Capture directions
        dirs = []
        while indent(self.fspec) == 2:
            dirs += [float(val) for val in self.fspec.readline().split()]
        if len(dirs) != self.ndirs:
            raise ValueError(f"Wrong number of directions: {len(dirs)} != {self.ndirs}\n{dirs}")
        self.dirs = np.array(dirs)

    def _parse_record(self):
        """ Parses a single record

        A record consists of:
        * The record time YYYYMMDD HH0000
        * Station name
        * Station latitude
        * Station longitude
        * Water depth
        * Wind speed (m/s)
        * Wind direction (deg)
        * Current speed (m/s)
        * Current direction (deg)
        * ndirs*nfreqs data points
        """
        # Read time
        timeline = self.fspec.readline()

        if not timeline:
            return None

        rtime = time.mktime(time.strptime(timeline.strip(), "%Y%m%d %H%M%S"))

        # Read Summary
        rsum = self.fspec.readline().strip()
        m = re.fullmatch(r"'([^ ]+) *' +(-?[0-9.]+) *(-?[0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+)",
                         rsum)
        if not m:
            raise ValueError(f"Bad record header: {rsum}")
        params = [m.groups()[0]] + [float(val) for val in m.groups()[1:]]
        record = Spectrum.Record(rtime, *params, self.freqs, self.df, self.dirs)

        data = []
        while indent(self.fspec) == 2:
            data += [float(val) for val in self.fspec.readline().split()]

        if len(data) != self.nfreqs * self.ndirs:
            raise ValueError(f"Received an unexpected amount of data: \n{data}\n\n{len(data)} elements")

        record.data = np.array(data).reshape((self.ndirs, self.nfreqs))
        return record
