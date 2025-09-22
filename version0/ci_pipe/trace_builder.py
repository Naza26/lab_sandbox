from typing import List

from ci_pipe.step import Step

class TraceBuilder:
    @staticmethod
    def build_dictionary_trace_from(steps: List[Step], branch_name: str):
        trace = {branch_name: {}}
        for step_index, step in enumerate(steps, 1):
            step_input = step.input()
            step_output = step.output()
            trace[branch_name][str(step_index)] = {
                "algorithm": step.name(),
                "input": [item for v in step_input.values() for item in v],
                "output": [item for v in step_output.values() for item in v],
                "parameters": step._kwargs
            }
        return trace

    @staticmethod
    def build_steps_from_trace(trace: dict, branch_name: str):
        steps = []
        if branch_name not in trace:
            return steps

        branch_trace = trace[branch_name]
        for step_number in sorted(branch_trace, key=lambda x: int(x)):
            step_data = branch_trace[step_number]
            step_name = step_data["algorithm"]
            step_input = {"input": step_data["input"]}
            step_output = {"output": step_data["output"]}
            step = Step.from_log(step_name, step_input, step_output)
            steps.append(step)
        return steps