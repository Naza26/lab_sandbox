import unittest

from isx_pipeline.isx_pipeline import ISXPipeline

class ISXDouble:
    pass


class ISXPipelineTestCase(unittest.TestCase): 
    def test_01(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = ISXPipeline(pipeline_raw_input)

        # Then
        self.assertEqual(pipeline.output(), [pipeline_raw_input])