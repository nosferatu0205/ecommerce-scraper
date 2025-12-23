"""
Ecommerce Scraper

Main entry point for scraping product information from ecommerce websites.

Usage:
    python main.py "https://www.sinorbeauty.com/"
    python main.py "https://www.sinorbeauty.com/" --category HAIR
"""

import argparse
import asyncio
import csv
import os
from pathlib import Path

from scraper.category_scraper import get_categories
from scraper.product_scraper import scrape_products


async def main(base_url: str, category_filter: str = None):
    """
    Main scraping function.
    
    Args:
        base_url: Base website URL
        category_filter: Optional category name to scrape only that category
    """
    print(f"🕷️ Ecommerce Scraper")
    print(f"   Target: {base_url}")
    print()
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Discover categories
    print("📂 Discovering categories...")
    categories = await get_categories(base_url)
    
    if not categories:
        print("❌ No categories found!")
        return
    
    print(f"   Found {len(categories)} categories:")
    for cat in categories:
        print(f"      - {cat['name']}")
    print()
    
    # Filter to specific category if requested
    if category_filter:
        categories = [c for c in categories if c['name'].upper() == category_filter.upper()]
        if not categories:
            print(f"❌ Category '{category_filter}' not found!")
            return
        print(f"   Filtering to: {category_filter}")
        print()
    
    # Step 2: Scrape products from each category
    all_products = []
    
    for cat in categories:
        print(f"🛍️ Scraping {cat['name']}...")
        products = await scrape_products(cat['url'], cat['name'])
        
        if products:
            # Save category-specific CSV
            cat_file = output_dir / f"{cat['name'].replace(' ', '_').replace('&', 'AND')}.csv"
            save_to_csv(products, cat_file)
            print(f"   ✅ Saved {len(products)} products to {cat_file}")
            
            all_products.extend(products)
        else:
            print(f"   ⚠️ No products found in {cat['name']}")
        
        print()
    
    # Step 3: Merge and deduplicate
    print("📊 Merging and deduplicating...")
    unique_products = deduplicate_products(all_products)
    
    # Save merged CSV
    all_file = output_dir / "all_products.csv"
    save_to_csv(unique_products, all_file)
    
    print(f"   Total products: {len(all_products)}")
    print(f"   Unique products: {len(unique_products)}")
    print(f"   ✅ Saved to {all_file}")
    print()
    print("🎉 Done!")


def save_to_csv(products: list[dict], filepath: Path):
    """Save products to a CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url', 'category', 'price'])
        writer.writeheader()
        writer.writerows(products)


def deduplicate_products(products: list[dict]) -> list[dict]:
    """Remove duplicate products based on URL."""
    seen_urls = set()
    unique = []
    
    for product in products:
        if product['url'] not in seen_urls:
            seen_urls.add(product['url'])
            unique.append(product)
    
    return unique


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape product information from ecommerce websites"
    )
    parser.add_argument(
        "url",
        help="Base website URL (e.g., https://www.sinorbeauty.com/)"
    )
    parser.add_argument(
        "--category", "-c",
        help="Scrape only a specific category (e.g., HAIR)",
        default=None
    )
    
    args = parser.parse_args()
    
    asyncio.run(main(args.url, args.category))
