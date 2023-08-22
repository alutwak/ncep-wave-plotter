import os
import yaml


class Config:

    def __init__(self, path):
        config_path = os.path.expanduser(path)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{path} does not exist")
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

    @property
    def stations(self):
        """Return the station definitions."""
        return self._config
