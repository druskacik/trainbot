from dataclasses import dataclass, field
from typing import List


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

    @property
    def success_count(self) -> int:
        return self.total_requests - len(self.failures)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100

    def failure_summary(self) -> str:
        """Returns a human-readable summary of the scrape run."""
        if not self.failures:
            return (
                f"✅ All {self.total_requests} requests succeeded. "
                f"{self.routes_scraped} routes scraped."
            )

        lines = [
            f"⚠️ {len(self.failures)}/{self.total_requests} requests failed "
            f"({self.success_rate:.1f}% success rate). "
            f"{self.routes_scraped} routes scraped."
        ]
        for f in self.failures:
            lines.append(f"  • {f.date} train {f.train_number}: {f.error}")
        return "\n".join(lines)
