# 🔍 GitPulse

**Beautiful terminal reports for any GitHub profile.**

GitPulse is a Python CLI tool that analyzes any GitHub user's activity and displays a rich, color-coded report right in your terminal — language breakdown, top repositories, commit streaks, contribution heatmap, impact score, and matching job listings powered by SerpApi.

```
gitpulse torvalds
gitpulse gvanrossum --top 10
gitpulse yourusername --export report.md
gitpulse yourusername --jobs
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
- **Job Matching** — pulls live job listings from Google Jobs (via SerpApi) that match your detected tech stack
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

**Editable install (for development)**
```bash
pip install -e .
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
  --jobs                Fetch matching job listings via SerpApi (Google Jobs)
                         based on your detected tech stack
  --location LOCATION   Location for job search (default: India)
  -h, --help             Show help
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

# See jobs matching your detected tech stack
gitpulse yourusername --jobs

# Job search in a specific location
gitpulse yourusername --jobs --location "Bangalore"
```

---

## 🔑 GitHub Token (Optional but Recommended)

Without a token, GitHub allows 60 API requests/hour. A free personal access token raises this to **5,000/hour**.

1. Go to [GitHub Settings → Developer Settings → Tokens (classic)](https://github.com/settings/tokens)
2. Generate a new token with **no scopes** (read-only public data is enough)
3. Use it with `gitpulse username --token YOUR_TOKEN`

---

## 💼 SerpApi Key (Required for `--jobs`)

The `--jobs` flag uses SerpApi's Google Jobs engine to find listings matching your top detected languages. It needs a free SerpApi key.

1. Sign up free at [serpapi.com](https://serpapi.com/) — the free tier includes 250 searches/month
2. Copy your key from **Your Account → API Key**
3. Copy `.env.example` to `.env` in the project root and paste your key:
   ```
   SERPAPI_KEY=your_key_here
   ```
4. `.env` is already in `.gitignore` — never commit your real key

---

## 🧱 Project Structure

```
gitpulse/
├── gitpulse/
│   ├── __init__.py
│   ├── cli.py          # Argument parsing & orchestration
│   ├── analyzer.py     # GitHub API fetching & data processing
│   ├── display.py      # Rich terminal UI
│   ├── exporter.py     # Markdown export
│   └── jobs.py         # SerpApi Google Jobs integration
├── requirements.txt
├── .env.example         # Template for your SerpApi key
├── setup.py
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.8+**
- [`requests`](https://pypi.org/project/requests/) — GitHub REST API & SerpApi calls
- [`rich`](https://github.com/Textualize/rich) — terminal formatting, tables, progress spinners
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) — loads SerpApi key from `.env`
- [SerpApi](https://serpapi.com/) — Google Jobs search results

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built with Python · Powered by the GitHub REST API and SerpApi*
