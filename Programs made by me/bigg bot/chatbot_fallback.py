"""
SmartFallback class - Handles unknown intents with intelligent keyword-based responses

This module uses a modular vocabulary system for faster loading and better maintainability.
The vocabulary is split into separate files in the fallback_vocab/ directory.
Now includes web search capabilities for factual questions!
"""
import re
import random
from fallback_vocab import get_all_responses

# Import web search module
try:
    from web_search import WebSearch
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    print("Warning: web_search.py not found. Web search disabled.")


class SmartFallback:
    """Handles unknown intents with intelligent responses"""

    def __init__(self):
        # Load keyword responses from modular vocabulary system
        # Python caches imported modules, so this is fast after first load
        self.keyword_responses = get_all_responses()
        
        # Initialize web search
        self.web_search = WebSearch() if WEB_SEARCH_AVAILABLE else None
        self.web_search_enabled = WEB_SEARCH_AVAILABLE

        # Generic responses for when no keywords match
        self.generic_responses = [
            "That's interesting! Tell me more.",
            "I see! What else is on your mind?",
            "Fascinating! Care to elaborate?",
            "Hmm, that's something to think about!",
            "I appreciate you sharing that!",
            "That's a unique perspective!",
            "I'm curious to hear more about that.",
            "What made you think of that?",
            "That's quite thought-provoking!",
            "I hadn't thought of it that way!",
            "You raise an interesting point!",
            "I'm all ears! Tell me more!",
            "That's new to me! Explain further?",
            "Interesting point! What else?",
            "I hadn't considered that before!",
        ]

        # Question responses when we detect a question
        self.question_fallbacks = [
            "That's a great question! I wish I knew the answer.",
            "Hmm, I'm not sure about that. What do you think?",
            "Good question! That's beyond what I know.",
            "I don't have that information, unfortunately.",
            "That's something I'd need to learn more about!",
            "Interesting question! Let me think...",
            "I'm not certain, but it's worth exploring!",
            "That stumped me! What's your take on it?",
            "Great question! I'd have to research that.",
            "I wish I had a better answer for you!",
        ]

    def extract_topic(self, text):
        """Extract the main topic/noun from text"""
        # Remove common words
        stop_words = {'i', 'me', 'my', 'you', 'your', 'the', 'a', 'an', 'is', 'are', 'was', 'were',
                      'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'to',
                      'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'about', 'into',
                      'it', 'its', 'this', 'that', 'these', 'those', 'what', 'which', 'who',
                      'whom', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
                      'and', 'but', 'or', 'not', 'no', 'so', 'if', 'then', 'than', 'too',
                      'very', 'just', 'also', 'now', 'here', 'there', 'really', 'think', 'know'}

        words = re.findall(r'\b\w+\b', text.lower())
        topics = [w for w in words if w not in stop_words and len(w) > 2]
        return topics[0] if topics else "that"

    def get_response(self, text):
        """Generate a response for unknown input"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Check if it's a question
        is_question = '?' in text or any(text_lower.startswith(w) for w in ['what', 'why', 'how', 'when', 'where', 'who', 'is', 'are', 'do', 'does', 'can', 'could', 'would', 'will'])

        # Try web search first for factual questions
        if self.web_search_enabled and self.web_search:
            if self.web_search.should_search(text):
                result = self.web_search.search(text)
                if result:
                    response = self.web_search.format_response(result)
                    if response:
                        return response

        # Look for keyword matches
        for word in words:
            if word in self.keyword_responses:
                return random.choice(self.keyword_responses[word])

        # Check for question words
        for qword in ['what', 'why', 'how', 'when', 'where', 'who']:
            if qword in words:
                topic = self.extract_topic(text)
                return random.choice(self.keyword_responses[qword]).format(topic=topic)

        # Use question fallback or generic
        if is_question:
            return random.choice(self.question_fallbacks)

        return random.choice(self.generic_responses)
    
    def toggle_web_search(self, enabled=None):
        """Enable or disable web search"""
        if enabled is None:
            self.web_search_enabled = not self.web_search_enabled
        else:
            self.web_search_enabled = enabled and WEB_SEARCH_AVAILABLE
        return self.web_search_enabled
    
    def is_web_search_available(self):
        """Check if web search is available"""
        return WEB_SEARCH_AVAILABLE
