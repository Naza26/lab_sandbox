from ci_pipe.pipeline_data import PipelineData


class Step:
    def __init__(self, step_name, step_input, step_function):
        self._step_name = step_name
        self._step_function = step_function
        self._step_input = step_input
        self._step_outputs = self._step_function(step_input)

    def step_output(self):
        return self._step_outputs
