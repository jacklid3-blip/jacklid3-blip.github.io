"""
Neural Network Chatbot - Main module
Imports utilities from chatbot_utils.py and chatbot_fallback.py
Training data and responses are imported from separate files
Enhanced with conversational learning and human-like personality
"""
import numpy as np
import pickle
import os
import re
import random
import math
import json
import socket
from datetime import datetime

# ============================================================
# 🔑 PUT YOUR OPENAI API KEY HERE
# ============================================================
OPENAI_API_KEY = "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"  # Paste your API key between the quotes
# Example: OPENAI_API_KEY = "sk-abc123..."
# ============================================================

# Try to import OpenAI for API-enhanced learning
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not found. Install with: pip install openai")

# Try to import sympy for calculus
try:
    import sympy
    from sympy import symbols, diff, integrate, limit, simplify, expand, factor
    from sympy import sin, cos, tan, log, ln, exp, sqrt, pi, E, oo
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

# Import from our modules
from chatbot_utils import MarkovTextGenerator, ConversationMemory
from chatbot_fallback import SmartFallback

# Import learning and personality modules
try:
    from chatbot_learning import (
        PersonalityEngine, 
        ConversationalLearner, 
        HumanLikeResponder,
        LongTermMemory
    )
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    print("Warning: chatbot_learning.py not found. Learning features disabled.")

# Import training data and responses from separate files
try:
    from training_data import training_data
except ImportError:
    # Fallback training data if file doesn't exist
    training_data = {
        "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
        "goodbye": ["bye", "goodbye", "see you", "later"],
        "thanks": ["thank you", "thanks", "appreciate it"],
        "name": ["what is your name", "who are you"],
    }

try:
    from bot_responses import responses
except ImportError:
    # Fallback responses if file doesn't exist
    responses = {
        "greeting": ["Hello!", "Hi there!", "Hey!"],
        "goodbye": ["Goodbye!", "See you later!", "Bye!"],
        "thanks": ["You're welcome!", "No problem!", "Happy to help!"],
        "name": ["I'm a chatbot!", "I'm your AI assistant!"],
    }


class APIEnhancedLearning:
    """
    Handles API-based learning enhancement with offline backup capability.
    - Uses OpenAI API when online/WiFi available
    - Saves responses as backup training data for offline use
    - Falls back to local backup when offline
    """
    
    def __init__(self, api_key: str = None, backup_file: str = "api_training_backup.json", model: str = "gpt-4o-mini"):
        # Check for API key in this order: passed argument, global constant, environment variable
        self.api_key = api_key or OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        self.backup_file = backup_file
        self.model = model
        self.client = None
        self.backup_data = self._load_backup()
        self.is_enabled = False
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.is_enabled = True
                print("✓ API Enhanced Learning initialized successfully!")
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def check_internet_connection(self, host="8.8.8.8", port=53, timeout=3):
        """Check if there's an internet/WiFi connection available."""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except (socket.error, socket.timeout):
            return False
    
    def _load_backup(self) -> dict:
        """Load backup training data from file."""
        if os.path.exists(self.backup_file):
            try:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✓ Loaded {len(data.get('conversations', []))} backup conversations")
                    return data
            except Exception as e:
                print(f"Warning: Could not load backup file: {e}")
        return {"conversations": [], "learned_responses": {}, "last_sync": None}
    
    def _save_backup(self):
        """Save current data to backup file."""
        try:
            self.backup_data["last_sync"] = datetime.now().isoformat()
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save backup: {e}")
    
    def get_enhanced_response(self, user_input: str, context: str = "", intent: str = None) -> str:
        """
        Get an enhanced response using the API if online, or from backup if offline.
        
        Args:
            user_input: The user's message
            context: Optional conversation context
            intent: Optional detected intent from the chatbot
            
        Returns:
            Enhanced response string
        """
        # Check if we have a cached response first
        input_key = user_input.lower().strip()
        if input_key in self.backup_data.get("learned_responses", {}):
            cached = self.backup_data["learned_responses"][input_key]
            # Return cached response 30% of the time for variety
            if random.random() < 0.3:
                return cached["response"]
        
        # Check if we can use the API
        if not self.is_enabled or not self.client:
            return None
            
        if not self.check_internet_connection():
            print("(Offline - using local knowledge)")
            return self._get_offline_response(user_input, intent)
        
        try:
            # Build the system prompt
            system_prompt = """You are a helpful, friendly chatbot assistant. 
Provide concise, natural responses. Keep answers brief but helpful.
If you don't know something, be honest about it."""
            
            if intent:
                system_prompt += f"\nThe detected intent is: {intent}"
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "assistant", "content": f"Previous context: {context}"})
            
            messages.append({"role": "user", "content": user_input})
            
            # Call the API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Save to backup for offline use
            self._save_to_backup(user_input, ai_response, intent)
            
            return ai_response
            
        except Exception as e:
            print(f"API error: {e}")
            return self._get_offline_response(user_input, intent)
    
    def _save_to_backup(self, user_input: str, response: str, intent: str = None):
        """Save a conversation exchange to backup training data."""
        # Save to conversations list
        self.backup_data["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "intent": intent
        })
        
        # Save to learned responses for quick lookup
        input_key = user_input.lower().strip()
        self.backup_data["learned_responses"][input_key] = {
            "response": response,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep backup file size manageable (max 1000 conversations)
        if len(self.backup_data["conversations"]) > 1000:
            self.backup_data["conversations"] = self.backup_data["conversations"][-500:]
        
        self._save_backup()
    
    def _get_offline_response(self, user_input: str, intent: str = None) -> str:
        """Get a response from backup data when offline."""
        input_key = user_input.lower().strip()
        
        # Direct match
        if input_key in self.backup_data.get("learned_responses", {}):
            return self.backup_data["learned_responses"][input_key]["response"]
        
        # Fuzzy match - find similar inputs
        best_match = None
        best_score = 0
        
        for stored_input, data in self.backup_data.get("learned_responses", {}).items():
            # Simple word overlap scoring
            input_words = set(input_key.split())
            stored_words = set(stored_input.split())
            
            if input_words and stored_words:
                overlap = len(input_words & stored_words)
                score = overlap / max(len(input_words), len(stored_words))
                
                if score > best_score and score > 0.5:
                    best_score = score
                    best_match = data["response"]
        
        return best_match
    
    def sync_training_data(self, training_data: dict, responses: dict):
        """
        Sync API knowledge with local training data (call when on WiFi).
        This enhances your local training data with API-generated examples.
        """
        if not self.is_enabled or not self.check_internet_connection():
            print("Cannot sync - offline or API not configured")
            return False
        
        print("Syncing training data with API...")
        enhanced_count = 0
        
        try:
            for intent, patterns in training_data.items():
                # Generate additional training examples for each intent
                prompt = f"""Generate 3 new example phrases that a user might say when they want to express "{intent}".
The existing examples are: {patterns[:5]}
Return only the new phrases, one per line, no numbers or bullets."""
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.8
                )
                
                new_patterns = response.choices[0].message.content.strip().split('\n')
                new_patterns = [p.strip() for p in new_patterns if p.strip()]
                
                # Add to backup
                if intent not in self.backup_data.get("enhanced_training", {}):
                    self.backup_data["enhanced_training"] = self.backup_data.get("enhanced_training", {})
                    self.backup_data["enhanced_training"][intent] = []
                
                self.backup_data["enhanced_training"][intent].extend(new_patterns)
                enhanced_count += len(new_patterns)
            
            self._save_backup()
            print(f"✓ Added {enhanced_count} new training examples to backup")
            return True
            
        except Exception as e:
            print(f"Sync error: {e}")
            return False
    
    def get_enhanced_training_data(self, original_training_data: dict) -> dict:
        """Get training data enhanced with API-generated examples from backup."""
        enhanced = dict(original_training_data)
        
        for intent, patterns in self.backup_data.get("enhanced_training", {}).items():
            if intent in enhanced:
                # Add unique patterns only
                existing = set(enhanced[intent])
                for pattern in patterns:
                    if pattern not in existing:
                        enhanced[intent].append(pattern)
        
        return enhanced
    
    def get_status(self) -> dict:
        """Get the current status of API learning."""
        return {
            "enabled": self.is_enabled,
            "online": self.check_internet_connection(),
            "backup_conversations": len(self.backup_data.get("conversations", [])),
            "learned_responses": len(self.backup_data.get("learned_responses", {})),
            "last_sync": self.backup_data.get("last_sync"),
            "model": self.model
        }


