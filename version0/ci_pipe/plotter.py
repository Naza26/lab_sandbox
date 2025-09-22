from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from anytree import Node, RenderTree



class Plotter:
    def __init__(self, console=None):
        self.console = console or Console()

    def get_step_info(self, trace, step_number, branch, show_parameters=True):
        step_number = str(step_number)
        step = self._get_step(trace, step_number, branch)
        if not step:
            return

        table = self._build_table(step_number, step, show_parameters)
        self.console.print(table)

    def _get_step(self, trace, step_number, branch):
        try:
            return trace[branch][step_number]
        except KeyError:
            self.console.print(f"[bold red]Step {step_number} not found in branch '{branch}'[/bold red]")
            return None

    def _build_table(self, step_number, step, show_parameters):
        table = Table(title=f"Step {step_number} Info", show_lines=True)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="yellow")
        table.add_row("Algorithm", step.get("algorithm", ""))
        table.add_row("Input", "\n".join(step.get("input", [])))
        table.add_row("Output", "\n".join(step.get("output", [])))

        if show_parameters and "parameters" in step:
            params = "\n".join(f"{k}: {v}" for k, v in step["parameters"].items())
            table.add_row("Parameters", params)

        return table
    
    def get_all_trace_from_branch(self, trace, branch):
        branch_trace = trace.get(branch)
        if not branch_trace:
            self.console.print(f"[bold red]Branch '{branch}' not found[/bold red]")
            return

        steps_ordered = sorted(branch_trace.keys(), key=int)
        items = self._build_trace_panels(branch_trace, steps_ordered)

        self.console.print(f"\n[bold underline]Pipeline Trace of branch: {branch}[/bold underline]\n")
        self.console.print(*items, justify="center")

    def _build_trace_panels(self, branch_trace, steps_ordered):
        panels = [
            Panel(
                f"Step {step_number}\n{branch_trace[step_number].get('algorithm', f'Step {step_number}')}",
                padding=(1, 2)
            )
            for step_number in steps_ordered
        ]

        items = []
        for i, p in enumerate(panels):
            items.append(p)
            if i < len(panels) - 1:
                items.append("⬇")
        return items
    
    def get_all_trace(self, trace, branch):
        self.convert_trace_to_tree(trace, branch)

    def convert_trace_to_tree(self, trace, highlight_branch=None):
        nodes = {}
        first_branch = list(trace.keys())[0]
        previous_node = None

        for step_num, step_info in sorted(trace[first_branch].items(), key=lambda x: int(x[0])):
            node_name = f"{first_branch}: step {step_num} - {step_info['algorithm']}"
            if highlight_branch and first_branch == highlight_branch:
                node_name = f"[yellow]{node_name}[/yellow]"
            node = Node(node_name)
            nodes[(first_branch, step_num)] = node
            if previous_node:
                node.parent = previous_node
            previous_node = node

        for branch in list(trace.keys())[1:]:
            steps = sorted(trace[branch].items(), key=lambda x: int(x[0]))
            start_node = None

            for step_num, step_info in steps:
                outputs = step_info.get("output", [])
                if not any(branch in out for out in outputs):
                    continue

                node_name = f"{branch}: step {step_num} - {step_info['algorithm']}"
                if highlight_branch and branch == highlight_branch:
                    node_name = f"[yellow]{node_name}[/yellow]"
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

        tree_lines = [f"{pre}{node.name}" for pre, _, node in RenderTree(root)]
        tree_str = "\n".join(tree_lines)

        console = Console()
        console.print(tree_str)

        return root