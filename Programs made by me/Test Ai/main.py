"""
AI Scraper Pipeline - Main Entry Point

A multi-agent system that:
1. Scrapes web content using ScraperAgent
2. Cleans and structures data using CleanerAgent (powered by OpenAI)

Usage:
    python main.py                          # Interactive mode
    python main.py <url>                    # Scrape single URL
    python main.py <url> --type products    # Extract specific data type
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
from pipeline import Pipeline


def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("=" * 50)
        print("ERROR: OpenAI API key not found!")
        print("=" * 50)
        print("\nPlease set up your API key:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to the .env file")
        print("\nGet an API key at: https://platform.openai.com/api-keys")
        return 1
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="AI-powered web scraper that extracts and structures data"
    )
    parser.add_argument("url", nargs="?", help="URL to scrape")
    parser.add_argument(
        "--type", "-t",
        choices=["products", "articles", "contacts", "events"],
        help="Type of data to extract"
    )
    parser.add_argument(
        "--output", "-o",
        default="output.json",
        help="Output file path (default: output.json)"
    )
    parser.add_argument(
        "--model", "-m",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = Pipeline(openai_api_key=api_key, model=args.model)
    
    # Interactive mode if no URL provided
    if not args.url:
        print("=" * 50)
        print("  AI Scraper Pipeline - Interactive Mode")
        print("=" * 50)
        print("\nThis tool scrapes web pages and uses AI to extract structured data.\n")
        
        url = input("Enter URL to scrape: ").strip()
        if not url:
            print("No URL provided. Exiting.")
            return 1
        
        print("\nData types: products, articles, contacts, events, or leave blank for auto")
        data_type = input("Enter data type (or press Enter for auto): ").strip() or None
        
        if data_type and data_type not in ["products", "articles", "contacts", "events"]:
            data_type = None
        
        args.url = url
        args.type = data_type
    
    # Process the URL
    print(f"\n🌐 Scraping: {args.url}")
    print(f"📊 Data type: {args.type or 'auto-detect'}")
    print(f"🤖 Model: {args.model}")
    print("-" * 50)
    
    result = pipeline.process_url(args.url, data_type=args.type)
    
    if result:
        # Display results
        print("\n" + "=" * 50)
        print("  EXTRACTED DATA")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        # Save to file
        pipeline.save_results(result, args.output)
        print(f"\n✅ Results saved to: {args.output}")
        return 0
    else:
        print("\n❌ Failed to process URL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
