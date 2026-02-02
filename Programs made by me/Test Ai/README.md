# AI Scraper Pipeline

A multi-agent AI system that scrapes web content and uses OpenAI to clean and structure the data into usable formats.

## Architecture

```
[Web URL] → [Scraper Agent] → Raw HTML/Text → [Cleaner Agent] → Structured JSON
```

- **Scraper Agent**: Uses `requests` + `BeautifulSoup` to fetch and parse web pages
- **Cleaner Agent**: Uses OpenAI API to intelligently extract and structure data

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the pipeline

```bash
# Interactive mode
python main.py

# With URL argument
python main.py https://example.com

# Extract specific data type
python main.py https://example.com/products --type products
```

## Usage Examples

### Basic usage (Python)

```python
from pipeline import Pipeline

pipeline = Pipeline(openai_api_key="your-key")
result = pipeline.process_url("https://example.com")
print(result)
```

### Extract specific data types

```python
# Extract product information
result = pipeline.process_url("https://shop.example.com", data_type="products")

# Extract article content
result = pipeline.process_url("https://news.example.com", data_type="articles")

# Extract contact information  
result = pipeline.process_url("https://company.example.com/contact", data_type="contacts")
```

### Custom extraction prompt

```python
result = pipeline.process_url(
    "https://example.com",
    custom_prompt="Extract all dates, prices, and person names mentioned on this page"
)
```

### Process multiple URLs

```python
urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]
results = pipeline.process_multiple_urls(urls, data_type="articles")
```

## Data Types

| Type | Extracts |
|------|----------|
| `products` | Names, prices, descriptions, availability |
| `articles` | Headlines, authors, dates, content |
| `contacts` | Names, emails, phones, addresses |
| `events` | Event names, dates, locations, descriptions |

## Output Format

Results are returned as JSON:

```json
{
  "title": "Page Title",
  "summary": "Brief summary of content",
  "main_content": "Key extracted information",
  "topics": ["topic1", "topic2"],
  "data_points": {
    "prices": ["$99.99"],
    "dates": ["2024-01-15"]
  },
  "_source_url": "https://example.com",
  "_processing_model": "gpt-4o-mini"
}
```

## Project Structure

```
ai-scraper-pipeline/
├── main.py              # CLI entry point
├── pipeline.py          # Orchestrates both agents
├── scraper_agent.py     # Web scraping functionality
├── cleaner_agent.py     # AI-powered data cleaning
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## License

MIT
