"""
Chatbot utility classes: MarkovTextGenerator and ConversationMemory
"""
import pickle
import os
import re
import random
from datetime import datetime
from collections import defaultdict


class MarkovTextGenerator:
    """Generates new sentences by learning word patterns"""
    
    def __init__(self, order=2):
        self.order = order  # How many words to look back
        self.chains = defaultdict(lambda: defaultdict(list))  # intent -> chain
        self.starters = defaultdict(list)  # Starting words per intent
    
    def tokenize(self, text):
        """Split text into words"""
        text = text.lower()
        words = re.findall(r'\b\w+\b|[.!?]', text)
        return words
    
    def train(self, intent, texts):
        """Learn patterns from a list of texts for an intent"""
        for text in texts:
            words = self.tokenize(text)
            if len(words) < self.order:
                continue
            
            # Store sentence starters
            starter = tuple(words[:self.order])
            if starter not in self.starters[intent]:
                self.starters[intent].append(starter)
            
            # Build chain
            for i in range(len(words) - self.order):
                key = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                if next_word not in self.chains[intent][key]:
                    self.chains[intent][key].append(next_word)
    
    def generate(self, intent, max_length=20):
        """Generate a new sentence for an intent"""
        if intent not in self.starters or not self.starters[intent]:
            return None
        
        # Start with a random beginning
        words = list(random.choice(self.starters[intent]))
        
        for _ in range(max_length):
            key = tuple(words[-self.order:])
            if key not in self.chains[intent]:
                break
            
            next_words = self.chains[intent][key]
            if not next_words:
                break
            
            next_word = random.choice(next_words)
            words.append(next_word)
            
            # Stop at sentence end
            if next_word in '.!?':
                break
        
        # Capitalize and format
        sentence = ' '.join(words)
        sentence = sentence.replace(' .', '.').replace(' !', '!').replace(' ?', '?')
        sentence = sentence.capitalize()
        return sentence
    
    def train_from_responses(self, responses_dict):
        """Train on all responses"""
        for intent, texts in responses_dict.items():
            self.train(intent, texts)


