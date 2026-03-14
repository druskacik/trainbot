import argparse
import sys
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.flows import daily_scraper_flow, european_sleeper_flow, nightjet_flow

FLOWS = {
    "european_sleeper": european_sleeper_flow,
    "nightjet": nightjet_flow,
    "daily": daily_scraper_flow,
}


def main():
    parser = argparse.ArgumentParser(description="Run a Prefect scraper flow.")
    parser.add_argument(
        "flow",
        choices=list(FLOWS.keys()),
        help="Which flow to run: european_sleeper, nightjet, or daily (both).",
    )
    args = parser.parse_args()
    flow_fn = FLOWS[args.flow]
    print(f"Running flow: {args.flow}")
    flow_fn()


if __name__ == "__main__":
    main()
