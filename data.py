import os
import sys
import re
import socket

from ftplib import FTP_TLS
import tarfile


NCEP_SERVER = "ftpprd.ncep.noaa.gov"
PRODUCT_PATH = "/pub/data/nccf/com/wave/prod"
DEFAULT_CACHE = os.path.expanduser("~/.cache/ncep-wave/")


class NCEPWaveDataFetcher:

    def __init__(self, ntries=None):
        print("Connecting to the ncep ftp server...")
        tries = 0
        while True:
            try:
                self.ftp = FTP_TLS(NCEP_SERVER)
                break
            except socket.gaierror as e:
                msg = f"Connection try {tries + 1} failed."
                if ntries is not None:
                    if tries >= ntries:
                        print(f"Unable to connect to ncep ftp server: {e}")
                        sys.exit(1)
                    else:
                        msg += " Trying again..."
                        tries += 1
                print(msg)

        print("Connected.")
        self.ftp.login(secure=False)
        self.ftp.cwd(PRODUCT_PATH)

    def __del__(self):
        self.ftp.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def multi_dirs(self):
        return [f for f in self.ftp.nlst() if "multi" in f]

    def enpSpecRuns(self, multi_dir):
        """ Returns a dictionary of available enp spectral runs available in the given multi dirs, keyed by the run time
        """
        enp_re = r"multi.+/enp.t(\d\d)z.spec_tar.gz"
        enp_specs = {}
        for f in self.ftp.nlst(multi_dir):
            m = re.fullmatch(enp_re, f)
            if m:
                enp_specs[m.group(1)] = f
        return enp_specs

    def latest_enp(self):
        latest = self.multi_dirs[-1]
        enps = self.enpSpecRuns(latest)
        run_times = list(enps.keys())
        run_times.sort()

        return enps[run_times[-1]]

    def fetch_latest_enp(self, cache=None):
        if cache is None:
            cache = DEFAULT_CACHE

        # Get the target data, the output dirname and the output path
        target_tar = self.latest_enp()
        output_tar = os.path.join(cache, target_tar)
        output_path, _ = os.path.splitext(output_tar)

        # If the output path already exists then we're done
        if os.path.exists(output_path):
            print(f"Found latest enp spectral run: {output_path}")
            return output_path

        # We need the data, so download it
        print(f"Downloading latest enp spectral run to {output_tar}")
        os.makedirs(os.path.dirname(output_tar), exist_ok=True)
        with open(output_tar, "wb") as f:
            self.ftp.retrbinary(f"RETR {target_tar}", f.write, 1024)

        # Now extract the tar file
        print(f"Extracting {output_tar} to {output_path}")
        tf = tarfile.open(output_tar)
        tf.extractall(output_path)
        tf.close()

        return output_path


def fetch_latest_enp_data(cache=None):
    with NCEPWaveDataFetcher() as wdf:
        return wdf.fetch_latest_enp(cache)
