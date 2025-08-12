class Step:
    def __init__(self, step_name, step_input, look_up_function, step_function, args, kwargs):
        self._step_name = step_name
        self._step_function = step_function
        self._step_input = step_input
        self._args = args
        self._kwargs = kwargs
        self._step_outputs = self._step_function(look_up_function, *args, **kwargs)

    def step_output(self):
        return self._step_outputs

    def info(self):
        return {
            "name": self._step_name,
            "input": self._step_input,
            "output": self._step_outputs,
            "args": self._args,
            "kwargs": self._kwargs or {}
        }