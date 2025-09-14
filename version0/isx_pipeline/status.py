from rich.console import Console # type: ignore
from rich.table import Table # type: ignore
from rich.panel import Panel # type: ignore
import json

import yaml

class Status:
    def __init__(self, trace):
        self._trace_file = trace

    def info(self, step_number, branch_name):
        console = Console()
        step_number = str(step_number)
        branch = branch_name 
        with open(self._trace_file) as f:
            trace = json.load(f)
        try:
            step = trace[branch][step_number]
        except KeyError:
            console.print(
                f"[bold red]❌ Step {step_number} not found in branch '{branch}'[/bold red]"
            )
            return
        table = Table(
            title=f"Step {step_number} Info",
            show_lines=True
        )
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="yellow")
        table.add_row("Algorithm", step.get("algorithm", ""))
        table.add_row("Input", "\n".join(step.get("input", [])))
        table.add_row("Output", "\n".join(step.get("output", [])))
        if "parameters" in step:
            params = "\n".join([f"{k}: {v}" for k, v in step["parameters"].items()])
            table.add_row("Parameters", params)
        console.print(table)

    def trace(self, branch_name):
        console = Console()
        try:
            with open(self._trace_file, "r") as f:
                full_trace = json.load(f)
            branch_trace = full_trace.get(branch_name)
            if branch_trace is None:
                console.print(f"[bold red]❌ Branch '{branch_name}' not found[/bold red]")
                return
        except Exception as e:
            console.print(f"[bold red]❌ Error loading trace: {e}[/bold red]")
            return

        steps_ordered = sorted(branch_trace.keys(), key=int)

        panels = []
        for step_number in steps_ordered:
            step_info = branch_trace[step_number]
            step_name = step_info.get("algorithm", f"Step {step_number}")
            panels.append(Panel(f"Step {step_number}\n{step_name}", padding=(1,2)))

        items = []
        for i, p in enumerate(panels):
            items.append(p)
            if i < len(panels) - 1:
                items.append("⬇")

        console.print(f"\n[bold underline]Pipeline Trace of branch: {branch_name}[/bold underline]\n")
        console.print(*items, justify="center")