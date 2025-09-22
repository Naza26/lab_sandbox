import unittest
from rich.console import Console
from rich.table import Table

from ci_pipe.plotter import Plotter

# Importar tu clase Plotter

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = Plotter()
        self.trace = {
            "branch 1": {
                "1": {
                    "algorithm": "Preprocess Videos",
                    "input": ["video1.isxd"],
                    "output": ["video1-PP.isxd"],
                    "parameters": {"param1": 10}
                }
            }
        }

    def test_get_step_info_existing_step(self):
        try:
            self.plotter.get_step_info(self.trace, step_number=1, branch="branch 1")
        except Exception as e:
            self.fail(f"get_step_info raised an exception: {e}")

    def test_get_step_info_non_existing_step(self):
        try:
            self.plotter.get_step_info(self.trace, step_number=2, branch="branch 1")
        except Exception as e:
            self.fail(f"get_step_info raised an exception for non-existing step: {e}")

    def test_get_step_info_non_existing_branch(self):
        try:
            self.plotter.get_step_info(self.trace, step_number=1, branch="branch 2")
        except Exception as e:
            self.fail(f"get_step_info raised an exception for non-existing branch: {e}")

if __name__ == "__main__":
    unittest.main()
