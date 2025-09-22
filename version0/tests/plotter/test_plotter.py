import io
import unittest
from rich.console import Console
from rich.table import Table

from ci_pipe.plotter import Plotter

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.trace = {
            "branch 1": {
                "1": {
                    "algorithm": "Preprocess Videos",
                    "input": ["video1.isxd"],
                    "output": ["video1-PP.isxd"],
                    "parameters": {"param1": 10}
                },
                "2": {
                    "algorithm": "Bandpass Filter Videos",
                    "input": ["video1-PP.isxd"],
                    "output": ["video1-BP.isxd"],
                    "parameters": {"low_cutoff": 0.5}
                }
            }
        }
        self.output = io.StringIO()
        self.console = Console(file=self.output, force_terminal=True, color_system=None)
        self.plotter = Plotter(console=self.console)

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

    def test_get_all_trace_from_branch_existing_branch(self):
        try:
            self.plotter.get_all_trace_from_branch(self.trace, "branch 1")
        except Exception as e:
            self.fail(f"get_all_trace_from_branch raised an exception: {e}")

        content = self.output.getvalue()
        self.assertIn("Step 1", content)
        self.assertIn("Preprocess Videos", content)
        self.assertIn("Step 2", content)
        self.assertIn("Bandpass Filter Videos", content)

    def test_get_all_trace_from_branch_non_existing_branch(self):
        try:
            self.plotter.get_all_trace_from_branch(self.trace, "branch X")
        except Exception as e:
            self.fail(f"get_all_trace_from_branch raised an exception for non-existing branch: {e}")

        content = self.output.getvalue()
        self.assertIn("Branch 'branch X' not found", content)


if __name__ == "__main__":
    unittest.main()
