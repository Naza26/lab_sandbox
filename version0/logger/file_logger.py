import json
import os
from graphviz import Digraph # type: ignore
from rich.console import Console # type: ignore
from anytree import Node, RenderTree # type: ignore


from utils import create_directory_from, build_filesystem_path_from


class FileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = cls.assert_file_can_be_created(filename, directory)
        return cls(path, directory)

    @classmethod
    def assert_file_can_be_created(cls, filename, directory):
        create_directory_from(directory)
        trace_path = build_filesystem_path_from(directory, filename)
        if not os.path.exists(trace_path):
            with open(trace_path, 'w') as f:
                f.write("{}")
        return trace_path

    def __init__(self, filepath, directory):
        self._filepath = filepath
        self._directory = directory


    def filepath(self):
        return self._filepath

    def directory(self):
        return self._directory

    def write_json_to_file(self, data):
        with open(self._filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def read_json_from_file(self):
        with open(self._filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def is_empty(self):
        return self.all_logs_as_json() == {}

    def add_log(self):
        pass

    def all_logs_as_json(self):
        with open(self._filepath, "r") as file:
            return json.load(file)
        

    def show(self):
        trace_json = self.all_logs_as_json()
        nodes = {}

        first_branch = list(trace_json.keys())[0]
        previous_node = None
        for step_num, step_info in sorted(trace_json[first_branch].items(), key=lambda x: int(x[0])):
            node_name = f"{first_branch}: step {step_num} - {step_info['algorithm']}"
            node = Node(node_name)
            nodes[(first_branch, step_num)] = node
            if previous_node:
                node.parent = previous_node
            previous_node = node

        for branch in list(trace_json.keys())[1:]:
            steps = sorted(trace_json[branch].items(), key=lambda x: int(x[0]))
            start_node = None

            for step_num, step_info in steps:
                outputs = step_info.get("output", [])

                if not any(branch in out for out in outputs):
                    continue

                node_name = f"{branch}: step {step_num} - {step_info['algorithm']}"
                node = Node(node_name)
                nodes[(branch, step_num)] = node

                if start_node is None:
                    inputs = step_info.get("input", [])
                    for inp in inputs:
                        for key, parent_node in nodes.items():
                            branch_key, step_key = key
                            if branch_key in inp and f"step {step_key}" in inp:
                                node.parent = parent_node
                                start_node = node
                                break
                        if start_node:
                            break
                    if start_node is None:
                        start_node = node
                else:
                    node.parent = start_node
                    start_node = node

        root = nodes[(first_branch, "1")]

        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")

        return root