import os
import sys
import socket
import enum

from ftplib import FTP_TLS
import tarfile

import ncep_wave.terminal as term
from .cache import DEFAULT_CACHE

NCEP_SERVER = "ftpprd.ncep.noaa.gov"
PRODUCT_PATH = "/pub/data/nccf/com/gfs/prod"


class STATION_FILE(enum.Enum):
    SPECTRAL = "spec_tar.gz"
    BULLETIN = "bull_tar"


class NCEPWaveDataFetcher:

    def __init__(self, ntries=None):
        term.message("Connecting to the ncep ftp server...")
        tries = 0
        while True:
            try:
                self.ftp = FTP_TLS(NCEP_SERVER)
                break
            except socket.gaierror as e:
                msg = f"Connection try {tries + 1} failed."
                if ntries is not None:
                    if tries >= ntries:
                        term.message(f"Unable to connect to ncep ftp server: {e}")
                        sys.exit(1)
                    else:
                        msg += " Trying again..."
                tries += 1
                term.message(msg)

        term.message("Connected.")
        self.ftp.login(secure=False)
        self.ftp.cwd(PRODUCT_PATH)

    def __del__(self):
        self.ftp.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def gfs_dirs(self):
        return [f for f in self.ftp.nlst() if "gfs." in f]

    def gfs_runs(self, gfs_dir):
        """ Returns a dictionary of available gfs runs available in the given gfs dir.

        These are all '00', '06', '12', or '18'
        """
        return self.ftp.nlst(gfs_dir)

    def gfs_station_files(self, gfs_run):
        station_dir = gfs_run + "/wave/station/"
        return self.ftp.nlst(station_dir)

    def latest_run(self):
        for gdir in self.gfs_dirs[::-1]:
            runs = self.gfs_runs(gdir)
            if not runs:  # empty mdir
                continue

            return sorted(runs)[-1]

    def latest_station_file(self, file_type):
        # Iterate from the end
        for gdir in self.gfs_dirs[::-1]:
            for run in self.gfs_runs(gdir)[::-1]:
                sfiles = self.gfs_station_files(run)
                for f in sfiles:
                    if file_type.value in f:
                        return f
        return None

    def latest_spectrals(self):
        return self.latest_station_file(STATION_FILE.SPECTRAL)

    def fetch_latest_spectrals(self, cache=DEFAULT_CACHE):
        # Get the target data, the output dirname and the output path
        target_tar = self.latest_spectrals()
        if target_tar is None:
            term.message("Failed to get the latest spectrals")
            return None
        output_tar = os.path.join(cache, target_tar)
        output_path, _ = os.path.splitext(output_tar)

        # If the output path already exists then we're done
        if os.path.exists(output_path):
            term.message(f"Found latest spectral run: {output_path}")
            return output_path

        # We need the data, so download it
        term.message(f"Downloading latest spectral run to {output_tar}")
        os.makedirs(os.path.dirname(output_tar), exist_ok=True)
        with open(output_tar, "wb") as f:
            self.ftp.retrbinary(f"RETR {target_tar}", f.write, 1024)

        # Now extract the tar file
        term.message(f"Extracting {output_tar} to {output_path}")
        tf = tarfile.open(output_tar)
        tf.extractall(output_path)
        tf.close()

        return output_path


def fetch_latest_spectral_data(cache=DEFAULT_CACHE):
    with NCEPWaveDataFetcher() as wdf:
        return wdf.fetch_latest_spectrals(cache)
