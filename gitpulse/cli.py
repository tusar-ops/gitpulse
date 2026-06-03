import argparse
import sys
from .analyzer import GitHubAnalyzer
from .display import Display


def main():
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="GitHub Activity Analyzer — beautiful terminal reports for any GitHub user",
    )
    parser.add_argument("username", help="GitHub username to analyze")
    parser.add_argument(
        "--token", "-t",
        help="GitHub personal access token (optional, increases rate limit)",
        default=None,
    )
    parser.add_argument(
        "--top", "-n",
        help="Number of top repos to show (default: 5)",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--export", "-e",
        help="Export report to a markdown file",
        metavar="FILE",
        default=None,
    )

    args = parser.parse_args()

    display = Display()
    display.print_banner()

    analyzer = GitHubAnalyzer(args.username, token=args.token)

    with display.spinner(f"Fetching data for [bold cyan]{args.username}[/]..."):
        success = analyzer.fetch_all()

    if not success:
        display.print_error(
            f"Could not fetch data for '{args.username}'. "
            "Check the username or add a --token to avoid rate limits."
        )
        sys.exit(1)

    display.print_profile(analyzer.profile)
    display.print_language_breakdown(analyzer.languages)
    display.print_top_repos(analyzer.repos, top_n=args.top)
    display.print_commit_stats(analyzer.commit_stats)
    display.print_streak(analyzer.streak_data)
    display.print_impact_score(analyzer.impact_score)

    if args.export:
        from .exporter import export_markdown
        export_markdown(args.export, analyzer)
        display.print_success(f"Report exported to [bold]{args.export}[/]")


if __name__ == "__main__":
    main()
