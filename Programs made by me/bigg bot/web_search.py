"""
Web Search Module for Chatbot
Provides free web search capabilities using DuckDuckGo and Wikipedia APIs
No API keys required!
"""

import urllib.request
import urllib.parse
import json
import re
import ssl

# Create SSL context that doesn't verify certificates (for some corporate networks)
try:
    ssl_context = ssl.create_default_context()
except:
    ssl_context = None


class WebSearch:
    """Handles web searches using free APIs"""
    
    def __init__(self):
        self.enabled = True
        self.timeout = 5  # seconds
        self.last_search = None
        self.cache = {}  # Simple cache to avoid repeated searches
        
    def search_duckduckgo(self, query):
        """
        Search using DuckDuckGo Instant Answer API (free, no key needed)
        Returns a summary/answer if available
        """
        try:
            # Clean and encode query
            query = query.strip()
            encoded_query = urllib.parse.quote(query)
            
            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(request, timeout=self.timeout, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Try to get the best answer
            if data.get('AbstractText'):
                return {
                    'source': 'DuckDuckGo',
                    'answer': data['AbstractText'],
                    'url': data.get('AbstractURL', ''),
                    'type': 'abstract'
                }
            
            if data.get('Answer'):
                return {
                    'source': 'DuckDuckGo',
                    'answer': data['Answer'],
                    'url': '',
                    'type': 'instant_answer'
                }
            
            # Check for definition
            if data.get('Definition'):
                return {
                    'source': data.get('DefinitionSource', 'DuckDuckGo'),
                    'answer': data['Definition'],
                    'url': data.get('DefinitionURL', ''),
                    'type': 'definition'
                }
            
            # Check related topics for a quick answer
            if data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                first_topic = data['RelatedTopics'][0]
                if isinstance(first_topic, dict) and first_topic.get('Text'):
                    return {
                        'source': 'DuckDuckGo',
                        'answer': first_topic['Text'],
                        'url': first_topic.get('FirstURL', ''),
                        'type': 'related'
                    }
            
            return None
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return None
    
    def search_wikipedia(self, query):
        """
        Search Wikipedia for information (free, no key needed)
        Returns a summary of the Wikipedia article
        """
        try:
            # Clean query
            query = query.strip()
            encoded_query = urllib.parse.quote(query)
            
            # Wikipedia API - search for the query first
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            
            request = urllib.request.Request(search_url)
            request.add_header('User-Agent', 'ChatBot/1.0 (Learning Project)')
            
            with urllib.request.urlopen(request, timeout=self.timeout, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get('extract'):
                # Limit length for chat
                extract = data['extract']
                if len(extract) > 500:
                    # Cut at sentence boundary
                    extract = extract[:500]
                    last_period = extract.rfind('.')
                    if last_period > 200:
                        extract = extract[:last_period + 1]
                
                return {
                    'source': 'Wikipedia',
                    'answer': extract,
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'type': 'wikipedia',
                    'title': data.get('title', query)
                }
            
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Page not found, try search API
                return self._wikipedia_search(query)
            return None
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None
    
    def _wikipedia_search(self, query):
        """Search Wikipedia when direct lookup fails"""
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded_query}&limit=1&format=json"
            
            request = urllib.request.Request(search_url)
            request.add_header('User-Agent', 'ChatBot/1.0 (Learning Project)')
            
            with urllib.request.urlopen(request, timeout=self.timeout, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # opensearch returns [query, [titles], [descriptions], [urls]]
            if len(data) >= 4 and data[1] and data[2]:
                if data[2][0]:  # Has description
                    return {
                        'source': 'Wikipedia',
                        'answer': data[2][0],
                        'url': data[3][0] if data[3] else '',
                        'type': 'wikipedia_search',
                        'title': data[1][0]
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def search(self, query):
        """
        Main search function - tries multiple sources
        Returns the best answer found
        """
        if not self.enabled:
            return None
        
        # Check cache first
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Extract search query from natural language
        search_query = self._extract_search_query(query)
        
        # Try DuckDuckGo first (faster, more general)
        result = self.search_duckduckgo(search_query)
        
        # If no result, try Wikipedia with the cleaned query
        if not result:
            result = self.search_wikipedia(search_query)
        
        # If still no result, try Wikipedia with just the main topic
        if not result:
            topic = self._extract_main_topic(query)
            if topic and topic != search_query:
                result = self.search_wikipedia(topic)
        
        # Last resort: try DuckDuckGo with just the topic
        if not result:
            topic = self._extract_main_topic(query)
            if topic and topic != search_query:
                result = self.search_duckduckgo(topic)
        
        # Cache the result
        if result:
            self.cache[cache_key] = result
            self.last_search = result
        
        return result
    
    def _extract_main_topic(self, text):
        """Extract the main noun/topic from a question"""
        text = text.lower().strip()
        
        # For "who invented X" questions, just extract the invention name
        invention_match = re.search(r'who\s+(invented|created|made|discovered|founded|built)\s+(?:the\s+)?(.+?)[\?]?$', text)
        if invention_match:
            invention = invention_match.group(2).strip()
            return invention  # Just return the thing itself, Wikipedia will have inventor info
        
        # Remove common question patterns more aggressively
        patterns = [
            r'^(what|who|where|when|why|how)\s+(is|are|was|were|do|does|did|can|could|would|will|to)\s+',
            r'^(tell me about|explain|define|describe)\s+',
            r'\s+(work|works|working|function|functions)\??$',
            r'\?+$',
        ]
        
        topic = text
        for pattern in patterns:
            topic = re.sub(pattern, '', topic, flags=re.IGNORECASE)
        
        # Remove articles
        topic = re.sub(r'^(the|a|an)\s+', '', topic.strip())
        
        return topic.strip()
    
    def _extract_search_query(self, text):
        """Extract the actual search query from natural language"""
        text = text.strip()
        
        # Remove question words and common phrases
        patterns_to_remove = [
            r'^(what is|what are|what\'s|whats)\s+',
            r'^(who is|who are|who\'s|whos)\s+',
            r'^(where is|where are|where\'s|wheres)\s+',
            r'^(when is|when are|when was|when were)\s+',
            r'^(why is|why are|why do|why does)\s+',
            r'^(how is|how are|how do|how does|how to)\s+',
            r'^(can you tell me about|tell me about|explain|define)\s+',
            r'^(do you know|i want to know)\s+',
            r'^(search for|look up|find)\s+',
            r'\?+$',
            r'^(the)\s+',
            r'^(a|an)\s+',
        ]
        
        search_query = text.lower()
        for pattern in patterns_to_remove:
            search_query = re.sub(pattern, '', search_query, flags=re.IGNORECASE)
        
        return search_query.strip() or text
    
    def should_search(self, text):
        """Determine if we should search the web for this query"""
        text_lower = text.lower().strip()
        
        # Keywords that suggest web search would help
        search_triggers = [
            'what is', 'what are', 'what\'s', 'whats',
            'who is', 'who are', 'who\'s', 'whos',
            'who invented', 'who created', 'who made', 'who discovered', 'who founded', 'who built',
            'where is', 'where are',
            'when is', 'when was', 'when did',
            'why is', 'why are', 'why do',
            'how does', 'how do', 'how to',
            'tell me about', 'explain',
            'define', 'meaning of',
            'search for', 'look up', 'find out',
            'do you know about', 'have you heard of',
            'what do you know about',
        ]
        
        # Check if it looks like a factual question
        for trigger in search_triggers:
            if trigger in text_lower:
                return True
        
        # Check if it's a question about a specific topic (capitalized words)
        if '?' in text or any(word[0].isupper() for word in text.split()[1:] if word):
            # Exclude personal questions
            personal_words = ['you', 'your', 'i', 'my', 'me', 'we', 'us']
            words = text_lower.split()
            if not any(pw in words[:3] for pw in personal_words):
                return True
        
        return False
    
    def format_response(self, result):
        """Format the search result into a chat-friendly response"""
        if not result:
            return None
        
        answer = result['answer']
        source = result['source']
        
        # Clean up the answer
        answer = answer.strip()
        
        # Add source attribution
        if result.get('title'):
            prefix = f"📚 **{result['title']}**: "
        else:
            prefix = "🔍 "
        
        response = f"{prefix}{answer}"
        
        # Add source note
        if source == 'Wikipedia':
            response += "\n\n_(Source: Wikipedia)_"
        elif source == 'DuckDuckGo':
            response += "\n\n_(Found via web search)_"
        
        return response


# Global instance for easy access
web_searcher = WebSearch()


def search_web(query):
    """Convenience function to search the web"""
    return web_searcher.search(query)


def format_search_result(result):
    """Convenience function to format search results"""
    return web_searcher.format_response(result)


if __name__ == "__main__":
    # Test the search
    searcher = WebSearch()
    
    test_queries = [
        "What is Python programming?",
        "Who is Albert Einstein?",
        "What is the capital of France?",
        "How does photosynthesis work?",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = searcher.search(query)
        if result:
            print(f"📖 Source: {result['source']}")
            print(f"💬 Answer: {result['answer'][:200]}...")
        else:
            print("❌ No result found")
