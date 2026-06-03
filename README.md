# 🔍 GitPulse

**Beautiful terminal reports for any GitHub profile.**

GitPulse is a Python CLI tool that analyzes any GitHub user's activity and displays a rich, color-coded report right in your terminal — language breakdown, top repositories, commit streaks, contribution heatmap, and an impact score.

```
gitpulse torvalds
gitpulse gvanrossum --top 10
gitpulse yourusername --export report.md
```

---

## ✨ Features

- **Profile Summary** — name, bio, location, followers, repo count
- **Language Breakdown** — percentage bars for top 8 languages across non-forked repos
- **Top Repositories** — sorted by stars, with forks and language info
- **Commit Activity** — last 30 days, last year, average per active day
- **Contribution Heatmap** — ASCII heatmap of the last 30 days
- **Streak Tracker** — current and longest commit streaks
- **Impact Score** — composite score (0–100) based on stars, forks, followers, and activity
- **Markdown Export** — save the report as a `.md` file

---

## 📦 Installation

**Option 1 — pip (recommended)**
```bash
pip install .
```

**Option 2 — run directly**
```bash
pip install -r requirements.txt
python -m gitpulse.cli <username>
```

---

## 🚀 Usage

```
gitpulse <username> [options]

Arguments:
  username              GitHub username to analyze

Options:
  -t, --token TOKEN     GitHub personal access token (raises rate limit to 5000 req/hr)
  -n, --top N           Number of top repos to display (default: 5)
  -e, --export FILE     Export report to a Markdown file
  -h, --help            Show help
```

### Examples

```bash
# Analyze any public profile
gitpulse torvalds

# Use a token to avoid rate limiting
gitpulse yourusername --token ghp_xxxxxxxxxxxx

# Show top 10 repos
gitpulse yourusername --top 10

# Export to markdown
gitpulse yourusername --export report.md
```

---

## 🔑 GitHub Token (Optional but Recommended)

Without a token, GitHub allows 60 API requests/hour. A free personal access token raises this to **5,000/hour**.

1. Go to [GitHub Settings → Developer Settings → Tokens (classic)](https://github.com/settings/tokens)
2. Generate a new token with **no scopes** (read-only public data is enough)
3. Use it with `gitpulse username --token YOUR_TOKEN`

---

## 🧱 Project Structure

```
gitpulse/
├── gitpulse/
│   ├── __init__.py
│   ├── cli.py          # Argument parsing & orchestration
│   ├── analyzer.py     # GitHub API fetching & data processing
│   ├── display.py      # Rich terminal UI
│   └── exporter.py     # Markdown export
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.8+**
- [`requests`](https://pypi.org/project/requests/) — GitHub REST API calls
- [`rich`](https://github.com/Textualize/rich) — terminal formatting, tables, progress spinners

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built with Python · Powered by the GitHub REST API*
