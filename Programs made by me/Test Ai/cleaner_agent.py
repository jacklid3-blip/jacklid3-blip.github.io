"""
Cleaner Agent - Uses AI to clean and structure scraped data.
"""

import json
import logging
from typing import Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CleanerAgent:
    """Agent responsible for cleaning and structuring scraped data using AI."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def clean_and_structure(
        self, 
        raw_data: dict, 
        extraction_schema: Optional[dict] = None,
        custom_prompt: Optional[str] = None
    ) -> dict:
        """
        Clean and structure raw scraped data using AI.
        
        Args:
            raw_data: The raw scraped data from ScraperAgent
            extraction_schema: Optional JSON schema describing desired output format
            custom_prompt: Optional custom instructions for extraction
        
        Returns:
            Structured, cleaned data as a dictionary
        """
        # Build the prompt
        system_prompt = """You are a data extraction and cleaning AI. Your job is to:
1. Extract relevant information from raw web content
2. Remove noise, ads, and irrelevant content
3. Structure the data in a clean, usable JSON format
4. Preserve important information while removing duplicates

Always respond with valid JSON only, no explanations or markdown."""

        # Prepare the content to send
        content_to_clean = {
            'url': raw_data.get('url', ''),
            'title': raw_data.get('metadata', {}).get('title', ''),
            'description': raw_data.get('metadata', {}).get('description', ''),
            'text_content': raw_data.get('text', '')[:8000],  # Limit text length
        }
        
        # Build user prompt
        if custom_prompt:
            user_prompt = f"""{custom_prompt}

Raw data to process:
{json.dumps(content_to_clean, indent=2)}"""
        elif extraction_schema:
            user_prompt = f"""Extract data according to this schema:
{json.dumps(extraction_schema, indent=2)}

Raw data to process:
{json.dumps(content_to_clean, indent=2)}"""
        else:
            user_prompt = f"""Extract and structure the main content from this webpage data. 
Return a JSON object with these fields:
- title: The page title
- summary: A brief summary of the content (2-3 sentences)
- main_content: The key information/text from the page
- topics: List of main topics/keywords
- data_points: Any structured data found (prices, dates, names, etc.)

Raw data to process:
{json.dumps(content_to_clean, indent=2)}"""

        try:
            logger.info(f"Sending to AI for cleaning: {raw_data.get('url', 'unknown')}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            cleaned_data = json.loads(result_text)
            
            # Add metadata
            cleaned_data['_source_url'] = raw_data.get('url', '')
            cleaned_data['_processing_model'] = self.model
            
            logger.info("Successfully cleaned and structured data")
            return cleaned_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return {"error": "Failed to parse response", "raw_response": result_text}
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return {"error": str(e)}
    
    def extract_specific_data(self, raw_data: dict, data_type: str) -> dict:
        """
        Extract specific types of data from scraped content.
        
        Args:
            raw_data: The raw scraped data
            data_type: Type of data to extract (e.g., 'products', 'articles', 'contacts')
        """
        prompts = {
            'products': """Extract product information including:
- Product names
- Prices (with currency)
- Descriptions
- Availability/stock status
- Any specifications or features""",
            
            'articles': """Extract article information including:
- Headline/title
- Author name
- Publication date
- Article body/summary
- Categories/tags""",
            
            'contacts': """Extract contact information including:
- Names
- Email addresses
- Phone numbers
- Addresses
- Social media links""",
            
            'events': """Extract event information including:
- Event name
- Date and time
- Location/venue
- Description
- Ticket prices or registration info"""
        }
        
        custom_prompt = prompts.get(data_type, f"Extract all {data_type} related information.")
        return self.clean_and_structure(raw_data, custom_prompt=custom_prompt)


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("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")
    
    if api_key:
        cleaner = CleanerAgent(api_key=api_key)
        
        # Example raw data
        sample_data = {
            'url': 'https://example.com/product',
            'metadata': {'title': 'Sample Product Page'},
            'text': 'iPhone 15 Pro - $999.99 - In Stock. Features: A17 chip, titanium design...'
        }
        
        result = cleaner.clean_and_structure(sample_data)
        print(json.dumps(result, indent=2))
    else:
        print("Please set OPENAI_API_KEY in your .env file")
