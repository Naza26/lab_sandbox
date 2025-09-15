from ci_pipe.pipeline import CIPipe


class PipeMock(CIPipe):
    def __init__(self, inputs, _branch_name="branch 1", logger=None):
        super().__init__(inputs, branch_name=_branch_name)
        self._logger = logger