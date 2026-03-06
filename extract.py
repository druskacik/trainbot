import json

with open("100_scrape_europeansleeper.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

with open("scraper_code.py", "w", encoding="utf-8") as f:
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            f.write("".join(cell["source"]) + "\n\n")
