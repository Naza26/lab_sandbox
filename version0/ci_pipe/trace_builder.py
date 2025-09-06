from typing import List

from ci_pipe.step import Step


class TraceBuilder:
    @staticmethod
    def build_dictionary_trace_from(steps: List[Step]):
        trace = {}
        for step_index, step in enumerate(steps, 1):
            step_info = step.info()
            trace[str(step_index)] = {
                "algorithm": step_info["name"],
                "input": [item for v in step_info["input"].values() for item in v],
                "output": [item for v in step_info["output"].values() for item in v]
            }
        return trace

    @staticmethod
    def build_steps_from_trace(trace: dict):
        steps = []
        for step_number in sorted(trace, key=lambda x: int(x)):
            step_data = trace[step_number]
            step_name = step_data["algorithm"]
            step_input = {"input": step_data["input"]}
            step_output = {"output": step_data["output"]}
            step = Step.from_log(step_name, step_input, step_output)
            steps.append(step)
        return steps
