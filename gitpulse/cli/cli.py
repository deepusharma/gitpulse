import logging
import sys
import os
import asyncio
from typing import Optional, List
import typing

import typer
from rich.console import Console
from rich.panel import Panel

from gitpulse.core.repo_reader import get_commits, load_config
from gitpulse.core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise
from gitpulse.core.utils import load_env

# Initialize Typer and Rich
app = typer.Typer(help="GitPulse — AI-powered standup summary generator", no_args_is_help=True)
console = Console()
logger = logging.getLogger("gitpulse")

def setup_logging(debug: bool):
    """Setup logging level."""
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=log_level, format="%(message)s")

@app.command()
def init():
    """
    Interactively initialize GitPulse configuration (~/.gitpulse.toml).
    """
    console.print(Panel("[bold cyan]Welcome to GitPulse Setup[/bold cyan]\nLet's configure your local standup generator.", expand=False))

    github_username = typer.prompt("Enter your GitHub username (for web/api context)")
    
    # Prompt for local repository paths
    repos = {}
    console.print("\n[bold yellow]Configure Repository Paths[/bold yellow]")
    console.print("Add local directories you want to track.")
    
    while True:
        repo_name = typer.prompt("Repo name")
        repo_path = typer.prompt("Repo path (absolute or relative to current dir)")
        repos[repo_name] = os.path.abspath(os.path.expanduser(repo_path))
        
        if not typer.confirm("Add another repository?", default=False):
            break

    # Set defaults
    console.print("\n[bold yellow]Set Summarization Defaults[/bold yellow]")
    default_days = typer.prompt("Default lookback days", default=7, type=int)
    default_output = typer.prompt("Default output file", default="output/summary.md")

    # Construct TOML
    config_path = os.path.expanduser("~/.gitpulse.toml")
    
    toml_content = f"""# GitPulse Configuration
github_username = "{github_username}"

[defaults]
days = {default_days}
output = "{default_output}"

[repos]
"""
    for name, path in repos.items():
        toml_content += f'{name} = "{path}"\n'

    # Save config
    try:
        with open(config_path, "w") as f:
            f.write(toml_content)
        console.print(f"\n[bold green]Success![/bold green] Configuration saved to [bold]{config_path}[/bold]")
    except Exception as e:
        console.print(f"\n[bold red]Error saving config:[/bold red] {e}")
        raise typer.Exit(1)

    # Check for GROQ_API_KEY
    if not os.getenv("GROQ_API_KEY"):
        console.print("\n[bold yellow]Final Step:[/bold yellow]")
        console.print("Please ensure your [bold]GROQ_API_KEY[/bold] is set in your environment.")
        console.print("You can add it to your [cyan].env[/cyan] file or export it: [cyan]export GROQ_API_KEY=re_xxx[/cyan]")

@app.command(name="generate")
def generate(
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Number of days to look back"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Filter by specific repo name from config"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show commits without calling Groq API"),
):
    """
    Generate a standup summary based on your git history.
    """
    setup_logging(debug)
    
    async def _run():
        try:
            config = load_config()
        except FileNotFoundError:
            console.print("[bold red]Error:[/bold red] ~/.gitpulse.toml not found.")
            console.print("Run [bold cyan]gitpulse init[/bold cyan] to set up your configuration.")
            raise typer.Exit(1)

        defaults = config.get("defaults", {})
        
        # Priority: cli args > config defaults > hardcoded fallback
        active_days = days if days is not None else defaults.get("days", 7)
        active_output = output if output is not None else defaults.get("output", "output/summary.md")
        active_repo = repo if repo is not None else defaults.get("repo")

        if active_repo:
            all_repos = config.get("repos", {})
            if active_repo not in all_repos:
                console.print(f"[bold red]Error:[/bold red] Repo '{active_repo}' not found in ~/.gitpulse.toml")
                raise typer.Exit(1)

        # Load environment and validate GROQ_API_KEY if not in dry-run
        try:
            load_env(check_keys=not dry_run)
        except EnvironmentError:
            console.print("[bold red]Error:[/bold red] GROQ_API_KEY not set. Check your environment or .env file.")
            raise typer.Exit(1)

        # Fetch commits
        with console.status(f"[bold blue]Reading git history ({active_days} days)...[/bold blue]"):
            commits, errors = await get_commits(source="local", days=active_days)
        
        if errors:
            for error in errors:
                console.print(f"[yellow]Warning:[/yellow] {error}")
        
        if active_repo:
            commits = [c for c in commits if c["repo"] == active_repo]

        if not commits:
            console.print(f"[bold yellow]No commits found for the last {active_days} days.[/bold yellow] Try increasing [cyan]--days[/cyan].")
            raise typer.Exit(0)

        # Format and display local commits
        formatted_commits = format_commits(commits)
        console.print(Panel(to_display_str(formatted_commits), title="Local Git History", border_style="blue"))

        if dry_run:
            console.print("[bold yellow]Dry-run mode[/bold yellow] — skipping AI summarization.")
            raise typer.Exit(0)

        # Summarize via Groq
        with console.status("[bold green]Generating AI standup summary...[/bold green]"):
            prompt_str = to_prompt_str(formatted_commits)
            prompt = build_prompt(prompt_str)
            summary = await summarise(prompt)

        # Display result
        console.print("\n[bold green]Standup Summary:[/bold green]")
        console.print(summary)

        # Write to file
        os.makedirs(os.path.dirname(active_output) or "output", exist_ok=True)
        with open(active_output, "w") as f:
            f.write(summary)
        console.print(f"\n[dim]Summary written to {active_output}[/dim]")

    # Run the async logic
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If a loop is already running (e.g. in tests), create a task or run it
        # In pytest-anyio context, we can just await the coroutine from the test
        # but the CLI function itself is sync. So we use a runner.
        task = loop.create_task(_run())
        # This is tricky in a sync function.
        # For tests, we'll change the tests to be synchronous.
    else:
        asyncio.run(_run())

# Support running help by default if no subcommand is provided
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Subcommand router. Default behavior is to show help if no command specified.
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]GitPulse[/bold cyan] v0.7.0")
        console.print("Use [bold]gitpulse generate[/bold] to create a summary or [bold]gitpulse init[/bold] to set up.")
        # console.print(ctx.get_help())

if __name__ == "__main__":
    app()