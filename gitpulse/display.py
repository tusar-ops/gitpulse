from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.columns import Columns
from rich import box
from contextlib import contextmanager


LANG_COLORS = {
    "Python": "yellow",
    "JavaScript": "bright_yellow",
    "TypeScript": "cyan",
    "Go": "bright_cyan",
    "Rust": "red",
    "Java": "bright_red",
    "C": "white",
    "C++": "bright_white",
    "C#": "magenta",
    "Ruby": "red",
    "PHP": "blue",
    "Swift": "bright_red",
    "Kotlin": "magenta",
    "Shell": "green",
    "HTML": "bright_red",
    "CSS": "blue",
    "Dart": "cyan",
    "Scala": "red",
}

HEATMAP_CHARS = [" ", "░", "▒", "▓", "█"]


class Display:
    def __init__(self):
        self.console = Console()

    def print_banner(self):
        banner = Text()
        banner.append("  ██████╗ ██╗████████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗\n", style="bold cyan")
        banner.append("  ██╔════╝ ██║╚══██╔══╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝\n", style="bold cyan")
        banner.append("  ██║  ███╗██║   ██║   ██████╔╝██║   ██║██║     ███████╗█████╗  \n", style="bold bright_cyan")
        banner.append("  ██║   ██║██║   ██║   ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  \n", style="bold bright_cyan")
        banner.append("  ╚██████╔╝██║   ██║   ██║     ╚██████╔╝███████╗███████║███████╗\n", style="bold white")
        banner.append("   ╚═════╝ ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝\n", style="bold white")
        banner.append("  GitHub Activity Analyzer · by gitpulse\n", style="dim")
        self.console.print(banner)

    @contextmanager
    def spinner(self, message: str):
        with Progress(
            SpinnerColumn(spinner_name="dots", style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(description=message, total=None)
            yield

    def print_error(self, msg: str):
        self.console.print(f"\n[bold red]✗ Error:[/] {msg}\n")

    def print_success(self, msg: str):
        self.console.print(f"\n[bold green]✓[/] {msg}\n")

    def print_profile(self, profile: dict):
        from datetime import datetime
        joined = ""
        if profile.get("created_at"):
            try:
                dt = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
                joined = dt.strftime("%b %Y")
            except Exception:
                pass

        lines = Text()
        lines.append(f"  {profile['name']}", style="bold white")
        if profile.get("login") != profile.get("name"):
            lines.append(f"  (@{profile['login']})", style="dim")
        lines.append("\n")
        lines.append(f"  {profile['bio']}\n", style="italic dim")
        lines.append(f"\n  📍 {profile['location']}   ", style="dim")
        lines.append(f"📅 Joined {joined}\n" if joined else "\n", style="dim")
        lines.append(f"\n  👥 {profile['followers']} followers  ", style="cyan")
        lines.append(f"· {profile['following']} following  ", style="dim")
        lines.append(f"· {profile['public_repos']} public repos\n", style="dim")

        self.console.print(Panel(lines, title="[bold cyan]Profile[/]", border_style="cyan", padding=(0, 1)))

    def print_language_breakdown(self, languages: dict):
        if not languages:
            return

        self.console.print("\n[bold cyan]  Language Breakdown[/]")
        self.console.print("  " + "─" * 48)

        for lang, pct in languages.items():
            color = LANG_COLORS.get(lang, "white")
            bar_len = int(pct / 2)  # max ~50 chars for 100%
            bar = "█" * bar_len
            self.console.print(
                f"  [bold {color}]{lang:<14}[/] [{color}]{bar:<25}[/] [dim]{pct}%[/]"
            )
        self.console.print()

    def print_top_repos(self, repos: list, top_n: int = 5):
        visible = [r for r in repos if not r.get("fork")][:top_n]
        if not visible:
            return

        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style="cyan",
            header_style="bold cyan",
            show_lines=False,
            padding=(0, 1),
        )
        table.add_column("Repository", style="bold white", min_width=24)
        table.add_column("⭐ Stars", justify="right", style="yellow")
        table.add_column("🍴 Forks", justify="right", style="blue")
        table.add_column("Language", style="green")
        table.add_column("Description", style="dim", max_width=36)

        for repo in visible:
            table.add_row(
                repo.get("name", ""),
                str(repo.get("stargazers_count", 0)),
                str(repo.get("forks_count", 0)),
                repo.get("language") or "—",
                (repo.get("description") or "—")[:60],
            )

        self.console.print(Panel(table, title="[bold cyan]Top Repositories[/]", border_style="cyan"))

    def print_commit_stats(self, stats: dict):
        if not stats:
            return

        self.console.print("[bold cyan]  Commit Activity[/]")
        self.console.print("  " + "─" * 48)
        self.console.print(f"  [white]Last 30 days:[/]  [bold yellow]{stats['last_30_days']}[/] commits")
        self.console.print(f"  [white]Last 365 days:[/] [bold yellow]{stats['last_365_days']}[/] commits")
        self.console.print(f"  [white]Active days:[/]   [bold yellow]{stats['active_days']}[/] days")
        self.console.print(f"  [white]Avg per day:[/]   [bold yellow]{stats['avg_per_active_day']}[/] commits/active day\n")

    def print_streak(self, streak: dict):
        if not streak:
            return

        self.console.print("[bold cyan]  Contribution Heatmap  [/][dim](last 30 days)[/]")
        self.console.print("  " + "─" * 48)

        heatmap = streak.get("heatmap", [])
        if heatmap:
            max_count = max(c for _, c in heatmap) or 1
            row = Text("  ")
            for date_str, count in heatmap:
                intensity = int((count / max_count) * 4) if count else 0
                char = HEATMAP_CHARS[intensity]
                if count == 0:
                    row.append(char + " ", style="dim")
                elif intensity == 4:
                    row.append(char + " ", style="bold green")
                elif intensity >= 2:
                    row.append(char + " ", style="green")
                else:
                    row.append(char + " ", style="dim green")
            self.console.print(row)

        self.console.print(
            f"\n  🔥 Current streak: [bold yellow]{streak['current']}[/] days  "
            f"  🏆 Longest streak: [bold yellow]{streak['longest']}[/] days\n"
        )

    def print_impact_score(self, score: int):
        bar_fill = int(score / 2)  # 50 chars = 100%
        bar_empty = 50 - bar_fill

        if score >= 70:
            color = "bold green"
            label = "High Impact 🚀"
        elif score >= 40:
            color = "bold yellow"
            label = "Growing 📈"
        else:
            color = "dim white"
            label = "Just Getting Started 🌱"

        bar = Text("  [")
        bar.append("█" * bar_fill, style=color)
        bar.append("░" * bar_empty, style="dim")
        bar.append(f"]  {score}/100  {label}")

        self.console.print("[bold cyan]  Impact Score[/]  [dim](stars · forks · followers · activity)[/]")
        self.console.print("  " + "─" * 48)
        self.console.print(bar)
        self.console.print()
