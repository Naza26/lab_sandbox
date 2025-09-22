from rich.console import Console
from rich.table import Table
from rich.panel import Panel


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