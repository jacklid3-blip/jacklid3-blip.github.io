"""
AI Scraper Pipeline - Orchestrates scraping and cleaning agents.
"""

import json
import logging
from typing import Optional
from scraper_agent import ScraperAgent
from cleaner_agent import CleanerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the scraper and cleaner agents."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.scraper = ScraperAgent()
        self.cleaner = CleanerAgent(api_key=openai_api_key, model=model)
    
    def process_url(
        self, 
        url: str, 
        data_type: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[dict]:
        """
        Complete pipeline: scrape URL and clean the data.
        
        Args:
            url: The URL to scrape
            data_type: Optional type of data to extract ('products', 'articles', 'contacts', 'events')
            custom_prompt: Optional custom extraction instructions
        
        Returns:
            Cleaned, structured data or None if failed
        """
        # Step 1: Scrape the URL
        logger.info(f"=== PIPELINE START: {url} ===")
        logger.info("Step 1: Scraping...")
        
        raw_data = self.scraper.scrape(url)
        if not raw_data:
            logger.error("Scraping failed")
            return None
        
        logger.info(f"Scraped {len(raw_data['text'])} chars of text, {len(raw_data['links'])} links")
        
        # Step 2: Clean and structure with AI
        logger.info("Step 2: Cleaning with AI...")
        
        if data_type:
            cleaned_data = self.cleaner.extract_specific_data(raw_data, data_type)
        elif custom_prompt:
            cleaned_data = self.cleaner.clean_and_structure(raw_data, custom_prompt=custom_prompt)
        else:
            cleaned_data = self.cleaner.clean_and_structure(raw_data)
        
        logger.info("=== PIPELINE COMPLETE ===")
        return cleaned_data
    
    def process_multiple_urls(
        self, 
        urls: list[str], 
        data_type: Optional[str] = None
    ) -> list[dict]:
        """
        Process multiple URLs and return all results.
        
        Args:
            urls: List of URLs to process
            data_type: Optional type of data to extract
        
        Returns:
            List of cleaned data dictionaries
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}")
            result = self.process_url(url, data_type=data_type)
            if result:
                results.append(result)
        
        return results
    
    def save_results(self, data: dict | list, filename: str = "output.json"):
        """Save results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {filename}")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: Please set OPENAI_API_KEY in your .env file")
        exit(1)
    
    # Initialize the pipeline
    pipeline = Pipeline(openai_api_key=api_key)
    
    # Example: Process a single URL
    result = pipeline.process_url("https://example.com")
    
    if result:
        print("\n=== CLEANED DATA ===")
        print(json.dumps(result, indent=2))
        
        # Save to file
        pipeline.save_results(result, "output.json")
