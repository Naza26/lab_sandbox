from ci_pipe.pipeline_data import PipelineData
from ci_pipe.step import Step
from ci_pipe.pipeline import CIPipe

class ISXPipeline(CIPipe):
    def __init__(self, isx, *inputs):
        self._pipeline_inputs = PipelineData(*inputs)
        self._steps = []
        self._isx = isx

    def read_movie(self, input_data):
        self.step("read_movie", self._isx.Movie.read)
        
