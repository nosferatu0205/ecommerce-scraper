"""
Category Scraper Module

Extracts all category URLs from the main website's BROWSE CATEGORIES menu.
"""

import asyncio
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from urllib.parse import urljoin


# Define the main top-level categories we want to scrape
# These are the primary categories visible in BROWSE CATEGORIES dropdown
MAIN_CATEGORY_IDS = {
    'HAIR': 'HAIR-456',
    'SKIN_CARE_BATH': 'SKIN-457', 
    'PARLOUR_EXCLUSIVE': 'PARLOUR-458',
    'MAKEUP': 'MAKEUP-459',
    'PERSONAL_CARE': 'PERSONAL-460',
    'SHAHNAZ_HUSAIN': 'SHAHNAZ-461',
}


async def get_categories(base_url: str) -> list[dict]:
    """
    Extract all category URLs from the website's navigation menu.
    
    Args:
        base_url: The base website URL (e.g., https://www.sinorbeauty.com/)
        
    Returns:
        List of dicts with 'name' and 'url' keys for each category
    """
    categories = []
    
    config = CrawlerRunConfig(
        wait_for="css:a[href*='/products/']",
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=base_url, config=config)
        
        if not result.success:
            print(f"Failed to fetch {base_url}: {result.error_message}")
            return categories
        
        soup = BeautifulSoup(result.html, 'lxml')
        
        # Find all links that point to /products/ pages (category pages)
        seen_categories = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Category URLs follow pattern: /products/CATEGORY-ID/
            if '/products/' in href:
                # Extract the category ID (e.g., HAIR-456)
                path = href.strip('/').split('/')
                if len(path) >= 2 and path[0] == 'products':
                    cat_id = path[1]  # e.g., "HAIR-456"
                    cat_name = cat_id.split('-')[0]  # e.g., "HAIR"
                    
                    # Only add if it's a main category URL (not subcategory)
                    # Main categories have format /products/{NAME}-{ID}/ with no additional path
                    if len(path) == 2 and cat_name not in seen_categories:
                        seen_categories.add(cat_name)
                        full_url = urljoin(base_url, f"/products/{cat_id}/")
                        categories.append({
                            'name': cat_name,
                            'url': full_url
                        })
    
    return categories


async def get_all_subcategories(base_url: str) -> list[dict]:
    """
    Extract ALL subcategory URLs for comprehensive scraping.
    This includes both main categories and their subcategories.
    
    Returns all unique category URLs found on the site.
    """
    all_categories = []
    
    config = CrawlerRunConfig(
        wait_for="css:a[href*='/products/']",
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=base_url, config=config)
        
        if not result.success:
            print(f"Failed to fetch {base_url}: {result.error_message}")
            return all_categories
        
        soup = BeautifulSoup(result.html, 'lxml')
        seen_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            if '/products/' in href:
                full_url = urljoin(base_url, href)
                
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # Extract category name from URL path
                    path = href.strip('/').split('/')
                    if len(path) >= 2:
                        cat_id = path[1]
                        cat_name = cat_id.split('-')[0]
                        
                        all_categories.append({
                            'name': cat_name,
                            'url': full_url
                        })
    
    return all_categories


if __name__ == "__main__":
    # Test the category scraper
    async def test():
        cats = await get_categories("https://www.sinorbeauty.com/")
        print(f"Found {len(cats)} main categories:")
        for cat in cats:
            print(f"  - {cat['name']}: {cat['url']}")
    
    asyncio.run(test())
