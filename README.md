# Ecommerce Scraper

A Python web scraper that extracts product information from ecommerce websites using Crawl4AI.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
# Scrape all products from all categories
python main.py "https://www.sinorbeauty.com/"

# Scrape only a specific category
python main.py "https://www.sinorbeauty.com/" --category HAIR
```

## Output

Results are saved to the `output/` directory:
- `{CATEGORY_NAME}.csv` - Products per category
- `all_products.csv` - All products merged and deduplicated
