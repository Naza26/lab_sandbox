from rich.console import Console # type: ignore
from rich.table import Table # type: ignore
from rich.panel import Panel # type: ignore

class Plotter:
    def __init__(self):
        pass

    def get_step_info(self, trace, step_number, branch):
        console = Console()
        step_number = str(step_number)
        print(trace)
        try:
            step = trace[branch][step_number]
        except KeyError:
            console.print(
                f"[bold red] Step {step_number} not found in branch '{branch}'[/bold red]"
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