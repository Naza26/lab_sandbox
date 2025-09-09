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
    def build_steps_from_trace(trace: dict, branch_name: str):
        if branch_name and branch_name in trace:
            steps_data = trace[branch_name]
        else:
            if len(trace) == 1 and isinstance(next(iter(trace.values())), dict):
                steps_data = next(iter(trace.values()))
            else:
                raise ValueError("El trace no corresponde a una rama válida")
        
        steps = []
        for step_number in sorted(steps_data, key=lambda x: int(x)):
            step_data = steps_data[step_number]
            step_name = step_data["algorithm"]
            steps.append(Step(step_name, step_data))
        return steps