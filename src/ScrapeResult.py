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
    total_failures: int = 0  # Total failure count; may exceed len(failures) if list was capped

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
        # Show up to 20 sample failures to avoid huge notifications
        for f in self.failures[:20]:
            lines.append(f"  • {f.date} train {f.train_number}: {f.error}")
        if len(self.failures) < n_fail:
            lines.append(f"  … and {n_fail - len(self.failures)} more (list capped).")
        return "\n".join(lines)
