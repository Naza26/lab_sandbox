# test_isx_config.py
import unittest
import os
import tempfile
import yaml

from isx_pipeline.available_isx_algorithms import AvailableISXAlgorithms
from isx_pipeline.config.isx_config import ISXConfig


class TestISXConfig(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        self.yaml_content = {
            'Preprocess Videos': None,
            'Bandpass Filter Videos': {'low_cutoff': 0.005, 'high_cutoff': 0.5},
            'Motion Correction Videos': {'max_translation': 20, 'series_name': 'series'}
        }
        with open(self.temp_file.name, 'w') as f:
            yaml.safe_dump(self.yaml_content, f)

        self.config = ISXConfig(config_path=self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_defaults(self):
        self.assertEqual(self.config.defaults, self.yaml_content)

    def test_get_parameters_with_string_key(self):
        params = self.config.get_parameters("Bandpass Filter Videos")
        expected = {'low_cutoff': 0.005, 'high_cutoff': 0.5}
        self.assertEqual(params, expected)

    def test_get_parameters_with_enum_value(self):
        params = self.config.get_parameters(AvailableISXAlgorithms.BANDPASS_FILTER_VIDEOS.value)
        expected = {'low_cutoff': 0.005, 'high_cutoff': 0.5}
        self.assertEqual(params, expected)

    def test_get_parameters_nonexistent_key(self):
        params = self.config.get_parameters("Nonexistent Algorithm")
        self.assertEqual(params, {})


if __name__ == "__main__":
    unittest.main()
