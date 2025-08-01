from ci_pipe.step import Step

class CIPipe:
    def __init__(self, inputs):
        self._pipeline_inputs = inputs
        self._steps = []

    def output(self):
        return self.next_step_input()

    def step(self, step_name, step_function, *args):
        new_step = Step(step_name, self.next_step_input(), step_function, args)
        self._steps.append(new_step)
        return self

    def next_step_input(self):
        # Recheck
        if self._steps_are_empty():
            return self._pipeline_inputs
        return self._steps[-1].step_output()

    def _steps_are_empty(self):
        return len(self._steps) == 0

    def info(self):
        return {
            "steps": [step.info() for step in self._steps],
            "inputs": self._pipeline_inputs,
            "output": self.output()
        }