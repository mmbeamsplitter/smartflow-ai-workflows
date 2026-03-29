"""
SmartFlow CLI - Command-line interface for managing workflows
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import Workflow, create_workflow


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SmartFlow AI - Universal AI-Powered Workflow Automation Platform"""
    pass


@cli.command()
@click.option("--name", prompt="Workflow name", help="Name of the workflow")
@click.option("--description", default="", help="Workflow description")
def create(name: str, description: str):
    """Create a new workflow"""
    workflow = create_workflow(name=name, description=description)

    console.print(f"[green]✓[/green] Created workflow: {name}")
    console.print(f"  Description: {description}")
    console.print(f"\nNext steps:")
    console.print(f"  1. Add steps using the workflow.add_step() method")
    console.print(f"  2. Validate with workflow.validate()")
    console.print(f"  3. Run with workflow.run(**context)")


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--context", type=click.Path(exists=True), help="JSON context file")
def run(workflow_file: str, context: str = None):
    """Run a workflow from a Python file"""
    console.print(f"[blue]Running workflow:[/blue] {workflow_file}")

    # Load workflow module
    workflow_path = Path(workflow_file)
    if not workflow_path.exists():
        console.print(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
        return

    # Load context if provided
    ctx = {}
    if context:
        try:
            with open(context, 'r') as f:
                ctx = json.load(f)
            console.print(f"[green]✓[/green] Loaded context from {context}")
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not load context: {e}")

    # Import and run workflow
    try:
        # This is a simple example - real implementation would load and execute
        console.print(f"[yellow]Note:[/yellow] Import-based workflow execution requires workflow to have a run_workflow() function")
        console.print(f"For direct usage, import the module in Python:")
        console.print(f"  from {workflow_path.stem} import create_workflow")
        console.print(f"  workflow = create_workflow()")
        console.print(f"  result = workflow.run(**{ctx})")

    except Exception as e:
        console.print(f"[red]Error running workflow:[/red] {e}")


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
def validate(workflow_file: str):
    """Validate a workflow configuration"""
    console.print(f"[blue]Validating workflow:[/blue] {workflow_file}")

    try:
        # Simple validation check
        workflow_path = Path(workflow_file)
        if workflow_path.suffix != ".py":
            console.print(f"[red]Error:[/red] Workflow file must be a Python .py file")
            return

        with open(workflow_file, 'r') as f:
            content = f.read()

        # Check for workflow definition
        has_workflow = "Workflow(" in content or "create_workflow" in content
        has_steps = "add_step" in content

        console.print(f"\nWorkflow structure:")
        console.print(f"  has_workflow: [green]{has_workflow}[/green]" if has_workflow else f"  has_workflow: [red]{has_workflow}[/red]")
        console.print(f"  has_steps: [green]{has_steps}[/green]" if has_steps else f"  has_steps: [red]{has_steps}[/red]")

        if has_workflow and has_steps:
            console.print(f"\n[green]✓[/green] Workflow appears valid")
        else:
            console.print(f"\n[yellow]⚠[/yellow] Workflow may be incomplete")

    except Exception as e:
        console.print(f"[red]Error validating workflow:[/red] {e}")


@cli.command()
def examples():
    """List available example workflows"""
    examples_dir = Path(__file__).parent.parent / "examples"

    table = Table(title="Available Example Workflows")
    table.add_column("File", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Use Case", style="yellow")

    examples = [
        ("devops_incident_response.py", "GitHub issue automated response", "DevOps"),
        ("healthcare_document_processing.py", "HIPAA-compliant document analysis", "Healthcare"),
        ("ecommerce_support.py", "Intelligent customer support automation", "E-commerce"),
    ]

    for filename, description, use_case in examples:
        file_path = examples_dir / filename
        exists = file_path.exists()
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        table.add_row(f"{status} {filename}", description, use_case)

    console.print(table)

    console.print(f"\nRun examples with:")
    console.print(f"  python {examples_dir}/devops_incident_response.py")
    console.print(f"  python {examples_dir}/healthcare_document_processing.py")
    console.print(f"  python {examples_dir}/ecommerce_support.py")


@cli.command()
def version():
    """Show version information"""
    panel = Panel(
        f"SmartFlow AI v0.1.0\n\n"
        f"Universal AI-Powered Workflow Automation Platform\n\n"
        f"Features:\n"
        f"• AI-enhanced multi-step workflows\n"
        f"• Universal API integration\n"
        f"• Natural language workflow definition\n"
        f"• Smart decision-making\n"
        f"• Real-time execution monitoring",
        title="SmartFlow AI",
        border_style="blue"
    )
    console.print(panel)


@cli.command()
@click.argument("context_file", type=click.Path(exists=True))
def context(context_file: str):
    """Show workflow context from JSON file"""
    try:
        with open(context_file, 'r') as f:
            ctx = json.load(f)

        console.print(f"[blue]Variables in context:[/blue]\n")
        for key, value in ctx.items():
            console.print(f"  [cyan]{key}:[/cyan] {value}")

    except Exception as e:
        console.print(f"[red]Error reading context:[/red] {e}")


if __name__ == "__main__":
    cli()