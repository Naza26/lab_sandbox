from ci_pipe.step import Step

class CIPipe:
    def __init__(self, inputs):
        self._pipeline_inputs = inputs
        self._steps = []
        # TODO: read from file? here or ISX?
        self._defaults = {}

    def output(self):
        return self.next_step_input()

    def step(self, step_name, step_function, *args, **kwargs):
        kwargs = {**self._defaults, **kwargs}
        new_step = Step(step_name, self.next_step_input(), self.look_up_input, step_function, args, kwargs)
        self._steps.append(new_step)
        return self

    def next_step_input(self):
        if self._steps_are_empty():
            return self._pipeline_inputs
        return self._steps[-1].step_output()

    def look_up_input(self, key):
        for step in reversed(self._steps):
            if key in step.step_output():
                return step.step_output()[key]
        if key in self._pipeline_inputs:
            return self._pipeline_inputs[key]
        raise KeyError(f"Key '{key}' not found in any step output or pipeline input.")

    def _steps_are_empty(self):
        return len(self._steps) == 0

    def info(self):
        return {
            "steps": [step.info() for step in self._steps],
            "inputs": self._pipeline_inputs,
            "output": self.output(),
            "defaults": self._defaults
        }

    def set_defaults(self, **defaults):
        self._load_defaults(defaults)
        return self

    def _load_defaults(self, defaults):
        for defaults_key, defaults_value in defaults.items():
            self._defaults[defaults_key] = defaults_value
