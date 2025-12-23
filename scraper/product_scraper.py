"""
Product Scraper Module

Scrapes all products from a category page by handling the "View More" pagination.
Uses Playwright directly for reliable session-based clicking.
"""

import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin


async def scrape_products(category_url: str, category_name: str, max_clicks: int = 100) -> list[dict]:
    """
    Scrape all products from a category page.
    
    Handles "View More" button pagination by clicking until no more products load.
    
    Args:
        category_url: URL of the category page
        category_name: Name of the category for output
        max_clicks: Maximum number of "View More" clicks (safety limit)
        
    Returns:
        List of dicts with 'name', 'url', and 'category' keys
    """
    products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to category page
            await page.goto(category_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(1)  # Let page settle
            
            # Get initial product count
            prev_count = await _count_products(page)
            print(f"[{category_name}] Initial load: {prev_count} products")
            
            # Click "View More" until no more products load
            for click_num in range(max_clicks):
                # Check if View More button exists
                view_more = await page.query_selector('._ilmPaging, .view-more, [class*="load-more"]')
                
                if not view_more:
                    print(f"[{category_name}] No more 'View More' button found")
                    break
                
                # Scroll to button and click
                await view_more.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
                await view_more.click()
                
                # Wait for new products to load
                await asyncio.sleep(1.5)
                
                # Count products after click
                new_count = await _count_products(page)
                print(f"[{category_name}] After click {click_num + 1}: {new_count} products")
                
                # If no new products loaded, we're done
                if new_count <= prev_count:
                    print(f"[{category_name}] No new products loaded, finished")
                    break
                
                prev_count = new_count
            
            # Extract all products from the fully loaded page
            html = await page.content()
            products = _extract_products_from_html(html, category_url, category_name)
            
        except Exception as e:
            print(f"[{category_name}] Error: {e}")
        finally:
            await browser.close()
    
    return products


async def _count_products(page) -> int:
    """Count products on the page."""
    # Count product links to /details/
    count = await page.evaluate('''
        () => document.querySelectorAll('a[href*="/details/"]').length
    ''')
    return count


def _extract_products_from_html(html: str, base_url: str, category_name: str) -> list[dict]:
    """
    Extract product names and URLs from HTML content.
    """
    products = []
    seen_urls = set()
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Find all product links (pattern: /details/product-slug/product-id/)
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        
        if '/details/' in href:
            full_url = urljoin(base_url, href)
            
            # Skip duplicates
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            # Try to get product name from h5 tag inside the link
            name_tag = link.find('h5')
            if name_tag:
                name = name_tag.get_text(strip=True)
            else:
                # Fallback: get any text from the link
                name = link.get_text(strip=True)
            
            # If still no name, extract from URL
            if not name:
                match = re.search(r'/details/([^/]+)/', href)
                if match:
                    name = match.group(1).replace('-', ' ')
            
            if name:
                products.append({
                    'name': name,
                    'url': full_url,
                    'category': category_name
                })
    
    return products


if __name__ == "__main__":
    # Test the product scraper on a single category
    async def test():
        products = await scrape_products(
            "https://www.sinorbeauty.com/products/HAIR-456/",
            "HAIR"
        )
        print(f"\nFound {len(products)} products:")
        for p in products[:10]:  # Show first 10
            print(f"  - {p['name']}: {p['url']}")
    
    asyncio.run(test())
