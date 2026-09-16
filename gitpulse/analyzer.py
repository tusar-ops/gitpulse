import requests
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta
from typing import Optional
import time


GITHUB_API = "https://api.github.com"


class GitHubAnalyzer:
    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

        self.profile = {}
        self.repos = []
        self.languages = {}
        self.commit_stats = {}
        self.streak_data = {}
        self.impact_score = 0

    def _get(self, url: str, params: dict = None) -> Optional[dict | list]:
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 404:
                return None
            if r.status_code == 403:
                raise RuntimeError("Rate limit hit. Use --token to increase limits.")
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            raise RuntimeError("No internet connection.")
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out.")

    def fetch_all(self) -> bool:
        user = self._get(f"{GITHUB_API}/users/{self.username}")
        if user is None:
            return False

        self.profile = {
            "login": user.get("login"),
            "name": user.get("name") or user.get("login"),
            "bio": user.get("bio") or "No bio provided.",
            "location": user.get("location") or "Unknown",
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "created_at": user.get("created_at", ""),
            "avatar_url": user.get("avatar_url", ""),
        }

        self._fetch_repos()
        self._fetch_languages()
        self._fetch_commit_stats()
        self._compute_streak()
        self._compute_impact_score()
        return True

    def _fetch_repos(self):
        repos = []
        page = 1
        while True:
            data = self._get(
                f"{GITHUB_API}/users/{self.username}/repos",
                params={"per_page": 100, "page": page, "sort": "updated"},
            )
            if not data:
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
            time.sleep(0.1)

        self.repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)

    def _fetch_languages(self):
        lang_totals = Counter()
        for repo in self.repos[:20]:  # cap to avoid hammering API
            if repo.get("fork"):
                continue
            langs = self._get(repo["languages_url"])
            if langs:
                lang_totals.update(langs)
            time.sleep(0.05)

        total_bytes = sum(lang_totals.values()) or 1
        self.languages = {
            lang: round((bytes_ / total_bytes) * 100, 1)
            for lang, bytes_ in lang_totals.most_common(8)
        }

    def _fetch_commit_stats(self):
        # NOTE: GitHub's Events API (/events/public) only returns events from
        # roughly the last 90 days (and caps out around 300 events total),
        # regardless of how far back we set year_ago. So "last_365_days" here
        # is really "last ~90 days, whatever the Events API gives us" — it
        # will undercount activity older than that window. The display layer
        # labels this accordingly instead of claiming a full year.
        now = datetime.now(timezone.utc)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)

        events = []
        page = 1
        while page <= 3:  # max 3 pages = 90 events
            data = self._get(
                f"{GITHUB_API}/users/{self.username}/events/public",
                params={"per_page": 30, "page": page},
            )
            if not data:
                break
            events.extend(data)
            if len(data) < 30:
                break
            page += 1
            time.sleep(0.1)

        push_events = [e for e in events if e.get("type") == "PushEvent"]

        commit_days = defaultdict(int)
        total_commits_month = 0
        total_commits_year = 0

        for event in push_events:
            created = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            commit_count = len(event.get("payload", {}).get("commits", []))

            if commit_count > 0:
                commit_days[created.date().isoformat()] += commit_count

            if created >= month_ago:
                total_commits_month += commit_count
            if created >= year_ago:
                total_commits_year += commit_count

        active_days = len(commit_days)
        avg_per_active_day = (
            round(total_commits_year / active_days, 1) if active_days else 0
        )

        self.commit_stats = {
            "last_30_days": total_commits_month,
            "last_365_days": total_commits_year,
            "active_days": active_days,
            "avg_per_active_day": avg_per_active_day,
            "commit_days": dict(commit_days),
        }

    def _compute_streak(self):
        commit_days = self.commit_stats.get("commit_days", {})
        if not commit_days:
            self.streak_data = {"current": 0, "longest": 0, "heatmap": []}
            return

        today = datetime.now(timezone.utc).date()
        sorted_days = sorted(commit_days.keys(), reverse=True)

        # current streak
        current = 0
        check = today
        for _ in range(365):
            if check.isoformat() in commit_days:
                current += 1
                check -= timedelta(days=1)
            else:
                if check == today:
                    check -= timedelta(days=1)
                    continue
                break

        # longest streak
        longest = 0
        streak = 0
        prev = None
        for day_str in sorted(commit_days.keys()):
            day = datetime.fromisoformat(day_str).date()
            if prev and (day - prev).days == 1:
                streak += 1
            else:
                streak = 1
            longest = max(longest, streak)
            prev = day

        # heatmap: last 30 days
        heatmap = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            count = commit_days.get(d.isoformat(), 0)
            heatmap.append((d.isoformat(), count))

        self.streak_data = {
            "current": current,
            "longest": longest,
            "heatmap": heatmap,
        }

    def _compute_impact_score(self):
        stars = sum(r.get("stargazers_count", 0) for r in self.repos)
        forks = sum(r.get("forks_count", 0) for r in self.repos)
        followers = self.profile.get("followers", 0)
        repos = self.profile.get("public_repos", 0)
        commits = self.commit_stats.get("last_365_days", 0)

        raw = (stars * 4) + (forks * 3) + (followers * 2) + (repos * 1) + (commits * 0.5)
        # normalize to 0–100 scale (soft cap at 500 raw → 100)
        self.impact_score = min(round((raw / 500) * 100), 100)

    def get_top_languages(self, limit: int = 3) -> list:
        """
        Returns the top detected languages as a plain list, e.g. ["Python", "JavaScript"].
        self.languages is already sorted by usage (highest % first), so this
        just takes the top `limit` keys. Used by jobs.py to build a job search query.
        """
        return list(self.languages.keys())[:limit]
