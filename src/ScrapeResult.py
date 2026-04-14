from dataclasses import dataclass, field
from typing import List

# Telegram messages are limited to 4096 chars; Apprise prepends the title to the
# body, so we leave ~190 chars of headroom for that.
TELEGRAM_BODY_LIMIT = 3900


def _cap_for_telegram(text: str) -> str:
    if len(text) <= TELEGRAM_BODY_LIMIT:
        return text
    return text[:TELEGRAM_BODY_LIMIT] + "\n… (trimmed)"


@dataclass
class ScrapeFailure:
    """Represents a single failed scrape request."""
    date: str
    train_number: str
    error: str


@dataclass
class ScrapeResult:
    """Holds the outcome of a scrape run, including successes and failures."""
    routes_scraped: int = 0
    failures: List[ScrapeFailure] = field(default_factory=list)
    total_requests: int = 0
    total_failures: int = 0  # Total failure count; may exceed len(failures) if list was capped
    scraper_name: str = ""

    @property
    def success_count(self) -> int:
        return self.total_requests - self._failure_count

    @property
    def _failure_count(self) -> int:
        """Number of failures to use for stats (total_failures if set, else len(failures))."""
        return self.total_failures if self.total_failures else len(self.failures)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100

    def failure_summary(self) -> str:
        """Returns a human-readable summary of the scrape run."""
        n_fail = self._failure_count
        if n_fail == 0:
            return (
                f"✅ All {self.total_requests} requests succeeded. "
                f"{self.routes_scraped} routes scraped."
            )

        lines = [
            f"⚠️ {n_fail}/{self.total_requests} requests failed "
            f"({self.success_rate:.1f}% success rate). "
            f"{self.routes_scraped} routes scraped."
        ]
        # Show a small sample (capped to stay under Telegram's 4096 char limit)
        for f in self.failures[:5]:
            lines.append(f"  • {f.date} train {f.train_number}: {f.error[:80]}")
        remaining = n_fail - min(len(self.failures), 5)
        if remaining > 0:
            lines.append(f"  … and {remaining} more.")
        return _cap_for_telegram("\n".join(lines))

    def _scraper_line(self) -> str:
        """One-line per-scraper summary for combined reports."""
        name = self.scraper_name or "Unknown"
        n_fail = self._failure_count
        if n_fail == 0:
            return f"  {name}: ✅ {self.total_requests}/{self.total_requests} OK — {self.routes_scraped} routes"
        return (
            f"  {name}: ⚠️ {n_fail}/{self.total_requests} failed "
            f"({self.success_rate:.1f}% success) — {self.routes_scraped} routes"
        )


def combined_failure_summary(results: List["ScrapeResult"]) -> str:
    """Build a notification body with per-scraper breakdowns."""
    total_req = sum(r.total_requests for r in results)
    total_fail = sum(r._failure_count for r in results)
    total_routes = sum(r.routes_scraped for r in results)

    if total_fail == 0:
        header = f"✅ All {total_req} requests succeeded. {total_routes} routes scraped."
    else:
        success_rate = ((total_req - total_fail) / total_req * 100) if total_req else 0.0
        header = (
            f"⚠️ {total_fail}/{total_req} requests failed "
            f"({success_rate:.1f}% success rate). {total_routes} routes scraped."
        )

    lines = [header, "", "Per scraper:"]
    for r in results:
        lines.append(r._scraper_line())

    # Show sample failures from all scrapers (capped to stay under Telegram's 4096 char limit)
    if total_fail:
        lines.append("")
        lines.append("Sample failures:")
        for r in results:
            for f in r.failures[:3]:
                name = r.scraper_name or "Unknown"
                lines.append(f"  • [{name}] {f.date} train {f.train_number}: {f.error[:80]}")
            remaining = r._failure_count - min(len(r.failures), 3)
            if remaining > 0:
                lines.append(f"  … and {remaining} more from {r.scraper_name}.")

    return _cap_for_telegram("\n".join(lines))
