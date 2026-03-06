import sys
from src.EuropeanSleeperScraper import EuropeanSleeperScraper

def main():
    print("Starting European Sleeper Scraper...")
    scraper = EuropeanSleeperScraper()
    
    # Scrape data
    routes = scraper.scrape()
    
    # Save to database
    if routes:
        scraper.save_routes(routes)
    else:
        print("No routes were found.")

if __name__ == "__main__":
    main()
