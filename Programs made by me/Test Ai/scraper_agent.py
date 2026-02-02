"""
Scraper Agent - Fetches and extracts raw content from web pages.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperAgent:
    """Agent responsible for scraping web content."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch raw HTML content from a URL."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML, removing scripts and styles."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
    
    def extract_links(self, html: str, base_url: str = "") -> list[dict]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            text = anchor.get_text(strip=True)
            links.append({
                'url': href,
                'text': text
            })
        
        return links
    
    def extract_metadata(self, html: str) -> dict:
        """Extract page metadata (title, description, etc.)."""
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            'title': '',
            'description': '',
            'keywords': ''
        }
        
        # Get title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Get meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content']
        
        # Get meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            metadata['keywords'] = keywords_tag['content']
        
        return metadata
    
    def scrape(self, url: str) -> Optional[dict]:
        """
        Main scraping method - fetches URL and extracts all content.
        
        Returns a dict with raw HTML, extracted text, links, and metadata.
        """
        html = self.fetch_url(url)
        if not html:
            return None
        
        return {
            'url': url,
            'raw_html': html,
            'text': self.extract_text(html),
            'links': self.extract_links(html, url),
            'metadata': self.extract_metadata(html)
        }


# Example usage
if __name__ == "__main__":
    scraper = ScraperAgent()
    result = scraper.scrape("https://example.com")
    
    if result:
        print(f"Title: {result['metadata']['title']}")
        print(f"Text preview: {result['text'][:500]}...")
        print(f"Found {len(result['links'])} links")
