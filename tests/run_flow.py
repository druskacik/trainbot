import sys
import os
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.flows import daily_scraper_flow

if __name__ == "__main__":
    print("Running European Sleeper scraper flow directly...")
    daily_scraper_flow()
