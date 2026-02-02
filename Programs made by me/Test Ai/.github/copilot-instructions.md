# AI Scraper Pipeline - Copilot Instructions

## Project Overview
A multi-agent AI pipeline that scrapes web content and uses an LLM to clean/structure the data.

## Architecture
- **ScraperAgent**: Fetches raw HTML/text from URLs using requests + BeautifulSoup
- **CleanerAgent**: Uses OpenAI API to extract structured data from raw content

## Key Files
- `scraper_agent.py` - Web scraping functionality
- `cleaner_agent.py` - AI-powered data cleaning
- `pipeline.py` - Orchestrates the two agents
- `main.py` - Entry point with example usage

## Development Guidelines
- Always use environment variables for API keys
- Handle rate limiting and errors gracefully
- Log scraping activities for debugging