class NeuralChatbot:
    def __init__(self, layer_sizes, learning_rate=0.01):
        self.learning_rate = learning_rate
        self.weights = []
        self.biases = []
        self.vocab = {}
        self.intents = []
        self.responses = {}
        self.memory = ConversationMemory()
        self.generator = MarkovTextGenerator(order=2)
        self.fallback = SmartFallback()
        self.use_generator = True  # Toggle between generated and preset responses
        self.bot_name = "ChatBot"  # Default bot name, can be changed by user
        
        # Initialize API Enhanced Learning (for WiFi/online learning with backup)
        self.api_learning = None
        self.use_api_enhancement = False  # Toggle to enable/disable API responses
        
        # Initialize learning and personality systems
        if LEARNING_AVAILABLE:
            self.personality = PersonalityEngine()
            self.learner = ConversationalLearner()
            self.humanizer = HumanLikeResponder()
            self.long_memory = LongTermMemory()
            self.long_memory.update_session()
        else:
            self.personality = None
            self.learner = None
            self.humanizer = None
            self.long_memory = None
        
        # Track last interaction for learning
        self.last_user_input = None
        self.last_bot_response = None
        
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.01
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def setup_api_learning(self, api_key: str = None, backup_file: str = "api_training_backup.json"):
        """
        Set up API-enhanced learning with your OpenAI API key.
        Call this to enable WiFi-based learning with offline backup.
        
        Args:
            api_key: Your OpenAI API key (or set OPENAI_API_KEY environment variable)
            backup_file: Path to save backup training data
        """
        self.api_learning = APIEnhancedLearning(api_key=api_key, backup_file=backup_file)
        if self.api_learning.is_enabled:
            self.use_api_enhancement = True
            print("API learning enabled! Responses will be enhanced when online.")
            print("Backup training data will be saved for offline use.")
        else:
            print("API learning could not be enabled. Check your API key.")
    
    def get_api_status(self) -> dict:
        """Get the status of API learning."""
        if self.api_learning:
            return self.api_learning.get_status()
        return {"enabled": False, "message": "API learning not configured"}
    
    def sync_with_api(self, training_data: dict, responses: dict):
        """Sync training data with API when on WiFi."""
        if self.api_learning:
            return self.api_learning.sync_training_data(training_data, responses)
        print("API learning not configured. Call setup_api_learning() first.")
        return False
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def forward(self, X):
        self.activations = [X]
        self.z_values = []
        
        for i in range(len(self.weights)):
            z = np.dot(self.activations[-1], self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            
            if i < len(self.weights) - 1:
                a = self.relu(z)
            else:
                a = self.softmax(z)
            
            self.activations.append(a)
        
        return self.activations[-1]
    
    def backward(self, y):
        m = y.shape[0]
        delta = self.activations[-1] - y
        
        for i in range(len(self.weights) - 1, -1, -1):
            dw = np.dot(self.activations[i].T, delta) / m
            db = np.sum(delta, axis=0, keepdims=True) / m
            
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self.relu_derivative(self.z_values[i - 1])
            
            self.weights[i] -= self.learning_rate * dw
            self.biases[i] -= self.learning_rate * db
    
    def train(self, X, y, epochs=100):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(y)
    
    def predict(self, X):
        return self.forward(X)
    
    def tokenize(self, text):
        """Convert text to lowercase and split into words"""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        return text.split()
    
    def text_to_vector(self, text):
        """Convert text to bag-of-words vector"""
        words = self.tokenize(text)
        vector = np.zeros(len(self.vocab))
        for word in words:
            if word in self.vocab:
                vector[self.vocab[word]] = 1
        return vector
    
    def build_vocab(self, training_data):
        """Build vocabulary from training data"""
        all_words = set()
        for intent, patterns in training_data.items():
            for pattern in patterns:
                words = self.tokenize(pattern)
                all_words.update(words)
        
        self.vocab = {word: i for i, word in enumerate(sorted(all_words))}
        return len(self.vocab)
    
    def prepare_training_data(self, training_data):
        """Convert training data to vectors"""
        X = []
        y = []
        self.intents = list(training_data.keys())
        
        for intent_idx, (intent, patterns) in enumerate(training_data.items()):
            for pattern in patterns:
                X.append(self.text_to_vector(pattern))
                y.append(intent_idx)
        
        X = np.array(X)
        y = np.eye(len(self.intents))[y]
        return X, y
    
    def evaluate_math(self, text):
        """Check if text contains a math expression and evaluate it"""
        text_lower = text.lower().strip()
        
        # First, convert word-based math to symbols
        expr = text_lower
        
        # Replace common math words with operators (order matters!)
        word_replacements = [
            (r'\bsquare root of\s*', 'sqrt('),  # Must add closing paren later
            (r'\bsqrt\s+', 'sqrt('),
            (r'\bsquared\b', '**2'),
            (r'\bcubed\b', '**3'),
            (r'\bto the power of\b', '**'),
            (r'\braised to\b', '**'),
            (r'\bmultiplied by\b', '*'),
            (r'\bdivided by\b', '/'),
            (r'\bplus\b', '+'),
            (r'\bminus\b', '-'),
            (r'\btimes\b', '*'),
            (r'\bover\b', '/'),
            (r'\bmod\b', '%'),
            (r'\bsin\b', 'sin('),
            (r'\bcos\b', 'cos('),
            (r'\btan\b', 'tan('),
            (r'\blog\b', 'log10('),
            (r'\bln\b', 'log('),
            (r'\babs\b', 'abs('),
            (r'\bpi\b', str(math.pi)),
            (r'\^', '**'),
        ]
        
        for pattern, replacement in word_replacements:
            expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)
        
        # Extract the math part - remove trigger phrases
        triggers_to_remove = [
            r"^what(?:'s| is)\s+",
            r"^calculate\s+",
            r"^compute\s+",
            r"^solve\s+",
            r"^how much is\s+",
            r"^evaluate\s+",
            r"^what does\s+",
            r"\?$",
            r"equal(?:s)?\s*\??$",
        ]
        
        for pattern in triggers_to_remove:
            expr = re.sub(pattern, '', expr, flags=re.IGNORECASE)
        
        expr = expr.strip()
        
        # Check if it looks like a math expression
        # Must have at least one digit and one operator or function
        has_digit = bool(re.search(r'\d', expr))
        has_operator = bool(re.search(r'[+\-*/\*\%]', expr))
        has_function = bool(re.search(r'(sqrt|sin|cos|tan|log|abs)\(', expr))
        has_power = '**' in expr
        
        if not has_digit:
            return None
        if not (has_operator or has_function or has_power):
            return None
        
        try:
            # Clean up the expression
            # Fix function calls that might be missing closing parens
            # Count parens and add missing ones
            open_parens = expr.count('(')
            close_parens = expr.count(')')
            if open_parens > close_parens:
                expr += ')' * (open_parens - close_parens)
            
            # Remove any remaining non-math characters
            # But keep: digits, operators, parens, dots, function names
            allowed_pattern = r'[^\d+\-*/().%\s]'
            
            # Check for dangerous content
            if any(word in expr for word in ['import', 'exec', 'eval', 'open', 'file', '__', 'os', 'sys']):
                return None
            
            # Create a safe namespace with only math functions
            safe_dict = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'abs': abs,
                'pow': pow,
                'round': round,
            }
            
            result = eval(expr, {"__builtins__": {}}, safe_dict)
            
            # Format the result nicely
            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 10)  # Avoid floating point weirdness
                    # Remove trailing zeros
                    if '.' in str(result):
                        result = f"{result:.10f}".rstrip('0').rstrip('.')
            
            return f"The answer is: {result}"
            
        except ZeroDivisionError:
            return "Cannot divide by zero!"
        except (SyntaxError, NameError, TypeError, ValueError):
            return None
        except Exception:
            return None
    
    def evaluate_calculus(self, text):
        """Handle calculus operations: derivatives, integrals, limits"""
        if not SYMPY_AVAILABLE:
            return None
        
        text_lower = text.lower().strip()
        
        # Define the variable (default to x)
        x, y, z, t = symbols('x y z t')
        
        try:
            # Derivative patterns
            derivative_patterns = [
                r"(?:derivative|differentiate|diff|d/dx)\s*(?:of\s+)?(.+?)(?:\s+with respect to (\w+))?$",
                r"(?:find|calculate|compute|what is|what's)\s+(?:the\s+)?derivative\s+(?:of\s+)?(.+?)(?:\s+with respect to (\w+))?$",
                r"d/d(\w)\s*\[?(.+?)\]?$",
            ]
            
            for pattern in derivative_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        expr_str, var_str = groups
                    else:
                        var_str, expr_str = groups[0], groups[1]
                    
                    # Parse the expression
                    expr_str = self._clean_calculus_expr(expr_str)
                    var = symbols(var_str) if var_str else x
                    
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    expr = parse_expr(expr_str, transformations=transformations)
                    
                    result = diff(expr, var)
                    return f"The derivative is: {result}"
            
            # Integral patterns
            integral_patterns = [
                r"(?:integral|integrate|antiderivative)\s*(?:of\s+)?(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?|d)(\w+))?(?:\s+from\s+([\d\-\.]+)\s+to\s+([\d\-\.]+))?$",
                r"(?:find|calculate|compute|what is|what's)\s+(?:the\s+)?integral\s+(?:of\s+)?(.+?)(?:\s+d(\w))?(?:\s+from\s+([\d\-\.]+)\s+to\s+([\d\-\.]+))?$",
                r"∫\s*(.+?)\s*d(\w)",
            ]
            
            for pattern in integral_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    expr_str = groups[0]
                    var_str = groups[1] if len(groups) > 1 else None
                    lower = groups[2] if len(groups) > 2 else None
                    upper = groups[3] if len(groups) > 3 else None
                    
                    expr_str = self._clean_calculus_expr(expr_str)
                    var = symbols(var_str) if var_str else x
                    
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    expr = parse_expr(expr_str, transformations=transformations)
                    
                    if lower and upper:
                        # Definite integral
                        result = integrate(expr, (var, float(lower), float(upper)))
                        return f"The definite integral from {lower} to {upper} is: {result}"
                    else:
                        # Indefinite integral
                        result = integrate(expr, var)
                        return f"The integral is: {result} + C"
            
            # Limit patterns
            limit_patterns = [
                r"(?:limit|lim)\s*(?:of\s+)?(.+?)\s+(?:as\s+)?(\w+)\s*(?:->|→|approaches|goes to)\s*(.+)$",
                r"(?:find|calculate|compute|what is|what's)\s+(?:the\s+)?limit\s+(?:of\s+)?(.+?)\s+(?:as\s+)?(\w+)\s*(?:->|→|approaches)\s*(.+)$",
            ]
            
            for pattern in limit_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    expr_str, var_str, approach = match.groups()
                    
                    expr_str = self._clean_calculus_expr(expr_str)
                    var = symbols(var_str) if var_str else x
                    
                    # Handle infinity
                    approach = approach.strip()
                    if approach in ['inf', 'infinity', '∞']:
                        approach_val = oo
                    elif approach in ['-inf', '-infinity', '-∞']:
                        approach_val = -oo
                    else:
                        approach_val = float(approach)
                    
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    expr = parse_expr(expr_str, transformations=transformations)
                    
                    result = limit(expr, var, approach_val)
                    return f"The limit is: {result}"
            
            # Simplify patterns
            simplify_patterns = [
                r"(?:simplify|reduce)\s+(.+)$",
                r"(?:expand)\s+(.+)$",
                r"(?:factor)\s+(.+)$",
            ]
            
            for pattern in simplify_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    expr_str = match.group(1)
                    expr_str = self._clean_calculus_expr(expr_str)
                    
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    expr = parse_expr(expr_str, transformations=transformations)
                    
                    if 'expand' in text_lower:
                        result = expand(expr)
                        return f"Expanded: {result}"
                    elif 'factor' in text_lower:
                        result = factor(expr)
                        return f"Factored: {result}"
                    else:
                        result = simplify(expr)
                        return f"Simplified: {result}"
            
            return None
            
        except Exception as e:
            return None
    
    def _clean_calculus_expr(self, expr_str):
        """Clean and prepare expression string for sympy parsing"""
        expr_str = expr_str.strip()
        
        # Remove trailing question marks
        expr_str = re.sub(r'\?$', '', expr_str)
        
        # Replace common notations
        replacements = [
            (r'\^', '**'),
            (r'\be\^', 'exp('),
            (r'\bln\b', 'log'),
            (r'\blog(\d+)\b', r'log(\1, 10)'),  # log10 -> log base 10
        ]
        
        for pattern, replacement in replacements:
            expr_str = re.sub(pattern, replacement, expr_str)
        
        return expr_str
    
    def get_response(self, text):
        """Get chatbot response for input text with memory, learning, and personality"""
        
        # Update personality mood based on input
        if self.personality:
            self.personality.update_mood(text)
        
        # Update long-term memory
        if self.long_memory:
            self.long_memory.add_message()
        
        # Check for web search help command
        text_lower = text.lower().strip()
        if text_lower in ['search help', 'web help', '/help search', 'how to search', 'search commands']:
            return self._get_search_help()
        
        # Check for API learning commands
        if text_lower.startswith('/api'):
            return self._handle_api_command(text_lower)
        
        # Check for direct web search commands first
        web_result = self._handle_web_search_command(text)
        if web_result:
            self.memory.add_message('user', text, 'web_search')
            self.memory.add_message('bot', web_result, 'web_search')
            self.last_user_input = text
            self.last_bot_response = web_result
            return web_result
        
        # Check if user is trying to teach the bot
        if self.learner:
            teaching_response = self.learner.process_teaching(
                text, 
                self.last_user_input, 
                self.last_bot_response
            )
            if teaching_response:
                self.last_user_input = text
                self.last_bot_response = teaching_response
                return self._finalize_response(teaching_response)
            
            # Check for learned responses first
            learned = self.learner.get_learned_response(text)
            if learned:
                self.memory.add_message('user', text, 'learned')
                self.last_user_input = text
                self.last_bot_response = learned
                self.memory.add_message('bot', learned, 'learned')
                return self._finalize_response(learned)
        
        # Check for calculus expressions first (derivatives, integrals, limits)
        calculus_result = self.evaluate_calculus(text)
        if calculus_result:
            self.memory.add_message('user', text, 'calculus')
            self.memory.add_message('bot', calculus_result, 'calculus')
            self.last_user_input = text
            self.last_bot_response = calculus_result
            return calculus_result
        
        # Check for basic math expressions
        math_result = self.evaluate_math(text)
        if math_result:
            self.memory.add_message('user', text, 'math')
            self.memory.add_message('bot', math_result, 'math')
            self.last_user_input = text
            self.last_bot_response = math_result
            return math_result
        
        # Check if user is telling their name
        name = self.memory.extract_name(text)
        if name:
            self.memory.user_name = name
            if self.long_memory:
                self.long_memory.user_profile['name'] = name
                self.long_memory.save()
            self.memory.add_message('user', text, 'user_name')
            response = f"Nice to meet you, {name}! I'll remember that."
            if self.personality:
                response = self.personality.add_personality_flair(response)
            self.last_user_input = text
            self.last_bot_response = response
            return response
        
        # Check if user is sharing a fact about themselves
        fact = self.memory.extract_fact(text)
        if fact:
            self.memory.store_fact(fact)
            if self.long_memory:
                self.long_memory.remember_fact(str(fact))
            response = self.memory.get_fact_response(fact)
            if response:
                self.memory.add_message('user', text, 'user_fact')
                if self.personality:
                    response += self.personality.get_curious_followup()
                self.last_user_input = text
                self.last_bot_response = response
                return self._finalize_response(response)
        
        # Check for questions about what the bot knows about user
        if any(phrase in text.lower() for phrase in ['what do you know about me', 'what have you learned about me', 'tell me about myself']):
            if self.memory.user_facts or self.memory.user_name:
                facts = []
                if self.memory.user_name:
                    facts.append(f"Your name is {self.memory.user_name}")
                for key, value in self.memory.user_facts.items():
                    facts.append(f"You {key.replace('_', ' ')}: {value}")
                response = "Here's what I know about you: " + ". ".join(facts) + "."
                if self.long_memory:
                    response += f" We've chatted {self.long_memory.user_profile['total_messages']} times!"
                return self._finalize_response(response)
            return self._finalize_response("I don't know much about you yet. Tell me something!")
        
        # Check for questions about what user said before
        if any(phrase in text.lower() for phrase in ['what did i say', 'my last message', 'remember what i said']):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                return self._finalize_response(f"You previously said: '{last_msg}'")
            return self._finalize_response("We just started talking!")
        
        # Check for questions about conversation
        if any(phrase in text.lower() for phrase in ['what have we talked about', 'what did we discuss', 'conversation so far']):
            if self.memory.topics_discussed:
                topics = ', '.join(self.memory.topics_discussed[-5:])
                return self._finalize_response(f"We've talked about: {topics}")
            return self._finalize_response("We haven't talked about much yet!")
        
        # Check if asking for user's own name
        if any(phrase in text.lower() for phrase in ['what is my name', 'whats my name', 'do you know my name', 'remember my name']):
            if self.memory.user_name:
                response = f"Your name is {self.memory.user_name}!"
                if self.long_memory and self.long_memory.relationship_level > 30:
                    response = f"Of course I remember! You're {self.memory.user_name}! 😊"
                return self._finalize_response(response)
            return self._finalize_response("I don't know your name yet. What should I call you?")
        
        # Check if user is setting the bot's name
        bot_name = self.extract_bot_name(text)
        if bot_name:
            old_name = self.bot_name
            self.bot_name = bot_name
            self.memory.add_message('user', text, 'set_bot_name')
            response = f"I love it! From now on, call me {self.bot_name}! 🎉"
            self.memory.add_message('bot', response, 'set_bot_name')
            self.last_user_input = text
            self.last_bot_response = response
            return response
        
        # Check if asking for bot's name
        if any(phrase in text.lower() for phrase in ['what is your name', 'whats your name', 'your name', 'who are you', 'what do i call you', 'what should i call you']):
            self.memory.add_message('user', text, 'name')
            response = f"My name is {self.bot_name}! Nice to meet you! 😊"
            self.memory.add_message('bot', response, 'name')
            self.last_user_input = text
            self.last_bot_response = response
            return response
        
        # Regular intent classification
        vector = self.text_to_vector(text).reshape(1, -1)
        prediction = self.predict(vector)
        intent_idx = np.argmax(prediction)
        confidence = prediction[0][intent_idx]
        intent = self.intents[intent_idx]
        
        # Store in memory
        self.memory.add_message('user', text, intent)
        
        # Use smart fallback for low confidence
        if confidence < 0.4:
            # Try API enhancement first if enabled and online
            if self.use_api_enhancement and self.api_learning:
                context = self.memory.get_recent_context() if hasattr(self.memory, 'get_recent_context') else ""
                api_response = self.api_learning.get_enhanced_response(text, context, intent)
                if api_response:
                    self.memory.add_message('bot', api_response, 'api_enhanced')
                    self.last_user_input = text
                    self.last_bot_response = api_response
                    return self._finalize_response(api_response)
            
            response = self.fallback.get_response(text)
            self.memory.add_message('bot', response, 'unknown')
            self.last_user_input = text
            self.last_bot_response = response
            return self._finalize_response(response)
        
        # Try to generate a new response, fallback to preset
        response = None
        if self.use_generator and random.random() < 0.6:  # 60% chance to generate
            response = self.generator.generate(intent)
        
        if not response:
            response = random.choice(self.responses[intent])
        
        # Personalize with name if known
        if self.memory.user_name and random.random() < 0.3:
            response = f"{self.memory.user_name}, {response[0].lower()}{response[1:]}"
        
        # Add context based on conversation length
        if self.memory.message_count > 10 and intent == "greeting":
            if self.long_memory:
                response = self.long_memory.get_personalized_greeting()
            else:
                response = "Welcome back! " + response
        
        self.memory.add_message('bot', response, intent)
        self.last_user_input = text
        self.last_bot_response = response
        return self._finalize_response(response)
    
    def _handle_web_search_command(self, text):
        """
        Handle direct web search commands from the user.
        
        Commands:
            search: <query>  - Search both DuckDuckGo and Wikipedia
            wiki: <query>    - Search Wikipedia only
            ddg: <query>     - Search DuckDuckGo only
            google: <query>  - Alias for search
            /search <query>  - Alternative syntax
            /wiki <query>    - Alternative syntax
        
        Returns formatted response or None if not a search command.
        """
        text_stripped = text.strip()
        text_lower = text_stripped.lower()
        
        # Define search command patterns
        search_patterns = [
            (r'^search[:\s]+(.+)$', 'both'),
            (r'^/search\s+(.+)$', 'both'),
            (r'^google[:\s]+(.+)$', 'both'),
            (r'^look\s*up[:\s]+(.+)$', 'both'),
            (r'^wiki[:\s]+(.+)$', 'wikipedia'),
            (r'^/wiki\s+(.+)$', 'wikipedia'),
            (r'^wikipedia[:\s]+(.+)$', 'wikipedia'),
            (r'^ddg[:\s]+(.+)$', 'duckduckgo'),
            (r'^/ddg\s+(.+)$', 'duckduckgo'),
            (r'^duckduckgo[:\s]+(.+)$', 'duckduckgo'),
        ]
        
        query = None
        search_type = None
        
        for pattern, stype in search_patterns:
            match = re.match(pattern, text_lower)
            if match:
                # Get the query from original text (preserve case)
                query_start = match.start(1)
                query = text_stripped[query_start:].strip()
                search_type = stype
                break
        
        if not query:
            return None
        
        # Try to import and use web search
        try:
            from web_search import WebSearch
            searcher = WebSearch()
            
            result = None
            
            if search_type == 'wikipedia':
                result = searcher.search_wikipedia(query)
                if not result:
                    # Try the search API as fallback
                    result = searcher._wikipedia_search(query)
            elif search_type == 'duckduckgo':
                result = searcher.search_duckduckgo(query)
            else:  # both
                result = searcher.search(query)
            
            if result:
                return searcher.format_response(result)
            else:
                return f"🔍 Sorry, I couldn't find information about '{query}'. Try a different search term!"
                
        except ImportError:
            return "❌ Web search is not available. Make sure web_search.py is installed."
        except Exception as e:
            return f"❌ Search error: {str(e)}"
    
    def _handle_api_command(self, text):
        """Handle API learning commands"""
        parts = text.split()
        
        # /api status - Show current API learning status
        if len(parts) == 1 or parts[1] == 'status':
            status = self.get_api_status()
            if not status.get('enabled'):
                return """📡 **API Learning Status: Not Configured**

To enable API-enhanced learning:
1. Get an OpenAI API key from https://platform.openai.com
2. Use `/api setup YOUR_API_KEY` to configure

Or set the OPENAI_API_KEY environment variable."""
            
            online_status = "🟢 Online" if status.get('online') else "🔴 Offline"
            return f"""📡 **API Learning Status**

• Status: {'✅ Enabled' if status['enabled'] else '❌ Disabled'}
• Connection: {online_status}
• Model: {status.get('model', 'N/A')}
• Backup Conversations: {status.get('backup_conversations', 0)}
• Learned Responses: {status.get('learned_responses', 0)}
• Last Sync: {status.get('last_sync', 'Never')}

Commands:
• `/api on` - Enable API responses
• `/api off` - Disable API responses  
• `/api sync` - Sync training data (requires WiFi)"""
        
        # /api setup <key> - Configure API key
        elif parts[1] == 'setup' and len(parts) >= 3:
            api_key = parts[2]
            self.setup_api_learning(api_key)
            if self.api_learning and self.api_learning.is_enabled:
                return "✅ API learning configured successfully! I'll now use the API when online and save responses for offline use."
            return "❌ Failed to configure API learning. Please check your API key."
        
        # /api on - Enable API enhancement
        elif parts[1] == 'on':
            if self.api_learning and self.api_learning.is_enabled:
                self.use_api_enhancement = True
                return "✅ API enhancement enabled! I'll use AI-powered responses when available."
            return "❌ API learning not configured. Use `/api setup YOUR_KEY` first."
        
        # /api off - Disable API enhancement
        elif parts[1] == 'off':
            self.use_api_enhancement = False
            return "✅ API enhancement disabled. Using local responses only."
        
        # /api sync - Sync training data with API
        elif parts[1] == 'sync':
            if self.api_learning:
                if self.api_learning.check_internet_connection():
                    if self.sync_with_api(training_data, responses):
                        return "✅ Training data synced! New examples added to backup."
                    return "❌ Sync failed. Please try again later."
                return "❌ No internet connection. Connect to WiFi and try again."
            return "❌ API learning not configured. Use `/api setup YOUR_KEY` first."
        
        # /api help
        else:
            return """📡 **API Learning Commands**

• `/api status` - Show current API status
• `/api setup <KEY>` - Configure your OpenAI API key
• `/api on` - Enable API-enhanced responses
• `/api off` - Disable API responses
• `/api sync` - Sync training data with API (WiFi required)

When enabled:
• Uses AI for better responses when online
• Saves responses as backup training data
• Falls back to local data when offline"""
    
    def _get_search_help(self):
        """Return help text for web search commands"""
        return """🌐 **Web Search Commands**

You can search the internet directly from chat!

**Commands:**
• `search: <topic>` - Search the web
• `wiki: <topic>` - Search Wikipedia only
• `ddg: <topic>` - Search DuckDuckGo only
• `/search <topic>` - Alternative syntax
• `look up: <topic>` - Another way to search

**Examples:**
• search: python programming
• wiki: Albert Einstein
• ddg: how does gravity work
• /search climate change

**Auto-Search:**
I also automatically search when you ask:
• "What is...?" questions
• "Who invented/created...?" questions
• Questions I don't know the answer to

Just ask me anything! 🔍"""
    
    def _finalize_response(self, response):
        """Apply personality and humanization to the final response"""
        if self.personality:
            # Add mood-based prefix
            response = self.personality.get_mood_prefix() + response
            # Add personality flair
            response = self.personality.add_personality_flair(response)
        
        if self.humanizer:
            # Make response more human-like
            mood = self.personality.mood if self.personality else 0.7
            response = self.humanizer.humanize_response(response, mood=mood)
        
        return response
    
    def extract_bot_name(self, text):
        """Extract bot name from user input when they want to name the bot"""
        text_lower = text.lower().strip()
        
        # Patterns for naming the bot
        patterns = [
            r"(?:your name is|youre called|you are called|you are named|youre named)\s+(.+)",
            r"(?:ill call you|i will call you|im calling you|i am calling you)\s+(.+)",
            r"(?:im naming you|i am naming you|lets name you|let us name you)\s+(.+)",
            r"(?:i name you|ill name you|i will name you)\s+(.+)",
            r"(?:your new name is|from now on you are|from now on youre)\s+(.+)",
            r"(?:i want to call you|id like to call you|i would like to call you)\s+(.+)",
            r"(?:can i call you|may i call you|could i call you)\s+(.+)",
            r"(?:call yourself|rename you to|change your name to)\s+(.+)",
            r"(?:youll be called|you will be called|youll be named|you will be named)\s+(.+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip()
                # Clean up the name - remove punctuation at the end
                name = re.sub(r'[.!?,;:]+$', '', name).strip()
                # Capitalize properly
                if name:
                    return name.title()
        
        return None
    
    def save(self, filename):
        data = {
            'weights': self.weights,
            'biases': self.biases,
            'vocab': self.vocab,
            'intents': self.intents,
            'responses': self.responses,
            'bot_name': self.bot_name,
            'use_api_enhancement': self.use_api_enhancement
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        
        # Also save learning data
        if self.learner:
            self.learner.save()
        if self.long_memory:
            self.long_memory.save()
        
        print(f"Chatbot saved to {filename}")
    
    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            self.weights = data['weights']
            self.biases = data['biases']
            self.vocab = data['vocab']
            self.intents = data['intents']
            self.responses = data['responses']
            self.bot_name = data.get('bot_name', 'ChatBot')  # Load bot name or use default
            self.use_api_enhancement = data.get('use_api_enhancement', False)
            
            # Also load learning data
            if self.learner:
                self.learner.load()
            if self.long_memory:
                self.long_memory.load()
            
            # Try to initialize API learning with env variable
            if self.use_api_enhancement and os.environ.get("OPENAI_API_KEY"):
                self.setup_api_learning()
            
            print(f"Chatbot loaded from {filename}")
            return True
        return False
    
    def get_learning_stats(self):
        """Get statistics about what the bot has learned"""
        stats = {
            'learned_responses': 0,
            'relationship_level': 0,
            'total_conversations': 0,
            'mood': 0.5
        }
        
        if self.learner:
            stats['learned_responses'] = sum(len(v) for v in self.learner.learned_responses.values())
        
        if self.long_memory:
            stats['relationship_level'] = self.long_memory.relationship_level
            stats['total_conversations'] = self.long_memory.user_profile.get('total_conversations', 0)
        
        if self.personality:
            stats['mood'] = self.personality.mood
        
        return stats


if __name__ == "__main__":
    model_file = "chatbot_model.pkl"
    memory_file = "chatbot_memory.pkl"
    
    # Build vocabulary and get size
    temp_bot = NeuralChatbot([1, 1])  # Temporary to build vocab
    vocab_size = temp_bot.build_vocab(training_data)
    num_intents = len(training_data)
    
    print(f"Vocabulary size: {vocab_size}")
    print(f"Number of intents: {num_intents}")
    
    # Create chatbot with proper architecture
    chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
    chatbot.vocab = temp_bot.vocab
    chatbot.responses = responses
    
    # Train the text generator on responses
    print("Training text generator...")
    chatbot.generator.train_from_responses(responses)
    
    # Check for saved model
    model_loaded = chatbot.load(model_file)
    
    # Check if intents have changed (new intents added)
    if model_loaded:
        saved_intents = set(chatbot.intents)
        current_intents = set(training_data.keys())
        if saved_intents != current_intents:
            print(f"\n⚠️  Intent mismatch detected!")
            print(f"   Saved model has {len(saved_intents)} intents: {saved_intents}")
            print(f"   Current config has {len(current_intents)} intents: {current_intents}")
            print(f"   New intents: {current_intents - saved_intents}")
            print(f"   Removed intents: {saved_intents - current_intents}")
            print("\n🔄 Rebuilding model with new architecture...")
            
            # Rebuild the chatbot with correct architecture
            chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
            chatbot.vocab = temp_bot.vocab
            chatbot.responses = responses
            chatbot.generator.train_from_responses(responses)
            model_loaded = False  # Force retraining
    
    if not model_loaded:
        print("\nTraining chatbot...")
        
        # Prepare and train
        X, y = chatbot.prepare_training_data(training_data)
        
        for epoch in range(1000):
            chatbot.train(X, y, epochs=1)
            if (epoch + 1) % 100 == 0:
                predictions = chatbot.predict(X)
                accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                print(f"Epoch {epoch + 1} - Accuracy: {accuracy:.2%}")
        
        chatbot.save(model_file)
    
    # Load memory from previous sessions
    if chatbot.memory.load(memory_file):
        if chatbot.memory.user_name:
            print(f"Welcome back, {chatbot.memory.user_name}!")
    
    # Main menu loop
    while True:
        print("\n" + "="*50)
        print("       NEURAL CHATBOT MAIN MENU")
        print("="*50)
        print("1. Chat with the bot")
        print("2. Train the bot (add new responses)")
        print("3. View current intents")
        print("4. Test bot accuracy")
        print("5. Increase accuracy")
        print("6. Retrain from scratch")
        print("7. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        # Option 1: Chat mode
        if choice == "1":
            print("\n" + "="*50)
            print("CHAT MODE")
            print("="*50)
            print("Commands:")
            print("  'menu' or 'back' - Return to main menu")
            print("  'help'           - Show these commands")
            print("  'clear'          - Clear conversation memory")
            print("  'facts'          - Show what I know about you")
            print("="*50 + "\n")
            
            while True:
                user_input = input("You: ").strip()
                
                # Exit commands
                if user_input.lower() in ['menu', 'back', 'exit', 'quit', 'q']:
                    print("\nReturning to main menu...")
                    break
                
                # Help command
                if user_input.lower() == 'help':
                    print("\n--- Chat Commands ---")
                    print("  'menu' or 'back' - Return to main menu")
                    print("  'help'           - Show these commands")
                    print("  'clear'          - Clear conversation memory")
                    print("  'facts'          - Show what I know about you")
                    print("---------------------\n")
                    continue
                
                # Clear memory command
                if user_input.lower() == 'clear':
                    chatbot.memory.conversation_history = []
                    chatbot.memory.message_count = 0
                    print("Bot: Conversation memory cleared!\n")
                    continue
                
                # Show facts command
                if user_input.lower() == 'facts':
                    if chatbot.memory.user_facts or chatbot.memory.user_name:
                        print("\n--- What I know about you ---")
                        if chatbot.memory.user_name:
                            print(f"  Name: {chatbot.memory.user_name}")
                        for key, value in chatbot.memory.user_facts.items():
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                        print("-----------------------------\n")
                    else:
                        print("Bot: I don't know much about you yet. Tell me something!\n")
                    continue
                
                if not user_input:
                    continue
                
                response = chatbot.get_response(user_input)
                print(f"Bot: {response}\n")
        
        # Option 2: Training mode
        elif choice == "2":
            print("\n" + "="*50)
            print("TRAINING MODE")
            print("="*50)
            print("\nOptions:")
            print("a. Add phrases to existing intent")
            print("b. Add responses to existing intent")
            print("c. Create new intent")
            print("d. Back to main menu")
            
            train_choice = input("\nEnter choice (a-d): ").strip().lower()
            
            if train_choice == "a":
                print("\nAvailable intents:")
                for i, intent in enumerate(chatbot.intents, 1):
                    print(f"  {i}. {intent}")
                
                try:
                    intent_num = int(input("\nEnter intent number: ")) - 1
                    if 0 <= intent_num < len(chatbot.intents):
                        intent_name = chatbot.intents[intent_num]
                        print(f"\nAdding phrases to '{intent_name}'")
                        print("Enter phrases (one per line, empty line to finish):")
                        
                        new_phrases = []
                        while True:
                            phrase = input("  > ").strip()
                            if not phrase:
                                break
                            new_phrases.append(phrase)
                            training_data[intent_name].append(phrase)
                        
                        if new_phrases:
                            # Rebuild vocab and retrain
                            print(f"\nAdded {len(new_phrases)} phrases. Retraining...")
                            chatbot.build_vocab(training_data)
                            X, y = chatbot.prepare_training_data(training_data)
                            
                            # Quick retrain
                            for epoch in range(500):
                                chatbot.train(X, y, epochs=1)
                            
                            chatbot.save(model_file)
                            print("Training complete!")
                    else:
                        print("Invalid intent number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif train_choice == "b":
                print("\nAvailable intents:")
                for i, intent in enumerate(chatbot.intents, 1):
                    print(f"  {i}. {intent}")
                
                try:
                    intent_num = int(input("\nEnter intent number: ")) - 1
                    if 0 <= intent_num < len(chatbot.intents):
                        intent_name = chatbot.intents[intent_num]
                        print(f"\nAdding responses to '{intent_name}'")
                        print("Enter responses (one per line, empty line to finish):")
                        
                        new_responses = []
                        while True:
                            response = input("  > ").strip()
                            if not response:
                                break
                            new_responses.append(response)
                            responses[intent_name].append(response)
                        
                        if new_responses:
                            chatbot.responses = responses
                            chatbot.generator.train_from_responses(responses)
                            print(f"\nAdded {len(new_responses)} responses!")
                    else:
                        print("Invalid intent number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif train_choice == "c":
                print("\nCreate new intent")
                intent_name = input("Enter intent name (e.g., 'compliment'): ").strip().lower()
                
                if intent_name and intent_name not in training_data:
                    print(f"\nEnter training phrases for '{intent_name}'")
                    print("(These are example inputs the bot should recognize)")
                    print("Enter phrases (one per line, empty line to finish):")
                    
                    new_phrases = []
                    while True:
                        phrase = input("  > ").strip()
                        if not phrase:
                            break
                        new_phrases.append(phrase)
                    
                    if len(new_phrases) >= 3:
                        print(f"\nEnter responses for '{intent_name}'")
                        print("(These are what the bot will say back)")
                        print("Enter responses (one per line, empty line to finish):")
                        
                        new_responses = []
                        while True:
                            response = input("  > ").strip()
                            if not response:
                                break
                            new_responses.append(response)
                        
                        if len(new_responses) >= 1:
                            # Add to training data
                            training_data[intent_name] = new_phrases
                            responses[intent_name] = new_responses
                            
                            # Rebuild everything
                            print("\nRebuilding and retraining chatbot...")
                            vocab_size = chatbot.build_vocab(training_data)
                            num_intents = len(training_data)
                            
                            # Create new chatbot with updated architecture
                            chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
                            chatbot.build_vocab(training_data)
                            chatbot.responses = responses
                            chatbot.generator.train_from_responses(responses)
                            
                            X, y = chatbot.prepare_training_data(training_data)
                            
                            for epoch in range(1000):
                                chatbot.train(X, y, epochs=1)
                                if (epoch + 1) % 200 == 0:
                                    predictions = chatbot.predict(X)
                                    accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                                    print(f"Epoch {epoch + 1} - Accuracy: {accuracy:.2%}")
                            
                            chatbot.save(model_file)
                            print(f"\nIntent '{intent_name}' created successfully!")
                        else:
                            print("Need at least 1 response.")
                    else:
                        print("Need at least 3 training phrases.")
                elif intent_name in training_data:
                    print("Intent already exists! Use option 'a' to add phrases.")
                else:
                    print("Invalid intent name.")
        
        # Option 3: View intents
        elif choice == "3":
            print("\n" + "="*50)
            print("CURRENT INTENTS")
            print("="*50)
            for i, intent in enumerate(chatbot.intents, 1):
                num_phrases = len(training_data.get(intent, []))
                num_responses = len(responses.get(intent, []))
                print(f"{i}. {intent}")
                print(f"   Phrases: {num_phrases}, Responses: {num_responses}")
            print(f"\nTotal: {len(chatbot.intents)} intents")
        
        # Option 4: Test accuracy
        elif choice == "4":
            print("\n" + "="*50)
            print("TESTING ACCURACY")
            print("="*50)
            X, y = chatbot.prepare_training_data(training_data)
            predictions = chatbot.predict(X)
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            print(f"\nCurrent accuracy: {accuracy:.2%}")
            print(f"Training samples: {len(X)}")
            print(f"Intents: {len(chatbot.intents)}")
        
        # Option 5: Increase accuracy
        elif choice == "5":
            print("\n" + "="*50)
            print("INCREASE ACCURACY")
            print("="*50)
            
            # Show current accuracy
            X, y = chatbot.prepare_training_data(training_data)
            predictions = chatbot.predict(X)
            current_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            print(f"\nCurrent accuracy: {current_accuracy:.2%}")
            
            print("\nOptions:")
            print("a. Quick boost (500 more epochs)")
            print("b. Medium training (2000 more epochs)")
            print("c. Intensive training (5000 more epochs)")
            print("d. Custom training (choose epochs)")
            print("e. Adjust learning rate")
            print("f. Train until target accuracy")
            print("g. Data augmentation (expand training data)")
            print("h. Back to main menu")
            
            acc_choice = input("\nEnter choice (a-h): ").strip().lower()
            
            if acc_choice in ['a', 'b', 'c', 'd']:
                if acc_choice == 'a':
                    extra_epochs = 500
                elif acc_choice == 'b':
                    extra_epochs = 2000
                elif acc_choice == 'c':
                    extra_epochs = 5000
                else:
                    try:
                        extra_epochs = int(input("Enter number of epochs: "))
                    except ValueError:
                        extra_epochs = 500
                
                print(f"\nTraining for {extra_epochs} more epochs...")
                
                for epoch in range(extra_epochs):
                    chatbot.train(X, y, epochs=1)
                    if (epoch + 1) % (extra_epochs // 10) == 0:
                        predictions = chatbot.predict(X)
                        accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                        print(f"Epoch {epoch + 1}/{extra_epochs} - Accuracy: {accuracy:.2%}")
                
                # Final accuracy
                predictions = chatbot.predict(X)
                final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                print(f"\nTraining complete!")
                print(f"Accuracy improved: {current_accuracy:.2%} → {final_accuracy:.2%}")
                chatbot.save(model_file)
            
            elif acc_choice == 'e':
                print(f"\nCurrent learning rate: {chatbot.learning_rate}")
                print("Suggested values: 0.01 (slow), 0.05 (medium), 0.1 (fast), 0.2 (aggressive)")
                try:
                    new_lr = float(input("Enter new learning rate: "))
                    chatbot.learning_rate = new_lr
                    print(f"Learning rate set to {new_lr}")
                    print("Now use training options to see the effect!")
                except ValueError:
                    print("Invalid value.")
            
            elif acc_choice == 'f':
                try:
                    target = float(input("Enter target accuracy (e.g., 0.95 for 95%): "))
                    max_epochs = int(input("Enter maximum epochs (e.g., 10000): "))
                    
                    print(f"\nTraining until {target:.0%} accuracy (max {max_epochs} epochs)...")
                    
                    epoch = 0
                    best_accuracy = current_accuracy
                    patience = 0
                    
                    while epoch < max_epochs:
                        chatbot.train(X, y, epochs=1)
                        epoch += 1
                        
                        if epoch % 100 == 0:
                            predictions = chatbot.predict(X)
                            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                            print(f"Epoch {epoch} - Accuracy: {accuracy:.2%}")
                            
                            if accuracy >= target:
                                print(f"\n🎯 Target accuracy reached!")
                                break
                            
                            if accuracy > best_accuracy:
                                best_accuracy = accuracy
                                patience = 0
                            else:
                                patience += 1
                                if patience >= 20:
                                    print(f"\nNo improvement for 2000 epochs. Stopping.")
                                    break
                    
                    predictions = chatbot.predict(X)
                    final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                    print(f"\nFinal accuracy: {final_accuracy:.2%}")
                    chatbot.save(model_file)
                    
                except ValueError:
                    print("Invalid input.")
            
            elif acc_choice == 'g':
                print("\nData Augmentation - Expanding training data...")
                
                augmented_count = 0
                for intent, phrases in list(training_data.items()):
                    new_phrases = []
                    for phrase in phrases:
                        words = phrase.split()
                        
                        # Add variations
                        if len(words) > 2:
                            # Swap word order variation
                            if len(words) >= 3:
                                swapped = words.copy()
                                swapped[1], swapped[2] = swapped[2], swapped[1]
                                new_phrase = ' '.join(swapped)
                                if new_phrase not in phrases and new_phrase not in new_phrases:
                                    new_phrases.append(new_phrase)
                            
                            # Remove first word variation
                            shorter = ' '.join(words[1:])
                            if shorter not in phrases and shorter not in new_phrases and len(shorter) > 3:
                                new_phrases.append(shorter)
                        
                        # Add "please" variation
                        please_phrase = "please " + phrase
                        if please_phrase not in phrases and please_phrase not in new_phrases:
                            new_phrases.append(please_phrase)
                    
                    # Add unique new phrases
                    for np_phrase in new_phrases[:5]:  # Limit to 5 new per intent
                        training_data[intent].append(np_phrase)
                        augmented_count += 1
                
                print(f"Added {augmented_count} augmented phrases.")
                
                # Rebuild and retrain
                print("Rebuilding vocabulary and retraining...")
                vocab_size = chatbot.build_vocab(training_data)
                X, y = chatbot.prepare_training_data(training_data)
                
                for epoch in range(1000):
                    chatbot.train(X, y, epochs=1)
                    if (epoch + 1) % 200 == 0:
                        predictions = chatbot.predict(X)
                        accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                        print(f"Epoch {epoch + 1} - Accuracy: {accuracy:.2%}")
                
                predictions = chatbot.predict(X)
                final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                print(f"\nAugmentation complete! Accuracy: {final_accuracy:.2%}")
                chatbot.save(model_file)
        
        # Option 6: Retrain
        elif choice == "6":
            confirm = input("\nThis will retrain from scratch. Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                print("\nRetraining chatbot...")
                
                # Rebuild vocab
                vocab_size = chatbot.build_vocab(training_data)
                num_intents = len(training_data)
                
                # Create fresh chatbot
                chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
                chatbot.build_vocab(training_data)
                chatbot.responses = responses
                chatbot.generator.train_from_responses(responses)
                
                X, y = chatbot.prepare_training_data(training_data)
                
                for epoch in range(1000):
                    chatbot.train(X, y, epochs=1)
                    if (epoch + 1) % 100 == 0:
                        predictions = chatbot.predict(X)
                        accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
                        print(f"Epoch {epoch + 1} - Accuracy: {accuracy:.2%}")
                
                chatbot.save(model_file)
                print("\nRetraining complete!")
        
        # Option 7: Exit
        elif choice == "7":
            chatbot.memory.save(memory_file)
            print("\nGoodbye! Your data has been saved.")
            break
        
        else:
            print("\nInvalid choice. Please enter 1-7.")
