import os
import yaml


class ISXConfig:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "isx_config.yaml")
        self.config_path = config_path
        self.defaults = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def get_parameters(self, name):
        return self.defaults.get(name, {})