class ConversationMemory:
    def __init__(self):
        self.user_name = None
        self.conversation_history = []
        self.topics_discussed = []
        self.user_facts = {}  # Store facts about the user
        self.message_count = 0
        self.session_start = datetime.now()
    
    def add_message(self, role, text, intent=None):
        self.message_count += 1
        self.conversation_history.append({
            'role': role,
            'text': text,
            'intent': intent,
            'time': datetime.now()
        })
        if intent and intent not in self.topics_discussed:
            self.topics_discussed.append(intent)
    
    def get_last_intent(self):
        for msg in reversed(self.conversation_history):
            if msg['role'] == 'user' and msg['intent']:
                return msg['intent']
        return None
    
    def get_last_user_message(self):
        for msg in reversed(self.conversation_history):
            if msg['role'] == 'user':
                return msg['text']
        return None
    
    def extract_name(self, text):
        # Skip if this looks like a request/command rather than name introduction
        skip_phrases = ['call me a ', 'call me an ', 'call me the ', 'call me that', 
                        'call me this', 'call me back', 'call me later', 'call me when',
                        'call me if', 'call me maybe', 'call me something', 'call me anything']
        text_lower = text.lower()
        for phrase in skip_phrases:
            if phrase in text_lower:
                return None
        
        patterns = [
            r"my name is ([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",  # captures first name and optional last name
            r"i am ([A-Z][a-z]+)",  # Only capitalized names (likely a proper name)
            r"im ([A-Z][a-z]+)",    # Only capitalized names
            r"call me ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # Only capitalized (proper names)
            r"i'm ([A-Z][a-z]+)",   # Only capitalized names
            r"(?:you can )?call me ([a-zA-Z]+)$",  # name at end of sentence
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Filter out common words that aren't names
                non_names = {'a', 'an', 'the', 'good', 'bad', 'nice', 'pretty', 'handsome', 
                            'beautiful', 'ugly', 'stupid', 'smart', 'dumb', 'idiot', 'genius',
                            'boy', 'girl', 'man', 'woman', 'person', 'human', 'friend', 'dude',
                            'bro', 'sis', 'mate', 'buddy', 'pal', 'sir', 'maam', 'boss', 
                            'chief', 'captain', 'doctor', 'maybe', 'later', 'back', 'anything',
                            'something', 'crazy', 'lazy', 'silly', 'funny'}
                if name.lower() in non_names:
                    return None
                return name.capitalize()
        return None
    
    def extract_fact(self, text):
        """Extract facts from user statements"""
        patterns = [
            (r"i (?:really )?like (\w+(?:\s+\w+)?)", "like"),
            (r"i (?:really )?love (\w+(?:\s+\w+)?)", "love"),
            (r"i (?:really )?hate (\w+(?:\s+\w+)?)", "hate"),
            (r"my favorite (\w+) is (\w+(?:\s+\w+)?)", "favorite"),
            (r"i am (?:a |an )?(\w+)", "identity"),
            (r"i work as (?:a |an )?(\w+)", "job"),
            (r"i live in (\w+(?:\s+\w+)?)", "location"),
            (r"i have (?:a |an )?(\w+)", "possession"),
        ]
        for pattern, fact_type in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if fact_type == "favorite":
                    return (fact_type, match.group(1), match.group(2))
                return (fact_type, match.group(1))
        return None
    
    def store_fact(self, fact_tuple):
        """Store a fact about the user"""
        if fact_tuple:
            if fact_tuple[0] == "favorite":
                key = f"favorite_{fact_tuple[1]}"
                self.user_facts[key] = fact_tuple[2]
            else:
                self.user_facts[fact_tuple[0]] = fact_tuple[1]
    
    def get_fact_response(self, fact_tuple):
        """Generate a response acknowledging a fact"""
        responses = {
            "like": [
                "Oh, you like {0}? That's cool!",
                "Nice! {0} is interesting!",
                "I'll remember that you like {0}!"
            ],
            "love": [
                "You love {0}? That's wonderful!",
                "{0} must be really special to you!",
                "I can tell {0} means a lot to you!"
            ],
            "hate": [
                "Oh, you're not a fan of {0}? I understand.",
                "Noted! You don't like {0}.",
                "I'll remember that {0} isn't your thing."
            ],
            "favorite": [
                "So your favorite {0} is {1}? Great choice!",
                "{1} is your favorite {0}? I'll remember that!",
                "Nice! {1} is a good {0}!"
            ],
            "identity": [
                "Oh, you're a {0}? That's interesting!",
                "Being a {0} sounds cool!",
                "A {0}? Tell me more about that!"
            ],
            "job": [
                "Working as a {0}? That sounds interesting!",
                "A {0}! How do you like that job?",
                "I'll remember you work as a {0}!"
            ],
            "location": [
                "You live in {0}? What's it like there?",
                "{0} sounds like a nice place!",
                "I'll remember you're from {0}!"
            ],
            "possession": [
                "You have a {0}? Cool!",
                "A {0}! That's nice!",
                "I'll remember you have a {0}!"
            ]
        }
        if fact_tuple and fact_tuple[0] in responses:
            template = random.choice(responses[fact_tuple[0]])
            if fact_tuple[0] == "favorite":
                return template.format(fact_tuple[1], fact_tuple[2])
            return template.format(fact_tuple[1])
        return None
    
    def save(self, filename):
        data = {
            'user_name': self.user_name,
            'user_facts': self.user_facts,
            'topics_discussed': self.topics_discussed
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            self.user_name = data.get('user_name')
            self.user_facts = data.get('user_facts', {})
            self.topics_discussed = data.get('topics_discussed', [])
            return True
        return False
