import json
import logging
import sys
import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, List
import typing

import groq
import typer
from rich.console import Console
from rich.panel import Panel

from gitpulse.core.repo_reader import get_activity, load_config
from gitpulse.core.summarise import format_activity, to_prompt_str, to_display_str, build_prompt, summarise
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
    default_tone = typer.prompt("Default tone (professional, casual, pirate, etc.)", default="professional")
    default_language = typer.prompt("Default language", default="English")

    # Construct TOML
    config_path = os.path.expanduser("~/.gitpulse.toml")
    
    toml_content = f"""# GitPulse Configuration
github_username = "{github_username}"

[defaults]
days = {default_days}
output = "{default_output}"
tone = "{default_tone}"
language = "{default_language}"

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
    tone: Optional[str] = typer.Option(None, "--tone", "-t", help="Tone of the summary (e.g. professional, casual)"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Language of the summary"),
    format: str = typer.Option("pretty", "--format", "-f", help="Output format: 'pretty' (default) or 'json'"),
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
            console.print(
                Panel(
                    "[bold red]Configuration Not Found[/bold red]\n\n"
                    "GitPulse requires a configuration file to know which repositories to scan.\n\n"
                    "[bold yellow]Resolution:[/bold yellow]\n"
                    "Run [bold cyan]gitpulse init[/bold cyan] to set up your configuration interactively.",
                    title="[bold red]Missing Config[/bold red]",
                    border_style="red",
                    expand=False,
                )
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(
                Panel(
                    f"Failed to load `~/.gitpulse.toml`.\n\n"
                    f"[bold yellow]Details:[/bold yellow]\n{e}\n\n"
                    "Please check the file syntax or run [bold cyan]gitpulse init[/bold cyan] to recreate it.",
                    title="[bold red]Invalid Config[/bold red]",
                    border_style="red",
                    expand=False,
                )
            )
            raise typer.Exit(1)

        defaults = config.get("defaults", {})
        
        # Priority: cli args > config defaults > hardcoded fallback
        active_days = days if days is not None else defaults.get("days", 7)
        active_output = output if output is not None else defaults.get("output", "output/summary.md")
        active_repo = repo if repo is not None else defaults.get("repo")
        active_tone = tone if tone is not None else defaults.get("tone", "professional")
        active_language = language if language is not None else defaults.get("language", "English")

        if active_repo:
            all_repos = config.get("repos", {})
            if active_repo not in all_repos:
                console.print(f"[bold red]Error:[/bold red] Repo '{active_repo}' not found in ~/.gitpulse.toml")
                raise typer.Exit(1)

        # Load environment and validate GROQ_API_KEY if not in dry-run
        try:
            load_env(check_keys=not dry_run)
        except EnvironmentError:
            console.print(
                Panel(
                    "Your [bold]GROQ_API_KEY[/bold] is not set in the environment.\n\n"
                    "[bold yellow]Resolution steps:[/bold yellow]\n"
                    "  1. Get a free API key from [link=https://console.groq.com]console.groq.com[/link]\n"
                    "  2. Set it in your terminal: [bold cyan]export GROQ_API_KEY=gsk_...[/bold cyan]\n"
                    "     — or add it to a [cyan].env[/cyan] file in your current directory.\n"
                    "  3. Re-run [bold cyan]gitpulse generate[/bold cyan]",
                    title="[bold red]Environment Error[/bold red]",
                    border_style="red",
                    expand=False,
                )
            )
            raise typer.Exit(1)

        # Fetch commits
        with console.status(f"[bold blue]Reading git history ({active_days} days)...[/bold blue]"):
            activity, errors = await get_activity(source="local", days=active_days)
            commits = activity.get("commits", [])
        
        if errors:
            for error in errors:
                console.print(f"[yellow]Warning:[/yellow] {error}")
        
        if active_repo:
            activity["commits"] = [c for c in activity.get("commits", []) if c["repo"] == active_repo]
            commits = activity["commits"]

        if not commits:
            console.print(f"[bold yellow]No commits found for the last {active_days} days.[/bold yellow] Try increasing [cyan]--days[/cyan].")
            raise typer.Exit(0)

        # Format and display local activity
        formatted_activity = format_activity(activity)
        console.print(Panel(to_display_str(formatted_activity), title="Local Git Activity", border_style="blue"))

        if dry_run:
            console.print("[bold yellow]Dry-run mode[/bold yellow] — skipping AI summarization.")
            raise typer.Exit(0)

        # Summarize via Groq
        with console.status("[bold green]Generating AI standup summary...[/bold green]"):
            prompt_str = to_prompt_str(formatted_activity)
            prompt = build_prompt(prompt_str, tone=active_tone, language=active_language)
            try:
                summary_text = await summarise(prompt)
            except groq.AuthenticationError:
                console.print(
                    Panel(
                        "[bold red]Authentication Failed[/bold red]\n\n"
                        "Your [bold]GROQ_API_KEY[/bold] was rejected by the Groq API (HTTP 401).\n\n"
                        "[bold yellow]Resolution steps:[/bold yellow]\n"
                        "  1. Get a valid key from [link=https://console.groq.com]console.groq.com[/link]\n"
                        "  2. Run: [bold cyan]export GROQ_API_KEY=gsk_...[/bold cyan]\n"
                        "     — or add it to your [cyan].env[/cyan] file in the project root\n"
                        "  3. Re-run [bold cyan]gitpulse generate[/bold cyan]",
                        title="[bold red]Groq Error[/bold red]",
                        border_style="red",
                        expand=False,
                    )
                )
                raise typer.Exit(1)

        # Display result
        if format == "json":
            payload = {
                "username": config.get("github_username", "unknown"),
                "repos": list(config.get("repos", {}).keys()) if not active_repo else [active_repo],
                "days": active_days,
                "summary": summary_text,
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            print(json.dumps(payload))  # noqa: T201 — intentional JSON output to stdout
        else:
            console.print("\n[bold green]Standup Summary:[/bold green]")
            console.print(summary_text)

        # Write to file
        os.makedirs(os.path.dirname(active_output) or "output", exist_ok=True)
        with open(active_output, "w") as f:
            f.write(summary_text)
        if format != "json":
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
        console.print("[bold cyan]GitPulse[/bold cyan] v1.6.0")
        console.print("Use [bold]gitpulse generate[/bold] to create a summary or [bold]gitpulse init[/bold] to set up.")
        # console.print(ctx.get_help())



@app.command(name="status")
def status():
    """Show current config, API key health, and API connectivity.

    A quick sanity check for new users and CI environments.
    """
    import httpx
    from rich.table import Table

    table = Table(title="GitPulse Status", show_header=True, header_style="bold cyan")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details", overflow="fold")

    # 1. Config file
    config_path = os.path.expanduser("~/.gitpulse.toml")
    if os.path.exists(config_path):
        table.add_row("Config file", "[green]\u2705 Found[/green]", config_path)
        try:
            config = load_config()
        except Exception:
            config = {}
    else:
        table.add_row("Config file", "[red]\u274c Missing[/red]", "Run 'gitpulse init' to create it")
        config = {}

    # 2. GROQ_API_KEY
    if os.getenv("GROQ_API_KEY"):
        table.add_row("GROQ_API_KEY", "[green]\u2705 Set[/green]", "")
    else:
        table.add_row("GROQ_API_KEY", "[red]\u274c Missing[/red]", "export GROQ_API_KEY=gsk_...")

    # 3. GITHUB_TOKEN
    if os.getenv("GITHUB_TOKEN"):
        table.add_row("GITHUB_TOKEN", "[green]\u2705 Set[/green]", "")
    else:
        table.add_row("GITHUB_TOKEN", "[yellow]\u26a0\ufe0f  Not set[/yellow]", "Rate limits apply (60 req/hr)")

    # 4. API reachability
    api_url = os.getenv("NEXT_PUBLIC_API_URL")
    if api_url:
        health_url = f"{api_url.rstrip('/')}/health"
        try:
            resp = httpx.get(health_url, timeout=3.0)
            if resp.status_code == 200:
                table.add_row("API health", "[green]\u2705 OK[/green]", health_url)
            else:
                table.add_row("API health", f"[yellow]\u26a0\ufe0f  HTTP {resp.status_code}[/yellow]", health_url)
        except Exception:
            table.add_row("API health", "[red]\u274c Unreachable[/red]", health_url)
    else:
        table.add_row("API health", "[dim]Skipped[/dim]", "NEXT_PUBLIC_API_URL not set")

    # 5. Repos from config
    repos = config.get("repos", {})
    if repos:
        repo_list = ", ".join(repos.keys())
        table.add_row("Configured repos", f"[cyan]{len(repos)} repo(s)[/cyan]", repo_list)
    else:
        table.add_row("Configured repos", "[dim]None[/dim]", "")

    # 6. Defaults
    defaults = config.get("defaults", {})
    if defaults:
        details = (
            f"days={defaults.get('days', 7)}, "
            f"tone={defaults.get('tone', 'professional')}, "
            f"lang={defaults.get('language', 'English')}"
        )
        table.add_row("Defaults", "[cyan]Set[/cyan]", details)
    else:
        table.add_row("Defaults", "[dim]Using built-in defaults[/dim]", "")

    console.print(table)

if __name__ == "__main__":
    app()