"""
Conversational Learning Module for Neural Chatbot
Enables the bot to learn from conversations and become more human-like
"""
import json
import os
import random
import re
from datetime import datetime, timedelta
from collections import defaultdict


class PersonalityEngine:
    """Gives the bot a more human-like personality with mood and traits"""
    
    def __init__(self):
        self.mood = 0.7  # 0 = sad, 1 = happy (starts slightly positive)
        self.energy = 0.8  # 0 = tired, 1 = energetic
        self.engagement = 0.5  # How engaged in conversation
        
        # Personality traits (0-1 scale)
        self.traits = {
            'friendliness': 0.8,
            'humor': 0.6,
            'curiosity': 0.7,
            'empathy': 0.75,
            'formality': 0.3,  # Lower = more casual
            'verbosity': 0.5   # How much detail in responses
        }
        
        # Mood modifiers based on conversation
        self.positive_triggers = ['thank', 'love', 'great', 'awesome', 'amazing', 'good', 
                                  'wonderful', 'excellent', 'happy', 'like', 'best', 'cool']
        self.negative_triggers = ['hate', 'bad', 'terrible', 'awful', 'stupid', 'dumb',
                                  'boring', 'worst', 'angry', 'sad', 'annoying', 'suck']
        
        # Conversation starters and fillers for natural speech
        self.thinking_phrases = [
            "Hmm, ", "Let me think... ", "Well, ", "You know, ", "Interesting... ",
            "Ah, ", "Oh! ", "Actually, ", "So, ", "I see... "
        ]
        
        self.acknowledgments = [
            "I hear you!", "I understand.", "Got it!", "Makes sense.",
            "I see what you mean.", "That's interesting!", "Noted!"
        ]
        
        self.empathy_phrases = [
            "I can imagine how you feel.", "That sounds {emotion}.",
            "I'm here for you.", "Tell me more about that.",
            "That must be {emotion} for you."
        ]
    
    def update_mood(self, text):
        """Update mood based on conversation content"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_triggers if word in text_lower)
        negative_count = sum(1 for word in self.negative_triggers if word in text_lower)
        
        # Mood shifts gradually
        mood_change = (positive_count - negative_count) * 0.05
        self.mood = max(0, min(1, self.mood + mood_change))
        
        # Energy decreases slightly over time but engagement increases
        self.engagement = min(1, self.engagement + 0.02)
        
        return self.mood
    
    def get_mood_prefix(self):
        """Get a mood-appropriate prefix for responses"""
        if self.mood > 0.8:
            prefixes = ["😊 ", "Great! ", "Wonderful! ", "I'm glad! ", ""]
        elif self.mood > 0.5:
            prefixes = ["", "", "Sure! ", "Alright, ", ""]
        elif self.mood > 0.3:
            prefixes = ["", "Well... ", "Hmm, ", ""]
        else:
            prefixes = ["I see... ", "Oh... ", "", ""]
        
        return random.choice(prefixes) if random.random() < 0.3 else ""
    
    def add_personality_flair(self, response):
        """Add personality touches to a response"""
        # Maybe add a thinking phrase
        if random.random() < 0.15 and self.traits['verbosity'] > 0.4:
            response = random.choice(self.thinking_phrases) + response[0].lower() + response[1:]
        
        # Add emoji based on mood and friendliness
        if random.random() < self.traits['friendliness'] * 0.3:
            if self.mood > 0.7:
                emojis = ['😊', '🙂', '✨', '👍', '💫']
            elif self.mood > 0.4:
                emojis = ['🙂', '👌', '']
            else:
                emojis = ['🤔', '']
            
            emoji = random.choice(emojis)
            if emoji and not any(e in response for e in ['😊', '🙂', '😄', '👍']):
                response = response.rstrip('!.') + ' ' + emoji
        
        return response
    
    def get_curious_followup(self):
        """Generate a curious follow-up question"""
        if random.random() < self.traits['curiosity'] * 0.5:
            followups = [
                " What made you think of that?",
                " Can you tell me more?",
                " That's interesting - why do you say that?",
                " I'm curious to know more!",
                " What else can you share about that?",
                ""
            ]
            return random.choice(followups)
        return ""


class ConversationalLearner:
    """Learns new patterns and responses from conversations"""
    
    def __init__(self, save_file="learned_data.json"):
        self.save_file = save_file
        
        # Learned patterns: maps user inputs to good responses
        self.learned_responses = defaultdict(list)
        
        # User corrections: when user says "that's wrong" or teaches
        self.corrections = []
        
        # New phrases for existing intents
        self.learned_phrases = defaultdict(list)
        
        # Completely new intents discovered
        self.new_intents = {}
        
        # Positive/negative feedback tracking
        self.response_feedback = defaultdict(lambda: {'positive': 0, 'negative': 0})
        
        # Conversation patterns for natural flow
        self.conversation_flows = defaultdict(list)  # intent -> likely follow-up intents
        
        # Teaching mode state
        self.teaching_mode = False
        self.pending_learning = None
        
        self.load()
    
    def save(self):
        """Save learned data to file"""
        data = {
            'learned_responses': dict(self.learned_responses),
            'corrections': self.corrections,
            'learned_phrases': dict(self.learned_phrases),
            'new_intents': self.new_intents,
            'response_feedback': {k: dict(v) for k, v in self.response_feedback.items()},
            'conversation_flows': dict(self.conversation_flows)
        }
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving learned data: {e}")
    
    def load(self):
        """Load previously learned data"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.learned_responses = defaultdict(list, data.get('learned_responses', {}))
                self.corrections = data.get('corrections', [])
                self.learned_phrases = defaultdict(list, data.get('learned_phrases', {}))
                self.new_intents = data.get('new_intents', {})
                self.response_feedback = defaultdict(
                    lambda: {'positive': 0, 'negative': 0},
                    {k: v for k, v in data.get('response_feedback', {}).items()}
                )
                self.conversation_flows = defaultdict(list, data.get('conversation_flows', {}))
                return True
            except Exception as e:
                print(f"Error loading learned data: {e}")
        return False
    
    def normalize_text(self, text):
        """Normalize text for comparison"""
        return re.sub(r'[^\w\s]', '', text.lower()).strip()
    
    def detect_teaching_intent(self, text):
        """Check if user is trying to teach the bot"""
        text_lower = text.lower()
        
        teaching_patterns = [
            r"when (?:someone|i|people) (?:say|says|ask|asks) ['\"]?(.+?)['\"]?,? (?:you should |say |respond with |reply with )['\"]?(.+)['\"]?",
            r"if (?:someone|i|people) (?:say|says|ask|asks) ['\"]?(.+?)['\"]?,? (?:you should |say |respond with |reply with )['\"]?(.+)['\"]?",
            r"learn (?:this|that):?\s*['\"]?(.+?)['\"]?\s*(?:->|=|means|:)\s*['\"]?(.+)['\"]?",
            r"remember:?\s*['\"]?(.+?)['\"]?\s*(?:->|=|means|:)\s*['\"]?(.+)['\"]?",
            r"['\"](.+?)['\"]?\s*should (?:get|have|receive) (?:the )?(?:response|reply|answer):?\s*['\"]?(.+)['\"]?",
        ]
        
        for pattern in teaching_patterns:
            match = re.search(pattern, text_lower)
            if match:
                trigger = match.group(1).strip()
                response = match.group(2).strip()
                return ('direct_teach', trigger, response)
        
        # Check for correction patterns
        correction_patterns = [
            r"(?:no,? )?(?:that'?s|thats) (?:wrong|incorrect|not right)",
            r"(?:no,? )?(?:you should|you're supposed to) (?:say|respond|reply)",
            r"(?:no,? )?the (?:correct|right|better) (?:answer|response|reply) is",
            r"(?:no,? )?(?:actually|instead),? (?:say|respond|reply)",
            r"(?:wrong|incorrect|nope|no)[!.]* (?:the answer is|it's|its|say)",
        ]
        
        for pattern in correction_patterns:
            if re.search(pattern, text_lower):
                return ('correction', text, None)
        
        # Check for feedback patterns
        if any(phrase in text_lower for phrase in ['good response', 'good answer', 'thats right', 
                                                    'correct', 'exactly', 'perfect', 'well done',
                                                    'nice answer', 'good job', 'thats correct']):
            return ('positive_feedback', None, None)
        
        if any(phrase in text_lower for phrase in ['bad response', 'bad answer', 'wrong answer',
                                                    'not what i meant', 'not helpful', 'that doesnt help',
                                                    'thats not right', 'incorrect']):
            return ('negative_feedback', None, None)
        
        # Check for intent to teach
        if any(phrase in text_lower for phrase in ['let me teach you', 'i want to teach you',
                                                    'im going to teach you', 'learn this',
                                                    'remember this', 'i\'ll teach you',
                                                    'can i teach you', 'teach you something']):
            return ('start_teaching', None, None)
        
        return None
    
    def process_teaching(self, text, last_user_input=None, last_bot_response=None):
        """Process a teaching interaction"""
        teaching_intent = self.detect_teaching_intent(text)
        
        if not teaching_intent:
            # Check if we're in teaching mode waiting for input
            if self.teaching_mode and self.pending_learning:
                # User is providing the response for the pending trigger
                self.learn_response(self.pending_learning, text)
                self.teaching_mode = False
                self.pending_learning = None
                self.save()
                return f"Got it! I'll respond with \"{text}\" when someone says \"{self.pending_learning}\". Thanks for teaching me! 📚"
            return None
        
        intent_type, trigger, response = teaching_intent
        
        if intent_type == 'direct_teach':
            self.learn_response(trigger, response)
            self.save()
            return f"Learned! When someone says \"{trigger}\", I'll respond with \"{response}\". Thanks for teaching me! 🎓"
        
        elif intent_type == 'correction':
            if last_user_input and last_bot_response:
                # Extract the correct response from the correction
                correct_response = self.extract_correction(text)
                if correct_response:
                    self.learn_response(last_user_input, correct_response)
                    self.record_feedback(last_user_input, last_bot_response, negative=True)
                    self.save()
                    return f"I'm sorry I got that wrong! I've learned that I should say \"{correct_response}\" instead. Thanks for correcting me! 📝"
            return "I'm sorry I got that wrong. Can you tell me what the correct response should be?"
        
        elif intent_type == 'positive_feedback':
            if last_user_input and last_bot_response:
                self.record_feedback(last_user_input, last_bot_response, negative=False)
                self.save()
            return random.choice([
                "Thanks! I'm glad I could help! 😊",
                "Yay! I'm learning! 🎉",
                "That makes me happy to hear!",
                "Wonderful! I'll remember that was a good response."
            ])
        
        elif intent_type == 'negative_feedback':
            if last_user_input and last_bot_response:
                self.record_feedback(last_user_input, last_bot_response, negative=True)
                self.save()
            return "I'm sorry about that. What should I have said instead?"
        
        elif intent_type == 'start_teaching':
            self.teaching_mode = True
            return "I'm ready to learn! 📚 Tell me what I should learn. You can say things like:\n" \
                   "• \"When someone says 'hello', you should say 'Hi there!'\"\n" \
                   "• \"Learn: 'how old are you' = 'I'm timeless!'\"\n" \
                   "Or just tell me a phrase, and I'll ask you what I should respond with!"
        
        return None
    
    def extract_correction(self, text):
        """Extract the correct response from a correction statement"""
        patterns = [
            r"(?:say|respond|reply) ['\"](.+)['\"]",
            r"(?:answer|response|reply) (?:is|should be) ['\"]?(.+)['\"]?",
            r"(?:instead|actually)[,.]? ['\"]?(.+)['\"]?$",
            r"(?:it's|its|it is) ['\"]?(.+)['\"]?$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        return None
    
    def learn_response(self, trigger, response):
        """Learn a new trigger-response pair"""
        normalized = self.normalize_text(trigger)
        if response not in self.learned_responses[normalized]:
            self.learned_responses[normalized].append(response)
    
    def record_feedback(self, user_input, bot_response, negative=False):
        """Record positive or negative feedback for a response"""
        key = f"{self.normalize_text(user_input)}::{bot_response}"
        if negative:
            self.response_feedback[key]['negative'] += 1
        else:
            self.response_feedback[key]['positive'] += 1
    
    def get_learned_response(self, text):
        """Check if we have a learned response for this input"""
        normalized = self.normalize_text(text)
        
        # Direct match
        if normalized in self.learned_responses:
            responses = self.learned_responses[normalized]
            if responses:
                return random.choice(responses)
        
        # Partial match (if input contains a learned trigger)
        for trigger, responses in self.learned_responses.items():
            if trigger in normalized or normalized in trigger:
                if responses:
                    return random.choice(responses)
        
        return None
    
    def learn_from_conversation(self, intent, user_input, bot_response):
        """Passively learn patterns from successful conversations"""
        # Track conversation flows
        # This helps predict what might come next in a conversation
        pass  # Can be expanded for more sophisticated learning
    
    def add_to_intent(self, intent, phrase):
        """Add a new phrase to an existing intent"""
        if phrase not in self.learned_phrases[intent]:
            self.learned_phrases[intent].append(phrase)
            self.save()


class HumanLikeResponder:
    """Generates more human-like responses with natural variations"""
    
    def __init__(self):
        # Response templates with placeholders
        self.response_variations = {
            'greeting': [
                "Hey there! How's it going?",
                "Hi! Nice to see you!",
                "Hello! What's on your mind today?",
                "Hey! I was hoping you'd come by!",
                "Hi there! Ready to chat?",
                "Hello, hello! How can I help?",
                "Hey! Good to see you again!",
                "Hi! What brings you here today?",
            ],
            'unknown': [
                "Hmm, I'm not quite sure I understand. Could you rephrase that?",
                "That's interesting... can you tell me more?",
                "I'm still learning! What exactly do you mean by that?",
                "Ooh, you've stumped me! Can you explain differently?",
                "I want to understand - could you say that another way?",
                "I'm not 100% sure what you mean. Help me out?",
                "That's a bit over my head right now. Can you simplify it for me?",
            ]
        }
        
        # Transitional phrases for more natural flow
        self.transitions = {
            'agreement': ["Absolutely!", "Definitely!", "For sure!", "Of course!", "Totally!", "You bet!"],
            'thinking': ["Let me think...", "Hmm...", "Well...", "So...", "Let's see..."],
            'surprise': ["Oh!", "Wow!", "Really?", "No way!", "Interesting!"],
            'understanding': ["I see!", "Ah, I get it!", "That makes sense!", "Oh, I understand now!"],
        }
        
        # Filler phrases that make speech more natural
        self.fillers = ["you know", "I mean", "like", "actually", "basically", "honestly"]
    
    def humanize_response(self, response, mood=0.7, add_filler=True):
        """Make a response more human-like"""
        # Sometimes add a transition
        if random.random() < 0.2:
            if mood > 0.6:
                transition = random.choice(self.transitions['agreement'] + self.transitions['understanding'])
            else:
                transition = random.choice(self.transitions['thinking'])
            response = transition + " " + response[0].lower() + response[1:]
        
        # Occasionally add natural fillers (but not too often)
        if add_filler and random.random() < 0.1:
            words = response.split()
            if len(words) > 5:
                insert_pos = random.randint(2, len(words) - 2)
                filler = random.choice(self.fillers)
                words.insert(insert_pos, f", {filler},")
                response = " ".join(words)
        
        # Natural capitalization variations (but keep it readable)
        # Sometimes add emphasis
        if random.random() < 0.1:
            words = response.split()
            for i, word in enumerate(words):
                if word.lower() in ['really', 'very', 'so', 'super', 'totally']:
                    words[i] = word.upper()
                    break
            response = " ".join(words)
        
        return response
    
    def add_typing_imperfections(self, text, chance=0.02):
        """Occasionally add very minor 'human' touches (use sparingly!)"""
        # This is mostly disabled by default - only for special effect
        if random.random() > chance:
            return text
        
        # Maybe double a letter (like "helllo" or "coool")
        # Or add casual endings like "haha" or "lol"
        
        casual_endings = [" haha", " lol", " :)", " :D"]
        if random.random() < 0.3:
            return text.rstrip('!.?') + random.choice(casual_endings)
        
        return text


class LongTermMemory:
    """Enhanced memory for maintaining context across conversations"""
    
    def __init__(self, save_file="long_term_memory.json"):
        self.save_file = save_file
        
        # User profile - things learned about the user
        self.user_profile = {
            'name': None,
            'preferences': {},
            'facts': {},
            'likes': [],
            'dislikes': [],
            'topics_of_interest': [],
            'conversation_style': 'casual',  # casual, formal, playful
            'first_seen': None,
            'last_seen': None,
            'total_conversations': 0,
            'total_messages': 0
        }
        
        # Important things to remember
        self.important_facts = []
        
        # Recent conversation summaries
        self.conversation_summaries = []
        
        # Relationship level (builds over time)
        self.relationship_level = 0  # 0-100
        
        self.load()
    
    def save(self):
        """Save memory to file"""
        data = {
            'user_profile': self.user_profile,
            'important_facts': self.important_facts,
            'conversation_summaries': self.conversation_summaries[-20:],  # Keep last 20
            'relationship_level': self.relationship_level
        }
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load(self):
        """Load memory from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.user_profile = data.get('user_profile', self.user_profile)
                self.important_facts = data.get('important_facts', [])
                self.conversation_summaries = data.get('conversation_summaries', [])
                self.relationship_level = data.get('relationship_level', 0)
                return True
            except Exception as e:
                print(f"Error loading memory: {e}")
        return False
    
    def update_session(self):
        """Update session tracking"""
        now = datetime.now().isoformat()
        if not self.user_profile['first_seen']:
            self.user_profile['first_seen'] = now
        self.user_profile['last_seen'] = now
        self.user_profile['total_conversations'] += 1
        self.save()
    
    def add_message(self):
        """Track a message"""
        self.user_profile['total_messages'] += 1
        # Relationship grows with interaction
        self.relationship_level = min(100, self.relationship_level + 0.1)
    
    def remember_fact(self, fact, importance='normal'):
        """Store an important fact"""
        fact_entry = {
            'fact': fact,
            'importance': importance,
            'learned_at': datetime.now().isoformat()
        }
        self.important_facts.append(fact_entry)
        self.save()
    
    def get_personalized_greeting(self):
        """Generate a personalized greeting based on history"""
        greetings = []
        
        name = self.user_profile.get('name')
        total_convos = self.user_profile.get('total_conversations', 0)
        
        if total_convos == 1:
            greetings = [
                "Nice to meet you!",
                "Hello! I don't think we've met before!",
                "Hi there! Welcome!"
            ]
        elif total_convos < 5:
            base = f"Hey{', ' + name if name else ''}! Good to see you again!"
            greetings = [base, f"Welcome back{', ' + name if name else ''}!"]
        elif total_convos < 20:
            greetings = [
                f"Hey{', ' + name if name else ''}! Always nice to chat with you!",
                f"Welcome back, friend! How have you been?",
                f"Hi{', ' + name if name else ''}! I was hoping you'd visit!"
            ]
        else:
            greetings = [
                f"Hey{', ' + name if name else ''}! My favorite person to chat with!",
                f"Hi there, old friend! Great to see you!",
                f"Welcome back! I've missed our conversations!"
            ]
        
        return random.choice(greetings)
    
    def get_relationship_status(self):
        """Describe the relationship level"""
        level = self.relationship_level
        if level < 10:
            return "stranger"
        elif level < 30:
            return "acquaintance"
        elif level < 60:
            return "friend"
        elif level < 90:
            return "good friend"
        else:
            return "best friend"
