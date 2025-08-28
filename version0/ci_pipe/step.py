class Step:
    def __init__(self, step_name, step_input, look_up_function=None, step_function=None, args=None, kwargs=None, step_outputs=None):
        self._step_name = step_name
        self._step_function = step_function
        self._step_input = step_input
        self._args = args if args is not None else []
        self._kwargs = kwargs if kwargs is not None else {}
        # TODO: Make this more declarative
        if step_outputs is not None:
            self._step_outputs = step_outputs
        elif self._step_function is not None and look_up_function is not None:
            self._step_outputs = self._step_function(look_up_function, *self._args, **self._kwargs)
        else:
            self._step_outputs = None

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
