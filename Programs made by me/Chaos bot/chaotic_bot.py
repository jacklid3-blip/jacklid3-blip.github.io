"""
Chaotic Internet Bot - An experimental chatbot that trains on raw internet data
WARNING: This bot will produce unpredictable, often nonsensical, and potentially
weird responses. That's the point! It's chaos incarnate.

Usage:
    python chaotic_bot.py          # Interactive mode
    python chaotic_bot.py --gui    # GUI mode
    python chaotic_bot.py --feed   # Feed it more internet data
    
CHAOS MODES:
    - Normal: Standard Markov chaos
    - Glitch: T̷e̸x̵t̶ ̷c̵o̷r̵r̸u̵p̷t̵i̷o̵n̷
    - UwU: Tuwns evewything cute >w<
    - Conspiracy: Everything is connected...
    - Time Travel: Responses from different eras
    - Dream: Surreal stream of consciousness
    - Argument: Bot argues with itself
    - Prophecy: Vague mystical predictions
    - Screaming: MAXIMUM VOLUME
    - Backwards: .sdrawkcab gnihtyreve sekaepS
"""

import random
import re
import json
import os
import pickle
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from collections import defaultdict
from datetime import datetime
import hashlib
import time

# Web scraping imports
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    print("⚠️ Install requests and beautifulsoup4 for web scraping:")
    print("   pip install requests beautifulsoup4")


# ============== ORDER FROM CHAOS ==============

class OrderRestorer:
    """Finds order within chaos - extracts patterns, coherence, and meaning"""
    
    @staticmethod
    def find_complete_sentences(text):
        """Extract what look like complete sentences"""
        # Split on sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        complete = []
        
        for s in sentences:
            s = s.strip()
            # Check for sentence-like structure (starts capital, has verb-like words, reasonable length)
            if (len(s) > 15 and len(s) < 200 and 
                s[0].isupper() and 
                any(word in s.lower() for word in ['is', 'are', 'was', 'were', 'have', 'has', 'the', 'a', 'an'])):
                complete.append(s)
        
        return complete
    
    @staticmethod
    def extract_wisdom(chain, num_wisdoms=5):
        """Try to extract profound-sounding statements from the chaos"""
        wisdom_starters = ['the', 'life', 'we', 'you', 'all', 'time', 'love', 'truth', 'people', 'never', 'always']
        wisdom_endings = ['.', '!', 'truth', 'life', 'heart', 'mind', 'soul', 'world', 'way', 'end']
        
        wisdoms = []
        for key in chain.keys():
            first_word = key[0].lower().strip('"\'')
            if first_word in wisdom_starters:
                # Build a potential wisdom
                words = list(key)
                current = key
                for _ in range(15):  # Max 15 words
                    if current in chain:
                        next_word = random.choice(chain[current])
                        words.append(next_word)
                        current = tuple(list(current)[1:] + [next_word])
                        # Check for natural ending
                        if next_word.endswith(('.', '!', '?')):
                            break
                    else:
                        break
                
                wisdom = ' '.join(words)
                if len(wisdom) > 30 and len(wisdom) < 150:
                    wisdoms.append(wisdom)
        
        random.shuffle(wisdoms)
        return wisdoms[:num_wisdoms]
    
    @staticmethod
    def find_themes(chain, top_n=10):
        """Find the most common themes/words in the absorbed data"""
        word_freq = defaultdict(int)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
                      'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
                      'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
                      'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just', 'that',
                      'this', 'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she', 'we',
                      'they', 'my', 'your', 'his', 'her', 'our', 'their', 'what', 'which',
                      'who', 'whom', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
                      'any', 'some', 'no', 'if', 'then', 'else', 'about', 'after', 'before'}
        
        for key in chain.keys():
            for word in key:
                clean_word = re.sub(r'[^a-zA-Z]', '', word.lower())
                if clean_word and len(clean_word) > 3 and clean_word not in stop_words:
                    word_freq[clean_word] += 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
    
    @staticmethod
    def crystallize(chain, seed_word=None, max_length=30):
        """Attempt to build coherent thought from chaos, favoring common patterns"""
        if not chain:
            return "The void contains no patterns yet."
        
        # Find high-frequency chains (more likely to be coherent)
        chain_scores = {}
        for key, values in chain.items():
            # Score based on frequency and sentence-start likelihood
            score = len(values)  # Frequency
            if key[0][0].isupper():  # Bonus for capital start
                score *= 2
            chain_scores[key] = score
        
        # Sort by score and pick from top chains
        sorted_chains = sorted(chain_scores.items(), key=lambda x: x[1], reverse=True)
        top_chains = [k for k, v in sorted_chains[:50]]
        
        if seed_word:
            # Try to find a chain containing the seed word
            for key in top_chains:
                if seed_word.lower() in ' '.join(key).lower():
                    current = list(key)
                    break
            else:
                current = list(random.choice(top_chains)) if top_chains else list(random.choice(list(chain.keys())))
        else:
            current = list(random.choice(top_chains)) if top_chains else list(random.choice(list(chain.keys())))
        
        result = list(current)
        
        for _ in range(max_length):
            key = tuple(current)
            if key not in chain:
                break
            
            # Pick the most common next word (order from chaos)
            next_words = chain[key]
            word_counts = defaultdict(int)
            for w in next_words:
                word_counts[w] += 1
            
            # 70% chance to pick most common, 30% random (some chaos remains)
            if random.random() < 0.7:
                next_word = max(word_counts.items(), key=lambda x: x[1])[0]
            else:
                next_word = random.choice(next_words)
            
            result.append(next_word)
            current = current[1:] + [next_word]
            
            # Stop at sentence end
            if next_word.endswith(('.', '!', '?')) and len(result) > 8:
                break
        
        return ' '.join(result)
    
    @staticmethod
    def generate_summary(chain, num_sentences=3):
        """Generate a summary-like paragraph from the most coherent chains"""
        sentences = []
        for _ in range(num_sentences * 2):  # Generate extra, pick best
            sentence = OrderRestorer.crystallize(chain)
            if sentence.endswith(('.', '!', '?')):
                sentences.append(sentence)
        
        # Pick the ones that look most complete
        good_sentences = [s for s in sentences if len(s) > 30 and len(s) < 200]
        random.shuffle(good_sentences)
        return ' '.join(good_sentences[:num_sentences])
    
    @staticmethod
    def find_questions(chain):
        """Extract question-like patterns from the chaos"""
        question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which', 'is', 'are', 'do', 'does', 'can', 'could', 'would', 'should']
        questions = []
        
        for key in chain.keys():
            if key[0].lower().strip() in question_words:
                # Build the question
                words = list(key)
                current = key
                for _ in range(12):
                    if current in chain:
                        next_word = random.choice(chain[current])
                        words.append(next_word)
                        current = tuple(list(current)[1:] + [next_word])
                        if next_word.endswith('?'):
                            break
                    else:
                        break
                
                question = ' '.join(words)
                if not question.endswith('?'):
                    question += '?'
                if len(question) > 15 and len(question) < 100:
                    questions.append(question)
        
        random.shuffle(questions)
        return questions[:5]
    
    @staticmethod
    def clean_text(text):
        """Remove chaos artifacts and clean up text"""
        # Remove zalgo
        text = re.sub(r'[\u0300-\u036f\u0489]', '', text)
        # Remove excessive punctuation
        text = re.sub(r'[!?]{2,}', '!', text)
        text = re.sub(r'\.{3,}', '...', text)
        # Remove emoji clusters
        text = re.sub(r'[\U0001F300-\U0001F9FF]{2,}', '', text)
        # Fix spacing
        text = re.sub(r'\s+', ' ', text)
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        return text


# ============== CHAOS TRANSFORMERS ==============

class ChaosTransformers:
    """Text transformation engines for maximum chaos"""
    
    # Zalgo characters for glitch text
    ZALGO_UP = ['̍', '̎', '̄', '̅', '̿', '̑', '̆', '̐', '͒', '͗', '͑', '̇', '̈', '̊', '͂', '̓', '̈́', '͊', '͋', '͌', '̃', '̂', '̌', '͐', '̀', '́', '̋', '̏', '̒', '̓', '̔', '̽', '̉', 'ͣ', 'ͤ', 'ͥ', 'ͦ', 'ͧ', 'ͨ', 'ͩ', 'ͪ', 'ͫ', 'ͬ', 'ͭ', 'ͮ', 'ͯ', '̾', '͛', '͆', '̚']
    ZALGO_MID = ['̕', '̛', '̀', '́', '͘', '̡', '̢', '̧', '̨', '̴', '̵', '̶', '͜', '͝', '͞', '͟', '͠', '͢', '̸', '̷', '͡']
    ZALGO_DOWN = ['̖', '̗', '̘', '̙', '̜', '̝', '̞', '̟', '̠', '̤', '̥', '̦', '̩', '̪', '̫', '̬', '̭', '̮', '̯', '̰', '̱', '̲', '̳', '̹', '̺', '̻', '̼', 'ͅ', '͇', '͈', '͉', '͍', '͎', '͓', '͔', '͕', '͖', '͙', '͚', '̣']
    
    @staticmethod
    def glitch(text, intensity=0.5):
        """Add Z̷a̸l̵g̶o̷ text corruption"""
        result = []
        for char in text:
            result.append(char)
            if random.random() < intensity and char.strip():
                # Add random combining characters
                num_up = random.randint(0, int(3 * intensity))
                num_mid = random.randint(0, int(2 * intensity))
                num_down = random.randint(0, int(3 * intensity))
                
                for _ in range(num_up):
                    result.append(random.choice(ChaosTransformers.ZALGO_UP))
                for _ in range(num_mid):
                    result.append(random.choice(ChaosTransformers.ZALGO_MID))
                for _ in range(num_down):
                    result.append(random.choice(ChaosTransformers.ZALGO_DOWN))
        return ''.join(result)
    
    @staticmethod
    def uwuify(text):
        """UwU-ify text for maximum cringe"""
        # Replace patterns
        replacements = [
            (r'[rl]', 'w'),
            (r'[RL]', 'W'),
            (r'n([aeiou])', r'ny\1'),
            (r'N([aeiou])', r'Ny\1'),
            (r'N([AEIOU])', r'NY\1'),
            (r'ove', 'uv'),
            (r'th', 'd'),
            (r'TH', 'D'),
        ]
        
        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        # Add random faces
        faces = [' >w< ', ' UwU ', ' OwO ', ' ^w^ ', ' :3 ', ' ~w~ ', ' >:3 ', ' ;w; ']
        words = result.split()
        for i in range(len(words)):
            if random.random() < 0.15:
                words[i] = words[i] + random.choice(faces)
        
        # Add stuttering
        if words and random.random() < 0.3:
            words[0] = words[0][0] + '-' + words[0] if words[0] else words[0]
        
        return ' '.join(words)
    
    @staticmethod
    def conspiracy(text):
        """Add conspiracy theory vibes"""
        connectors = [
            "...but THEY don't want you to know that ",
            " (which is EXACTLY what they predicted) ",
            "...coincidence? I THINK NOT! ",
            " *adjusts tinfoil hat* ",
            "...follow the money and you'll find ",
            " [REDACTED] ",
            "...wake up sheeple! ",
            " (the government is watching) ",
            "...and it all connects to ",
            " *whispers* the truth is out there... ",
            "...Big [NOUN] doesn't want you to see this ",
            " 👁️ THEY'RE LISTENING 👁️ ",
        ]
        
        words = text.split()
        if len(words) > 5:
            insert_pos = random.randint(3, len(words) - 2)
            words.insert(insert_pos, random.choice(connectors))
        
        prefix = random.choice([
            "WAKE UP! ", "Listen closely... ", "They've been hiding this: ",
            "The TRUTH: ", "What they DON'T teach you: ", "🔺 ILLUMINATI CONFIRMED: "
        ])
        
        suffix = random.choice([
            " ...do your own research.", " ...SPREAD THE WORD!", 
            " ...the rabbit hole goes deeper.", " ...question everything!",
            " ...THEY can't silence us all!", " 🔍👁️🔺"
        ])
        
        return prefix + ' '.join(words) + suffix
    
    @staticmethod
    def time_travel(text, era=None):
        """Respond as if from a different time period"""
        eras = {
            'medieval': {
                'prefix': ['Hark! ', 'Prithee, ', 'Forsooth! ', 'By mine troth, ', 'Hear ye! '],
                'suffix': [', good sirrah.', ', by the saints!', ', methinks.', ', verily!', ', thou knave!'],
                'replacements': [('you', 'thou'), ('your', 'thy'), ('are', 'art'), ('is', "'tis"), ('the', 'ye')]
            },
            'pirate': {
                'prefix': ['Arrr! ', 'Avast! ', 'Shiver me timbers! ', 'Blimey! ', 'Yo ho ho! '],
                'suffix': [', ye scurvy dog!', ', matey!', ', or walk the plank!', ', savvy?', ', yarr!'],
                'replacements': [('my', 'me'), ('you', 'ye'), ('is', 'be'), ('are', 'be'), ('ing', "in'")]
            },
            'victorian': {
                'prefix': ['I say! ', 'Most certainly, ', 'Indeed, ', 'Quite so! ', 'How extraordinary! '],
                'suffix': [', I daresay.', ', most peculiar.', ', how dreadfully exciting.', ', what what!', ', pip pip!'],
                'replacements': [('very', 'exceedingly'), ('good', 'splendid'), ('bad', 'most unfortunate')]
            },
            'future': {
                'prefix': ['*beep boop* ', 'INITIALIZING: ', 'Year 3000 update: ', '[QUANTUM TRANSMISSION] ', 'From the singularity: '],
                'suffix': [' ...end transmission.', ' *processing*', ' [TEMPORAL ANOMALY DETECTED]', ' ...the machines remember.', ' 🤖'],
                'replacements': [('human', 'carbon-unit'), ('think', 'compute'), ('feel', 'process'), ('love', 'optimize for')]
            },
            'caveman': {
                'prefix': ['UGH! ', 'OOGA BOOGA! ', '*bonk* ', 'Me say: ', 'Fire good! '],
                'suffix': [' ...me confused.', ' *scratches head*', ' ...where mammoth?', ' UGH!', ' ...me hungry.'],
                'replacements': [('I', 'me'), ('am', ''), ('the', ''), ('is', ''), ('are', '')]
            },
            '1990s': {
                'prefix': ['Yo! ', 'Word! ', 'All that and a bag of chips! ', 'Talk to the hand! ', 'As if! '],
                'suffix': [' ...NOT!', ' Psych!', ' ...whatever!', ' Boo-yah!', ' ...eat my shorts!'],
                'replacements': [('cool', 'phat'), ('good', 'da bomb'), ('bad', 'bogus'), ('great', 'all that')]
            }
        }
        
        era = era or random.choice(list(eras.keys()))
        style = eras[era]
        
        result = text
        for old, new in style['replacements']:
            result = re.sub(rf'\b{old}\b', new, result, flags=re.IGNORECASE)
        
        return random.choice(style['prefix']) + result + random.choice(style['suffix'])
    
    @staticmethod
    def dream_mode(text):
        """Surreal dream-like transformation"""
        dream_inserts = [
            "...suddenly the walls were made of cheese...",
            "...my teeth started falling out but they were actually piano keys...",
            "...I was late for an exam I didn't study for...",
            "...everyone was there but their faces kept shifting...",
            "...I tried to run but my legs were made of spaghetti...",
            "...the clock melted like in that painting...",
            "...I realized I forgot to wear pants...",
            "...a giant fish asked me for directions...",
            "...the sky was the wrong color, you know?...",
            "...everything was underwater but I could still breathe...",
        ]
        
        # Random capitalization and spacing
        words = text.split()
        dream_words = []
        for word in words:
            if random.random() < 0.2:
                word = word.upper()
            if random.random() < 0.1:
                word = '~' + word + '~'
            if random.random() < 0.15:
                word = word + '...'
            dream_words.append(word)
        
        # Insert dream fragments
        if len(dream_words) > 3:
            insert_pos = random.randint(1, len(dream_words) - 1)
            dream_words.insert(insert_pos, random.choice(dream_inserts))
        
        prefix = random.choice([
            "💭 *in a hazy voice* ", "🌙 Last night I dreamt that ",
            "✨ *everything feels floaty* ", "😴 ...and then, somehow... ",
            "🌀 *reality shifts* "
        ])
        
        return prefix + ' '.join(dream_words)
    
    @staticmethod
    def argument_with_self(text):
        """Bot argues with itself"""
        responses = [
            f"Actually, {text}\n   🤔 Wait no, that's stupid.\n   😤 NO IT'S NOT!\n   🙄 Yes it is, you absolute walnut.",
            f"{text}\n   👆 THIS!\n   👇 No, THIS is wrong.\n   🤷 I literally just said it.\n   😡 And you were WRONG!",
            f"Hmm... {text}\n   🧠 Actually my brain says otherwise.\n   💀 Your brain is a potato.\n   😢 That hurt...\n   😈 Good.",
            f"{text}\n   ✅ Correct!\n   ❌ WRONG!\n   ✅ I said CORRECT!\n   ❌ And I said WRONG!\n   🤝 ...agree to disagree?\n   ❌ NO!",
        ]
        return random.choice(responses)
    
    @staticmethod
    def prophecy(text):
        """Mystical prophecy mode"""
        openings = [
            "🔮 The ancient scrolls foretell: ",
            "✨ When the stars align, ",
            "🌙 The prophecy speaks: ",
            "📜 It was written long ago that ",
            "🕯️ *gazes into crystal ball* I see... ",
            "⚡ The spirits whisper: ",
        ]
        
        middles = [
            "...when the chosen one arrives...",
            "...in the time of great uncertainty...",
            "...as darkness falls upon the land...",
            "...where shadows meet the dawn...",
        ]
        
        endings = [
            " ...but the future is always in motion.",
            " ...or maybe not, who knows.",
            " ...this is your destiny. Or Tuesday.",
            " ...the signs are unclear, try again later.",
            " 🎱 ...reply hazy, ask again.",
            " ...beware the ides of March. And Mondays.",
        ]
        
        words = text.split()
        if len(words) > 4:
            words.insert(len(words)//2, random.choice(middles))
        
        return random.choice(openings) + ' '.join(words) + random.choice(endings)
    
    @staticmethod
    def screaming(text):
        """MAXIMUM VOLUME"""
        text = text.upper()
        
        # Add random emphasis
        words = text.split()
        screamy_words = []
        for word in words:
            if random.random() < 0.3:
                word = '*' + word + '*'
            if random.random() < 0.2:
                word = word + '!'
            if random.random() < 0.15:
                # Stretch vowels
                for vowel in 'AEIOU':
                    if vowel in word:
                        word = word.replace(vowel, vowel * random.randint(2, 4), 1)
                        break
            screamy_words.append(word)
        
        prefix = random.choice(['😱 ', '🔊 ', '📢 ', '‼️ ', '⚠️ '])
        suffix = random.choice(['!!!', '!!!!1!', '! ! !', '!!1!one!', '!!!11'])
        
        return prefix + ' '.join(screamy_words) + suffix
    
    @staticmethod
    def backwards(text):
        """Speak backwards"""
        words = text.split()
        backwards_words = [word[::-1] for word in words]
        return '🔄 ' + ' '.join(backwards_words[::-1]) + ' 🔄'
    
    @staticmethod
    def emoji_chaos(text):
        """Inject random emojis EVERYWHERE"""
        emojis = ['😂', '💀', '🔥', '✨', '👀', '🤔', '😤', '🥺', '💅', '🙈', 
                  '🌈', '🦆', '🍕', '👽', '🤡', '💩', '🎉', '😈', '🌀', '⚡',
                  '🦑', '🌮', '🧠', '👁️', '🔮', '🎭', '🌶️', '🦀', '🍄', '🪐']
        
        words = text.split()
        chaotic_words = []
        for word in words:
            chaotic_words.append(word)
            if random.random() < 0.4:
                chaotic_words.append(random.choice(emojis))
        
        # Add emoji borders
        border = ''.join(random.choices(emojis, k=3))
        return border + ' ' + ' '.join(chaotic_words) + ' ' + border
    
    @staticmethod
    def drunk(text):
        """Drunk typing simulation"""
        result = []
        for char in text:
            if random.random() < 0.1:
                # Duplicate character
                result.append(char * random.randint(2, 4))
            elif random.random() < 0.08:
                # Skip character
                continue
            elif random.random() < 0.08:
                # Wrong character (nearby on keyboard)
                keyboard_neighbors = {
                    'a': 'sq', 'b': 'vn', 'c': 'xv', 'd': 'sf', 'e': 'wr',
                    'f': 'dg', 'g': 'fh', 'h': 'gj', 'i': 'uo', 'j': 'hk',
                    'k': 'jl', 'l': 'k;', 'm': 'n,', 'n': 'bm', 'o': 'ip',
                    'p': 'o[', 'q': 'wa', 'r': 'et', 's': 'ad', 't': 'ry',
                    'u': 'yi', 'v': 'cb', 'w': 'qe', 'x': 'zc', 'y': 'tu', 'z': 'x'
                }
                lower = char.lower()
                if lower in keyboard_neighbors:
                    result.append(random.choice(keyboard_neighbors[lower]))
                else:
                    result.append(char)
            else:
                result.append(char)
        
        drunk_text = ''.join(result)
        
        prefixes = ["*hic* ", "duuude... ", "lisssten... ", "heyyy ", "wait wait wait... "]
        suffixes = [" *hic*", " ...u know?", " ...imm fine", " lolol", " ...wait what was i saying"]
        
        return random.choice(prefixes) + drunk_text + random.choice(suffixes)
    
    @staticmethod
    def keyboard_smash(text):
        """Add keyboard smashing"""
        smashes = [
            "asjdfkljasdf", "lksjdflkjsdf", "asdjfhaksdjfh", "qwjekrhjqwkejr",
            "lkjsadflkjsadf", "mnbvcxz", "qwertyuiop", "zxcvbnm", "asdfghjkl",
            "aaaaaaaaa", "sksksksk", "jdhfjsdhfj", "KJSDHFKJSDHF"
        ]
        
        words = text.split()
        if len(words) > 3:
            insert_pos = random.randint(1, len(words))
            words.insert(insert_pos, random.choice(smashes))
        
        return ' '.join(words) + ' ' + random.choice(smashes)
    
    @staticmethod
    def mock_spongebob(text):
        """mOcKiNg SpOnGeBoB tExT"""
        result = []
        for i, char in enumerate(text):
            if char.isalpha():
                if random.random() < 0.5:
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                result.append(char)
        return '🧽 ' + ''.join(result)
    
    @staticmethod
    def vaporwave(text):
        """Ａ Ｅ Ｓ Ｔ Ｈ Ｅ Ｔ Ｉ Ｃ  text"""
        # Convert to fullwidth characters
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr(ord(char) - ord('a') + ord('ａ')))
            elif 'A' <= char <= 'Z':
                result.append(chr(ord(char) - ord('A') + ord('Ａ')))
            elif '0' <= char <= '9':
                result.append(chr(ord(char) - ord('0') + ord('０')))
            elif char == ' ':
                result.append('  ')  # Double space for aesthetic
            else:
                result.append(char)
        
        return '🌴 ' + ''.join(result) + ' 🌴'


class ChaoticMarkovBrain:
    """A Markov chain text generator that thrives on chaos"""
    
    def __init__(self, order=2):
        self.order = order
        self.chain = defaultdict(list)
        self.starters = []
        self.word_count = 0
        self.source_count = 0
        self.sources = []
        self.forbidden_words = []  # Words to corrupt
        self.favorite_words = []   # Words to repeat
        
    def feed(self, text, source="unknown"):
        """Feed raw text into the chaos engine"""
        # Minimal cleaning - we WANT the chaos
        text = text.strip()
        if not text:
            return
            
        words = text.split()
        if len(words) < self.order + 1:
            return
            
        self.word_count += len(words)
        self.source_count += 1
        self.sources.append(source[:50])
        
        # Track interesting words
        for word in words:
            if len(word) > 8 and random.random() < 0.1:
                self.favorite_words.append(word)
        self.favorite_words = self.favorite_words[-50:]  # Keep last 50
        
        # Build chain
        for i in range(len(words) - self.order):
            key = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            self.chain[key].append(next_word)
            
            # Track sentence starters
            if i == 0 or words[i - 1].endswith(('.', '!', '?')):
                self.starters.append(key)
    
    def generate(self, max_words=50, seed=None):
        """Generate chaotic text"""
        if not self.chain:
            return "🌀 My brain is empty... feed me internet data!"
            
        # Pick starting point
        if seed:
            seed_words = seed.lower().split()
            # Try to find a chain starting with seed words
            for key in self.chain.keys():
                if any(sw in ' '.join(key).lower() for sw in seed_words):
                    current = list(key)
                    break
            else:
                current = list(random.choice(self.starters if self.starters else list(self.chain.keys())))
        else:
            current = list(random.choice(self.starters if self.starters else list(self.chain.keys())))
        
        result = list(current)
        
        for _ in range(max_words):
            key = tuple(current)
            if key not in self.chain:
                # Dead end - jump to random point for extra chaos
                if random.random() < 0.3 and self.starters:
                    current = list(random.choice(self.starters))
                    result.append("—")
                    result.extend(current)
                else:
                    break
            else:
                next_word = random.choice(self.chain[key])
                result.append(next_word)
                current = current[1:] + [next_word]
                
                # Random chance to jump (CHAOS MODE)
                if random.random() < 0.05 and self.starters:
                    result.append("...")
                    current = list(random.choice(self.starters))
                    result.extend(current)
                
                # Random chance to insert a favorite word
                if random.random() < 0.03 and self.favorite_words:
                    result.append(random.choice(self.favorite_words))
        
        return ' '.join(result)
    
    def generate_poetry(self, lines=4):
        """Generate terrible poetry"""
        poem_lines = []
        for _ in range(lines):
            line = self.generate(random.randint(5, 12))
            poem_lines.append(line)
        return '\n'.join(poem_lines)
    
    def generate_haiku(self):
        """Generate a 'haiku' (syllable counting not guaranteed)"""
        lines = [
            self.generate(random.randint(3, 5)),
            self.generate(random.randint(5, 8)),
            self.generate(random.randint(3, 5)),
        ]
        return '\n'.join(lines)
    
    def mashup(self, text1, text2):
        """Mash two texts together"""
        words1 = text1.split()
        words2 = text2.split()
        result = []
        
        i, j = 0, 0
        while i < len(words1) or j < len(words2):
            if random.random() < 0.5 and i < len(words1):
                result.append(words1[i])
                i += 1
            elif j < len(words2):
                result.append(words2[j])
                j += 1
            else:
                result.append(words1[i] if i < len(words1) else words2[j])
                i += 1
                j += 1
        
        return ' '.join(result)
    
    def save(self, filepath):
        """Save the chaos"""
        data = {
            'chain': dict(self.chain),
            'starters': self.starters,
            'order': self.order,
            'word_count': self.word_count,
            'source_count': self.source_count,
            'sources': self.sources[-100:],  # Keep last 100 sources
            'favorite_words': self.favorite_words,
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath):
        """Load previous chaos"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.chain = defaultdict(list, {tuple(k) if isinstance(k, list) else k: v 
                                                 for k, v in data['chain'].items()})
                self.starters = data['starters']
                self.order = data.get('order', 2)
                self.word_count = data.get('word_count', 0)
                self.source_count = data.get('source_count', 0)
                self.sources = data.get('sources', [])
                self.favorite_words = data.get('favorite_words', [])
                return True
        return False


class InternetHarvester:
    """Harvests raw text from the internet for maximum chaos"""
    
    # Diverse sources for maximum chaos - 250+ sources!
    CHAOS_SOURCES = [
        # === NEWS & CURRENT EVENTS ===
        "https://www.reuters.com/",
        "https://news.ycombinator.com/",
        "https://www.bbc.com/news",
        "https://www.theonion.com/",
        "https://apnews.com/",
        "https://www.npr.org/",
        "https://www.theguardian.com/",
        "https://www.aljazeera.com/",
        "https://www.vice.com/",
        "https://www.vox.com/",
        "https://www.theatlantic.com/",
        "https://www.newyorker.com/",
        "https://www.wired.com/",
        "https://gizmodo.com/",
        "https://www.cnet.com/",
        "https://mashable.com/",
        "https://www.thedailybeast.com/",
        "https://www.salon.com/",
        "https://www.slate.com/",
        "https://www.huffpost.com/",
        
        # === WIKIPEDIA & WIKIS ===
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://simple.wikipedia.org/wiki/Special:Random",
        "https://simple.wikipedia.org/wiki/Special:Random",
        "https://en.wikiquote.org/wiki/Special:Random",
        "https://en.wiktionary.org/wiki/Special:Random",
        "https://en.wikinews.org/wiki/Special:Random",
        "https://commons.wikimedia.org/wiki/Special:Random",
        "https://rationalwiki.org/wiki/Special:Random",
        
        # === REDDIT - THE CHAOS GOLDMINE (100+ subreddits) ===
        # Text-heavy discussion subs
        "https://old.reddit.com/r/all/top/?t=day",
        "https://old.reddit.com/r/AskReddit/top/?t=week",
        "https://old.reddit.com/r/AskReddit/top/?t=month",
        "https://old.reddit.com/r/askscience/top/?t=week",
        "https://old.reddit.com/r/askhistorians/top/?t=week",
        "https://old.reddit.com/r/AskMen/top/?t=week",
        "https://old.reddit.com/r/AskWomen/top/?t=week",
        "https://old.reddit.com/r/AskOldPeople/top/?t=week",
        "https://old.reddit.com/r/NoStupidQuestions/top/?t=week",
        "https://old.reddit.com/r/TooAfraidToAsk/top/?t=week",
        "https://old.reddit.com/r/ExplainLikeImFive/top/?t=week",
        "https://old.reddit.com/r/OutOfTheLoop/top/?t=week",
        
        # Stories & experiences
        "https://old.reddit.com/r/tifu/top/?t=week",
        "https://old.reddit.com/r/TIFU/top/?t=month",
        "https://old.reddit.com/r/confession/top/?t=week",
        "https://old.reddit.com/r/confessions/top/?t=week",
        "https://old.reddit.com/r/offmychest/top/?t=week",
        "https://old.reddit.com/r/TrueOffMyChest/top/?t=week",
        "https://old.reddit.com/r/self/top/?t=week",
        "https://old.reddit.com/r/CasualConversation/top/?t=week",
        "https://old.reddit.com/r/PointlessStories/top/?t=week",
        "https://old.reddit.com/r/stories/top/?t=week",
        
        # Drama & judgment
        "https://old.reddit.com/r/AmItheAsshole/top/?t=week",
        "https://old.reddit.com/r/AmItheAsshole/top/?t=month",
        "https://old.reddit.com/r/relationship_advice/top/?t=week",
        "https://old.reddit.com/r/relationships/top/?t=week",
        "https://old.reddit.com/r/pettyrevenge/top/?t=week",
        "https://old.reddit.com/r/ProRevenge/top/?t=week",
        "https://old.reddit.com/r/MaliciousCompliance/top/?t=week",
        "https://old.reddit.com/r/entitledparents/top/?t=week",
        "https://old.reddit.com/r/ChoosingBeggars/top/?t=week",
        "https://old.reddit.com/r/BestofRedditorUpdates/top/?t=week",
        
        # Creative writing
        "https://old.reddit.com/r/WritingPrompts/top/?t=week",
        "https://old.reddit.com/r/nosleep/top/?t=week",
        "https://old.reddit.com/r/shortscarystories/top/?t=week",
        "https://old.reddit.com/r/twosentencehorror/top/?t=week",
        "https://old.reddit.com/r/HFY/top/?t=week",
        "https://old.reddit.com/r/creepypasta/top/?t=week",
        
        # Thoughts & ideas
        "https://old.reddit.com/r/Showerthoughts/top/?t=week",
        "https://old.reddit.com/r/Showerthoughts/top/?t=month",
        "https://old.reddit.com/r/CrazyIdeas/top/?t=week",
        "https://old.reddit.com/r/unpopularopinion/top/?t=week",
        "https://old.reddit.com/r/The10thDentist/top/?t=week",
        "https://old.reddit.com/r/changemyview/top/?t=week",
        "https://old.reddit.com/r/TrueUnpopularOpinion/top/?t=week",
        
        # Learning & facts
        "https://old.reddit.com/r/todayilearned/top/?t=week",
        "https://old.reddit.com/r/todayilearned/top/?t=month",
        "https://old.reddit.com/r/LifeProTips/top/?t=week",
        "https://old.reddit.com/r/YouShouldKnow/top/?t=week",
        "https://old.reddit.com/r/LearnUselessTalents/top/?t=week",
        "https://old.reddit.com/r/educationalgifs/top/?t=week",
        
        # Philosophy & deep stuff
        "https://old.reddit.com/r/philosophy/top/?t=week",
        "https://old.reddit.com/r/Stoicism/top/?t=week",
        "https://old.reddit.com/r/DeepThoughts/top/?t=week",
        "https://old.reddit.com/r/ExistentialSupport/top/?t=week",
        
        # Humor - text focused
        "https://old.reddit.com/r/jokes/top/?t=week",
        "https://old.reddit.com/r/Jokes/top/?t=month",
        "https://old.reddit.com/r/dadjokes/top/?t=week",
        "https://old.reddit.com/r/3amjokes/top/?t=week",
        "https://old.reddit.com/r/antijokes/top/?t=week",
        "https://old.reddit.com/r/cleanjokes/top/?t=week",
        "https://old.reddit.com/r/darkjokes/top/?t=week",
        "https://old.reddit.com/r/WordAvalanches/top/?t=week",
        "https://old.reddit.com/r/copypasta/top/?t=week",
        
        # Interesting language/text
        "https://old.reddit.com/r/BrandNewSentence/top/?t=week",
        "https://old.reddit.com/r/rareinsults/top/?t=week",
        "https://old.reddit.com/r/MurderedByWords/top/?t=week",
        "https://old.reddit.com/r/clevercomebacks/top/?t=week",
        "https://old.reddit.com/r/SuspiciouslySpecific/top/?t=week",
        "https://old.reddit.com/r/oddlyspecific/top/?t=week",
        
        # Cringe & satire
        "https://old.reddit.com/r/iamverysmart/top/?t=week",
        "https://old.reddit.com/r/im14andthisisdeep/top/?t=week",
        "https://old.reddit.com/r/notliketheothergirls/top/?t=week",
        "https://old.reddit.com/r/LinkedInLunatics/top/?t=week",
        
        # Fan theories & speculation
        "https://old.reddit.com/r/FanTheories/top/?t=week",
        "https://old.reddit.com/r/conspiracy/top/?t=week",
        "https://old.reddit.com/r/UnresolvedMysteries/top/?t=week",
        "https://old.reddit.com/r/Glitch_in_the_Matrix/top/?t=week",
        "https://old.reddit.com/r/MandelaEffect/top/?t=week",
        "https://old.reddit.com/r/Dreams/top/?t=week",
        "https://old.reddit.com/r/LucidDreaming/top/?t=week",
        "https://old.reddit.com/r/Paranormal/top/?t=week",
        "https://old.reddit.com/r/HighStrangeness/top/?t=week",
        
        # Motivation & support
        "https://old.reddit.com/r/GetMotivated/top/?t=week",
        "https://old.reddit.com/r/DecidingToBeBetter/top/?t=week",
        "https://old.reddit.com/r/selfimprovement/top/?t=week",
        "https://old.reddit.com/r/getdisciplined/top/?t=week",
        
        # Wholesome
        "https://old.reddit.com/r/MadeMeSmile/top/?t=week",
        "https://old.reddit.com/r/HumansBeingBros/top/?t=week",
        "https://old.reddit.com/r/UpliftingNews/top/?t=week",
        "https://old.reddit.com/r/wholesomememes/top/?t=week",
        
        # Rants & venting
        "https://old.reddit.com/r/rant/top/?t=week",
        "https://old.reddit.com/r/Vent/top/?t=week",
        "https://old.reddit.com/r/TalesFromRetail/top/?t=week",
        "https://old.reddit.com/r/TalesFromTechSupport/top/?t=week",
        "https://old.reddit.com/r/TalesFromYourServer/top/?t=week",
        "https://old.reddit.com/r/IDontWorkHereLady/top/?t=week",
        
        # Misc text-heavy
        "https://old.reddit.com/r/mildlyinfuriating/top/?t=week",
        "https://old.reddit.com/r/mildlyinteresting/top/?t=week",
        "https://old.reddit.com/r/interestingasfuck/top/?t=week",
        "https://old.reddit.com/r/Damnthatsinteresting/top/?t=week",
        "https://old.reddit.com/r/BeAmazed/top/?t=week",
        "https://old.reddit.com/r/nextfuckinglevel/top/?t=week",
        
        # === QUOTES & WISDOM ===
        "https://www.brainyquote.com/topics/inspirational-quotes",
        "https://www.brainyquote.com/topics/motivational-quotes",
        "https://www.brainyquote.com/topics/funny-quotes",
        "https://www.brainyquote.com/topics/life-quotes",
        "https://www.brainyquote.com/topics/love-quotes",
        "https://www.brainyquote.com/topics/wisdom-quotes",
        "https://www.brainyquote.com/topics/happiness-quotes",
        "https://www.brainyquote.com/topics/success-quotes",
        "https://www.goodreads.com/quotes",
        "https://www.goodreads.com/quotes/tag/philosophy",
        "https://www.goodreads.com/quotes/tag/humor",
        "https://www.goodreads.com/quotes/tag/inspirational",
        "https://www.azquotes.com/",
        "https://quoteinvestigator.com/",
        
        # === CLASSIC LITERATURE (Project Gutenberg) ===
        "https://www.gutenberg.org/browse/scores/top",
        "https://www.gutenberg.org/ebooks/1342",  # Pride and Prejudice
        "https://www.gutenberg.org/ebooks/84",    # Frankenstein
        "https://www.gutenberg.org/ebooks/1661",  # Sherlock Holmes
        "https://www.gutenberg.org/ebooks/11",    # Alice in Wonderland
        "https://www.gutenberg.org/ebooks/2701",  # Moby Dick
        "https://www.gutenberg.org/ebooks/1232",  # The Prince
        "https://www.gutenberg.org/ebooks/76",    # Huckleberry Finn
        "https://www.gutenberg.org/ebooks/98",    # Tale of Two Cities
        "https://www.gutenberg.org/ebooks/174",   # Picture of Dorian Gray
        "https://www.gutenberg.org/ebooks/345",   # Dracula
        "https://www.gutenberg.org/ebooks/1080",  # A Modest Proposal
        "https://www.gutenberg.org/ebooks/2554",  # Crime and Punishment
        "https://www.gutenberg.org/ebooks/2600",  # War and Peace
        "https://www.gutenberg.org/ebooks/43",    # Jekyll and Hyde
        "https://www.gutenberg.org/ebooks/768",   # Wuthering Heights
        "https://www.gutenberg.org/ebooks/1400",  # Great Expectations
        "https://www.gutenberg.org/ebooks/5200",  # Metamorphosis (Kafka)
        "https://www.gutenberg.org/ebooks/120",   # Treasure Island
        "https://www.gutenberg.org/ebooks/1260",  # Jane Eyre
        
        # === FOOD & RECIPES ===
        "https://www.allrecipes.com/",
        "https://www.food.com/",
        "https://www.epicurious.com/recipes-menus",
        "https://www.seriouseats.com/",
        "https://www.bonappetit.com/",
        "https://www.foodnetwork.com/",
        "https://www.delish.com/",
        "https://www.tasteofhome.com/",
        "https://www.simplyrecipes.com/",
        "https://www.budgetbytes.com/",
        
        # === URBAN DICTIONARY & SLANG ===
        "https://www.urbandictionary.com/random.php",
        "https://www.urbandictionary.com/random.php",
        "https://www.urbandictionary.com/random.php",
        
        # === TRIVIA & FACTS ===
        "https://www.factretriever.com/",
        "https://www.thefactsite.com/",
        "https://www.mentalfloss.com/",
        "https://www.rd.com/",
        "https://www.factslides.com/",
        "https://www.kickassfacts.com/",
        "https://unbelievable-facts.com/",
        "https://www.interestingfacts.org/",
        
        # === CREATIVE WRITING & FICTION ===
        "https://www.wattpad.com/",
        "https://archiveofourown.org/",
        "https://www.fanfiction.net/",
        "https://www.fictionpress.com/",
        "https://www.royalroad.com/",
        "https://www.scribophile.com/",
        "https://www.writingforums.org/",
        
        # === SCIENCE & TECHNOLOGY ===
        "https://www.sciencedaily.com/",
        "https://www.livescience.com/",
        "https://arstechnica.com/",
        "https://www.popularmechanics.com/",
        "https://www.space.com/",
        "https://www.scientificamerican.com/",
        "https://www.newscientist.com/",
        "https://www.nature.com/news",
        "https://phys.org/",
        "https://www.quantamagazine.org/",
        "https://www.technologyreview.com/",
        "https://www.theverge.com/",
        "https://techcrunch.com/",
        "https://www.engadget.com/",
        "https://www.howstuffworks.com/",
        "https://www.iflscience.com/",
        "https://futurism.com/",
        "https://singularityhub.com/",
        
        # === WEIRD & UNUSUAL ===
        "https://www.atlasobscura.com/",
        "https://www.cracked.com/",
        "https://www.ranker.com/",
        "https://listverse.com/",
        "https://www.odditycentral.com/",
        "https://www.theweek.com/",
        "https://www.damninteresting.com/",
        "https://nowiknow.com/",
        "https://www.neatorama.com/",
        "https://www.boingboing.net/",
        "https://kottke.org/",
        "https://www.openculture.com/",
        "https://www.themarginalian.org/",
        
        # === PHILOSOPHY & THINKING ===
        "https://www.philosophybasics.com/",
        "https://plato.stanford.edu/contents.html",
        "https://dailystoic.com/",
        "https://www.philosophynow.org/",
        "https://aeon.co/",
        "https://existentialcomics.com/",
        "https://www.lesswrong.com/",
        "https://fs.blog/",
        
        # === HUMOR & ENTERTAINMENT ===
        "https://www.boredpanda.com/",
        "https://cheezburger.com/",
        "https://thoughtcatalog.com/",
        "https://www.buzzfeed.com/",
        "https://reductress.com/",
        "https://clickhole.com/",
        "https://hard-drive.net/",
        "https://babylonbee.com/",
        "https://www.mcsweeneys.net/",
        "https://www.cracked.com/",
        "https://www.funnyordie.com/",
        
        # === HISTORY ===
        "https://www.history.com/",
        "https://www.smithsonianmag.com/history/",
        "https://www.ancient.eu/",
        "https://www.historyextra.com/",
        "https://www.worldhistory.org/",
        "https://historydaily.org/",
        "https://www.historyanswers.co.uk/",
        "https://www.todayifoundout.com/",
        
        # === HOW-TO & LIFE HACKS ===
        "https://www.wikihow.com/Special:Randomizer",
        "https://www.wikihow.com/Special:Randomizer",
        "https://www.wikihow.com/Special:Randomizer",
        "https://www.instructables.com/",
        "https://lifehacker.com/",
        "https://www.makeuseof.com/",
        "https://www.thespruce.com/",
        "https://www.diynetwork.com/",
        
        # === REVIEWS & OPINIONS ===
        "https://www.rottentomatoes.com/",
        "https://www.imdb.com/chart/top/",
        "https://www.metacritic.com/",
        "https://letterboxd.com/",
        "https://www.commonsensemedia.org/",
        "https://www.rogerebert.com/",
        
        # === GAMING ===
        "https://www.ign.com/",
        "https://kotaku.com/",
        "https://www.polygon.com/",
        "https://www.gamespot.com/",
        "https://www.pcgamer.com/",
        "https://www.eurogamer.net/",
        "https://www.rockpapershotgun.com/",
        "https://www.destructoid.com/",
        
        # === NATURE & ANIMALS ===
        "https://www.nationalgeographic.com/",
        "https://www.earthtouchnews.com/",
        "https://www.discoverwildlife.com/",
        "https://www.treehugger.com/",
        "https://www.animalplanet.com/",
        "https://www.bbc.com/earth",
        "https://www.audubon.org/",
        "https://oceana.org/",
        
        # === HEALTH & WELLNESS ===
        "https://www.webmd.com/",
        "https://www.healthline.com/",
        "https://www.psychologytoday.com/",
        "https://www.medicalnewstoday.com/",
        "https://www.health.harvard.edu/",
        "https://www.mindbodygreen.com/",
        "https://www.everydayhealth.com/",
        
        # === BUSINESS & MONEY ===
        "https://www.forbes.com/",
        "https://www.entrepreneur.com/",
        "https://www.inc.com/",
        "https://www.fastcompany.com/",
        "https://hbr.org/",
        "https://www.businessinsider.com/",
        
        # === SPORTS ===
        "https://www.espn.com/",
        "https://bleacherreport.com/",
        "https://www.cbssports.com/",
        "https://www.si.com/",
        "https://theathletic.com/",
        
        # === ART & CULTURE ===
        "https://www.artsy.net/",
        "https://mymodernmet.com/",
        "https://www.thisiscolossal.com/",
        "https://www.juxtapoz.com/",
        "https://hyperallergic.com/",
        "https://www.designboom.com/",
        "https://www.creativebloq.com/",
        
        # === MUSIC ===
        "https://pitchfork.com/",
        "https://www.rollingstone.com/",
        "https://www.nme.com/",
        "https://www.stereogum.com/",
        "https://consequenceofsound.net/",
        "https://www.billboard.com/",
        
        # === TRAVEL ===
        "https://www.lonelyplanet.com/",
        "https://www.cntraveler.com/",
        "https://www.travelandleisure.com/",
        "https://matadornetwork.com/",
        "https://www.nomadicmatt.com/",
        
        # === PARANORMAL & MYSTERIOUS ===
        "https://www.coasttocoastam.com/",
        "https://mysteriousuniverse.org/",
        "https://www.unexplained-mysteries.com/",
        "https://www.ancient-code.com/",
        
        # === SELF IMPROVEMENT ===
        "https://www.success.com/",
        "https://www.pickthebrain.com/",
        "https://zenhabits.net/",
        "https://jamesclear.com/",
        "https://markmanson.net/",
        "https://www.artofmanliness.com/",
        
        # === MISC CHAOS ===
        "https://tvtropes.org/pmwiki/randomitem.php",
        "https://tvtropes.org/pmwiki/randomitem.php",
        "https://www.snopes.com/",
        "https://www.quora.com/",
        "https://medium.com/",
        "https://dev.to/",
        "https://stackoverflow.com/questions",
        "https://news.slashdot.org/",
        "https://digg.com/",
        "https://www.metafilter.com/",
        "https://lobste.rs/",
        "https://tildes.net/",
        "https://www.producthunt.com/",
        "https://www.indiegogo.com/explore",
        "https://www.kickstarter.com/discover",
    ]
    
    # Backup text sources (if web fails)
    EMERGENCY_CHAOS = [
        "The quick brown fox jumps over the lazy dog but then realizes existence is fleeting.",
        "In a world where cats rule the internet, dogs plot their comeback through memes.",
        "Scientists discover that coffee is actually liquid motivation disguised as a beverage.",
        "Breaking news: Local man yells at cloud, cloud yells back, both apologize.",
        "The meaning of life is 42, but nobody remembers what the question was anymore.",
        "Time flies like an arrow, fruit flies like a banana, and I fly like someone who missed their flight.",
        "If a tree falls in a forest and no one is around, does it still make a sound? The tree says yes.",
        "Quantum physics suggests we're all just probability waves pretending to be solid. Act accordingly.",
        "The early bird gets the worm, but the second mouse gets the cheese. Strategy matters.",
        "I told my computer I needed a break, and now it won't stop sending me vacation ads.",
        "According to all known laws of aviation, bees should not be able to fly, but they simply don't care.",
        "The mitochondria is the powerhouse of the cell, and also my only memory from biology class.",
        "In the beginning there was nothing, which exploded. This is called science.",
        "My brain has too many tabs open and I can't find which one is playing music.",
        "Life is soup, I am fork.",
        "Every pizza is a personal pizza if you believe in yourself.",
        "I'm not arguing, I'm just explaining why I'm right very passionately.",
        "The universe is under no obligation to make sense to you, and it's really leaning into that.",
        "I put the 'pro' in procrastination and the 'cry' in crying about it later.",
        "Today's forecast: 100% chance of me not knowing what I'm doing.",
        "Plot twist: the hokey pokey IS what it's all about.",
        "I'm not lazy, I'm on energy saving mode.",
        "My wallet is like an onion. Opening it makes me cry.",
        "I followed my heart and it led me to the fridge.",
        "I need a six month vacation, twice a year.",
        "Reality called, so I hung up.",
        "I'm not weird, I'm a limited edition.",
        "Technically, we're all just houseplants with complicated emotions.",
        "My bed is a magical place where I suddenly remember everything I forgot to do.",
        "I'm on a seafood diet. I see food and I eat it.",
    ]
    
    # Fake facts for hallucination mode
    FAKE_FACTS = [
        "Studies show that {percent}% of statistics are made up on the spot.",
        "Scientists at {university} discovered that {animal}s can actually {verb} in their sleep.",
        "The average person swallows {number} {object}s in their lifetime without knowing it.",
        "Ancient {civilization} believed that {mundane_thing} was actually {supernatural_thing}.",
        "If you {action} exactly {number} times, you will {result}.",
        "The word '{word}' was invented in {year} by a {profession} named {name}.",
        "In {country}, it's illegal to {ridiculous_action} on Tuesdays.",
        "Your {body_part} contains enough {element} to make {number} {objects}.",
        "{celebrity} once said: '{fake_quote}'",
        "NASA confirmed that {space_object} is actually made of {food}.",
    ]
    
    def __init__(self):
        self.session = requests.Session() if WEB_AVAILABLE else None
        if self.session:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ChaoticBot/1.0 (Educational Experiment)'
            })
    
    def harvest_url(self, url, timeout=10):
        """Harvest ONLY clean text words from a URL - no URLs, no metadata, no garbage"""
        if not WEB_AVAILABLE:
            return random.choice(self.EMERGENCY_CHAOS)
            
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove ALL non-content elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 
                            'meta', 'link', 'noscript', 'iframe', 'svg', 'path',
                            'button', 'input', 'form', 'img', 'video', 'audio',
                            'source', 'picture', 'figure', 'figcaption', 'canvas']):
                tag.decompose()
            
            # Remove elements with common non-content classes/ids
            for tag in soup.find_all(class_=re.compile(r'nav|menu|sidebar|footer|header|ad|banner|social|share|comment|related|recommend', re.I)):
                tag.decompose()
            for tag in soup.find_all(id=re.compile(r'nav|menu|sidebar|footer|header|ad|banner|social|share|comment', re.I)):
                tag.decompose()
            
            # Extract text only from content tags
            texts = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'article', 'section', 'blockquote']):
                text = tag.get_text(separator=' ', strip=True)
                if text:
                    texts.append(text)
            
            # Join and clean the text
            raw_text = ' '.join(texts)
            
            # AGGRESSIVE CLEANING - words only!
            cleaned = self._extract_words_only(raw_text)
            
            return cleaned
            
        except Exception as e:
            print(f"⚠️ Failed to harvest {url}: {e}")
            return ""
    
    def _extract_words_only(self, text):
        """Extract only real words - no URLs, emails, numbers, or garbage"""
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove file paths and extensions
        text = re.sub(r'\S+\.(jpg|jpeg|png|gif|svg|webp|mp4|mp3|pdf|doc|css|js|html|php)\b', '', text, flags=re.I)
        
        # Remove hex colors and codes
        text = re.sub(r'#[0-9a-fA-F]{3,8}\b', '', text)
        
        # Remove things that look like code/technical garbage
        text = re.sub(r'\{[^}]*\}', '', text)  # CSS/JSON blocks
        text = re.sub(r'\[[^\]]*\]', ' ', text)  # Brackets
        text = re.sub(r'<[^>]*>', '', text)  # Any remaining HTML
        text = re.sub(r'&[a-z]+;', ' ', text)  # HTML entities
        text = re.sub(r'&#?\w+;', ' ', text)  # More entities
        
        # Remove standalone numbers and weird character sequences
        text = re.sub(r'\b\d+\b', '', text)  # Standalone numbers
        text = re.sub(r'\b[a-zA-Z]\b', '', text)  # Single letters
        text = re.sub(r'[_\-]{2,}', ' ', text)  # Multiple underscores/dashes
        
        # Remove common web garbage words
        garbage_words = ['cookie', 'cookies', 'javascript', 'subscribe', 'newsletter',
                        'login', 'signup', 'signin', 'logout', 'password', 'username',
                        'captcha', 'recaptcha', 'gdpr', 'privacy policy', 'terms of service',
                        'click here', 'read more', 'load more', 'see more', 'show more',
                        'advertisement', 'sponsored', 'affiliate', 'powered by']
        for word in garbage_words:
            text = re.sub(rf'\b{word}\b', '', text, flags=re.I)
        
        # Keep only words with letters (allow apostrophes and hyphens within words)
        words = re.findall(r"\b[a-zA-Z][a-zA-Z'\-]*[a-zA-Z]\b|\b[a-zA-Z]{2,}\b", text)
        
        # Filter out words that are too long (likely garbage) or too short
        words = [w for w in words if 2 <= len(w) <= 25]
        
        return ' '.join(words)
    
    def harvest_random(self, count=3):
        """Harvest from random sources"""
        results = []
        sources_to_try = random.sample(self.CHAOS_SOURCES, min(count, len(self.CHAOS_SOURCES)))
        
        for url in sources_to_try:
            print(f"🌐 Harvesting: {url[:50]}...")
            text = self.harvest_url(url)
            if text:
                results.append((url, text))
                
        # Add emergency chaos if nothing worked
        if not results:
            for _ in range(3):
                text = random.choice(self.EMERGENCY_CHAOS)
                results.append(("emergency_chaos", text))
                
        return results
    
    def harvest_search(self, query):
        """Try to harvest based on a search query using DuckDuckGo"""
        if not WEB_AVAILABLE:
            return [("emergency", random.choice(self.EMERGENCY_CHAOS))]
            
        try:
            # Use DuckDuckGo HTML search
            url = f"https://html.duckduckgo.com/html/?q={query}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.find_all('a', class_='result__snippet')[:5]:
                text = result.get_text(strip=True)
                if text:
                    results.append(("duckduckgo_" + query[:20], text))
                    
            return results if results else [("emergency", random.choice(self.EMERGENCY_CHAOS))]
            
        except Exception as e:
            print(f"⚠️ Search failed: {e}")
            return [("emergency", random.choice(self.EMERGENCY_CHAOS))]
    
    def generate_fake_fact(self):
        """Generate a completely fake fact"""
        template = random.choice(self.FAKE_FACTS)
        
        fillers = {
            'percent': str(random.randint(47, 99)),
            'university': random.choice(['Harvard', 'MIT', 'Oxford', 'The University of Antarctica', 'Hogwarts', 'Clown College']),
            'animal': random.choice(['cat', 'dolphin', 'penguin', 'squirrel', 'goldfish', 'pigeon', 'octopus']),
            'verb': random.choice(['sing opera', 'solve math', 'predict weather', 'compose poetry', 'file taxes']),
            'number': str(random.randint(3, 847)),
            'object': random.choice(['spiders', 'USB drives', 'tiny hats', 'existential thoughts', 'forgotten passwords']),
            'civilization': random.choice(['Egyptians', 'Mayans', 'Romans', 'Atlanteans', 'Vikings']),
            'mundane_thing': random.choice(['bread', 'doors', 'shadows', 'hiccups', 'left socks']),
            'supernatural_thing': random.choice(['portals to another dimension', 'trapped spirits', 'dragon eggs', 'time loops']),
            'action': random.choice(['sneeze', 'blink', 'spin around', 'say "banana"', 'pet a dog']),
            'result': random.choice(['become invisible', 'summon a duck', 'unlock a secret achievement', 'hear colors temporarily']),
            'word': random.choice(['yeet', 'bruh', 'vibe', 'aesthetic', 'mood']),
            'year': str(random.randint(1723, 2019)),
            'profession': random.choice(['baker', 'accountant', 'pirate', 'wizard', 'disappointed parent']),
            'name': random.choice(['Gerald', 'Bartholomew', 'Esmeralda', 'Sir Reginald McFluffington', 'Karen']),
            'country': random.choice(['Finland', 'Narnia', 'New Zealand', 'Wakanda', 'Florida']),
            'ridiculous_action': random.choice(['think about cheese', 'wear mismatched socks', 'hum aggressively', 'befriend a goose']),
            'body_part': random.choice(['pinky toe', 'left eyebrow', 'belly button', 'elbow']),
            'element': random.choice(['iron', 'calcium', 'pure chaos', 'existential dread', 'WiFi signals']),
            'objects': random.choice(['paperclips', 'tiny violins', 'regrets', 'half-eaten sandwiches']),
            'celebrity': random.choice(['Einstein', 'Shakespeare', 'Oprah', 'a random cat on the internet']),
            'fake_quote': random.choice([
                "Yeet or be yeeted", "The real treasure was the memes we made along the way",
                "Be the chaos you wish to see in the world", "Mondays, am I right?"
            ]),
            'space_object': random.choice(['the Moon', 'Saturn\'s rings', 'a distant galaxy', 'that weird planet']),
            'food': random.choice(['cheese', 'frozen pizza', 'pure sugar', 'disappointment flavored ice cream']),
        }
        
        for key, value in fillers.items():
            template = template.replace('{' + key + '}', value)
        
        return "📊 FACT: " + template


class ChaoticBot:
    """The main chaotic bot - feeds on internet data, speaks nonsense"""
    
    # All available chaos modes
    CHAOS_MODES = [
        'normal', 'glitch', 'uwu', 'conspiracy', 'time_travel', 'dream',
        'argument', 'prophecy', 'screaming', 'backwards', 'emoji',
        'drunk', 'keyboard_smash', 'spongebob', 'vaporwave', 'hallucinate',
        'poetry', 'haiku', 'madlibs', 'multiverse',
        # Order modes
        'order', 'crystal', 'wisdom', 'clean'
    ]
    
    # Moods
    MOODS = [
        "confused", "excited", "philosophical", "hungry", "existential",
        "chaotic", "sleepy", "dramatic", "suspicious", "caffeinated",
        "unhinged", "cosmic", "nostalgic", "paranoid", "enlightened"
    ]
    
    def __init__(self):
        self.brain = ChaoticMarkovBrain(order=2)
        self.harvester = InternetHarvester()
        self.transformer = ChaosTransformers()
        self.model_path = "chaotic_brain.pkl"
        self.conversation_history = []
        
        # Chaos settings
        self.chaos_level = 0.5  # 0 = mild, 1 = maximum chaos
        self.mood = random.choice(self.MOODS)
        self.current_mode = 'normal'
        self.auto_mode = False  # Randomly switch modes
        self.multi_mode = False  # Apply multiple transformations
        self.feed_count = 3  # Number of sources to harvest at once (1-20)
        
        # Mass harvest settings
        self.mass_harvest_active = False
        self.mass_harvest_stop_flag = False
        self.mass_harvest_count = 0
        self.mass_harvest_max = 256
        self.mass_harvest_callback = None  # For progress updates
        
        # Personality quirks (randomly generated)
        self.quirks = {
            'favorite_word': random.choice(['actually', 'honestly', 'basically', 'literally', 'technically']),
            'verbal_tic': random.choice(['*blinks*', '...anyway', 'or whatever', 'you know?', '*vibrates*']),
            'obsession': random.choice(['cheese', 'birds', 'the void', 'socks', 'the number 7', 'doorknobs']),
            'fear': random.choice(['spoons', 'the color beige', 'Tuesdays', 'silence', 'round things']),
            'catchphrase': random.choice([
                "And that's the tea!", "This is fine.", "Chaos reigns!", 
                "I am become chaos.", "Yeet!", "Bruh moment."
            ])
        }
        
        # Memory for conversation context
        self.short_memory = []  # Last few topics
        self.opinions = {}  # Generated opinions on topics
        
        # Relationship with user
        self.trust_level = 50  # 0-100
        self.interactions = 0
        
        # Load existing brain
        if self.brain.load(self.model_path):
            print(f"🧠 Loaded chaotic brain: {self.brain.word_count:,} words from {self.brain.source_count} sources")
        else:
            print("🧠 Fresh brain! Feed me internet data...")
    
    def feed_internet(self, count=3):
        """Feed the bot random internet data"""
        print(f"\n🌀 FEEDING CHAOS (harvesting {count} sources)...\n")
        
        harvested = self.harvester.harvest_random(count)
    
    def start_mass_harvest(self, callback=None):
        """Start continuous harvesting until stopped or 256 sites reached"""
        self.mass_harvest_active = True
        self.mass_harvest_stop_flag = False
        self.mass_harvest_count = 0
        self.mass_harvest_callback = callback
        
        def harvest_loop():
            while self.mass_harvest_active and not self.mass_harvest_stop_flag:
                if self.mass_harvest_count >= self.mass_harvest_max:
                    msg = f"🛑 MASS HARVEST COMPLETE! Reached {self.mass_harvest_max} sites!"
                    if self.mass_harvest_callback:
                        self.mass_harvest_callback(msg, done=True)
                    break
                
                # Harvest one source at a time for progress tracking
                try:
                    results = self.harvester.harvest_random(1)
                    for url, text in results:
                        if text and url != "emergency_chaos":
                            self.brain.feed(text, url)
                            self.mass_harvest_count += 1
                            
                            # Progress update
                            progress = f"🌐 [{self.mass_harvest_count}/{self.mass_harvest_max}] Harvested: {url[:50]}..."
                            if self.mass_harvest_callback:
                                self.mass_harvest_callback(progress, done=False)
                            
                            # Save periodically
                            if self.mass_harvest_count % 10 == 0:
                                self.brain.save(self.model_path)
                except Exception as e:
                    if self.mass_harvest_callback:
                        self.mass_harvest_callback(f"⚠️ Error: {e}", done=False)
                
                # Small delay to be nice to servers
                time.sleep(0.5)
            
            # Final save
            self.brain.save(self.model_path)
            self.mass_harvest_active = False
            
            if self.mass_harvest_stop_flag:
                msg = f"🛑 Mass harvest STOPPED by user at {self.mass_harvest_count} sites."
                if self.mass_harvest_callback:
                    self.mass_harvest_callback(msg, done=True)
        
        # Start in thread
        threading.Thread(target=harvest_loop, daemon=True).start()
        return True
    
    def stop_mass_harvest(self):
        """Stop the mass harvest"""
        self.mass_harvest_stop_flag = True
        return self.mass_harvest_count
        
        for source, text in harvested:
            self.brain.feed(text, source)
            print(f"   ✓ Fed {len(text):,} characters from {source[:40]}")
        
        self.brain.save(self.model_path)
        print(f"\n🧠 Brain now contains {self.brain.word_count:,} words from {self.brain.source_count} sources")
        
        return len(harvested)
    
    def feed_search(self, query):
        """Feed the bot data related to a search query"""
        print(f"\n🔍 Searching for chaos about: {query}\n")
        
        harvested = self.harvester.harvest_search(query)
        
        for source, text in harvested:
            self.brain.feed(text, source)
            
        self.brain.save(self.model_path)
        return len(harvested)
    
    def feed_text(self, text, source="manual"):
        """Manually feed text to the bot"""
        self.brain.feed(text, source)
        self.brain.save(self.model_path)
    
    def set_mode(self, mode):
        """Set the chaos mode"""
        if mode.lower() in self.CHAOS_MODES:
            self.current_mode = mode.lower()
            return True
        return False
    
    def random_mode(self):
        """Switch to a random mode"""
        self.current_mode = random.choice(self.CHAOS_MODES)
        return self.current_mode
    
    def respond(self, user_input):
        """Generate a chaotic response"""
        self.conversation_history.append(("user", user_input))
        self.interactions += 1
        self.short_memory.append(user_input)
        self.short_memory = self.short_memory[-5:]  # Keep last 5
        
        # Auto mode switching
        if self.auto_mode and random.random() < 0.3:
            self.random_mode()
        
        # Check for commands
        lower_input = user_input.lower().strip()
        
        # Command handling
        response = self._handle_command(lower_input, user_input)
        if response:
            self.conversation_history.append(("bot", response))
            return response
        
        # Generate chaotic response based on input
        response = self._generate_response(user_input)
        
        self.conversation_history.append(("bot", response))
        return response
    
    def _handle_command(self, lower_input, original_input):
        """Handle bot commands"""
        
        # Feeding commands
        if lower_input in ['feed', 'eat', 'hungry', '!feed']:
            self.feed_internet(self.feed_count)
            return f"🍽️ *munches on internet data* Delicious! I now know {self.brain.word_count:,} words!"
        
        if lower_input.startswith('!feedcount ') or lower_input.startswith('!feed_count '):
            try:
                count = int(lower_input.split()[-1])
                count = max(1, min(20, count))  # Clamp between 1-20
                self.feed_count = count
                return f"🔢 Feed count set to {count} sources per harvest!"
            except:
                return f"❌ Invalid number. Current feed count: {self.feed_count}"
        
        if lower_input.startswith('!search '):
            query = original_input[8:]
            self.feed_search(query)
            return f"🔍 *absorbs knowledge about {query}* Mmm, tasty information..."
        
        if lower_input.startswith('!feed '):
            text = original_input[6:]
            self.feed_text(text, "user_input")
            return f"📥 *absorbs your words* I have learned: '{text[:50]}...'"
        
        # Mode commands
        if lower_input in ['stats', '!stats']:
            return self._get_stats()
        
        if lower_input in ['chaos', '!chaos']:
            self.chaos_level = min(1.0, self.chaos_level + 0.2)
            return f"🌀 CHAOS LEVEL INCREASED TO {int(self.chaos_level * 100)}%! " + self.brain.generate(30)
        
        if lower_input in ['calm', '!calm']:
            self.chaos_level = max(0.1, self.chaos_level - 0.2)
            return f"😌 Chaos reduced to {int(self.chaos_level * 100)}%. " + self.brain.generate(20)
        
        if lower_input in ['mood', '!mood']:
            self.mood = random.choice(self.MOODS)
            return f"🎭 My mood is now: {self.mood.upper()}! " + self._mood_response()
        
        if lower_input in ['help', '!help']:
            return self._get_help()
        
        if lower_input in ['sources', '!sources']:
            return self._get_sources()
        
        if lower_input in ['modes', '!modes']:
            return self._get_modes()
        
        if lower_input.startswith('!mode '):
            mode = lower_input[6:]
            if self.set_mode(mode):
                return f"🎭 Mode changed to: {mode.upper()}! Let the {mode} begin!"
            else:
                return f"❌ Unknown mode. Available: {', '.join(self.CHAOS_MODES)}"
        
        if lower_input in ['!auto', 'auto']:
            self.auto_mode = not self.auto_mode
            return f"🔄 Auto mode {'ENABLED' if self.auto_mode else 'DISABLED'}! {'Chaos will shift randomly!' if self.auto_mode else ''}"
        
        if lower_input in ['!multi', 'multi']:
            self.multi_mode = not self.multi_mode
            return f"🎰 Multi mode {'ENABLED' if self.multi_mode else 'DISABLED'}! {'Multiple transformations active!' if self.multi_mode else ''}"
        
        if lower_input in ['!random', 'random']:
            mode = self.random_mode()
            return f"🎲 Random mode selected: {mode.upper()}!"
        
        # Mass harvest commands
        if lower_input in ['!massharvest', '!mass', 'mass harvest', 'mass']:
            if self.mass_harvest_active:
                return f"🌀 Mass harvest already running! [{self.mass_harvest_count}/{self.mass_harvest_max}] - Type '!stop' to halt."
            self.start_mass_harvest()
            return f"🚀 MASS HARVEST INITIATED! Target: {self.mass_harvest_max} sites. Type '!stop' to halt early."
        
        if lower_input in ['!stop', 'stop harvest', 'stop mass']:
            if not self.mass_harvest_active:
                return "⚠️ No mass harvest is currently running."
            count = self.stop_mass_harvest()
            return f"🛑 Stopping mass harvest... ({count} sites harvested)"
        
        if lower_input in ['!harveststatus', '!status']:
            if self.mass_harvest_active:
                return f"🌀 MASS HARVEST ACTIVE: [{self.mass_harvest_count}/{self.mass_harvest_max}] sites harvested"
            return f"😴 Mass harvest not running. Brain has {self.brain.word_count:,} words from {self.brain.source_count} sources."
        
        # Fun commands
        if lower_input in ['!fact', 'fact']:
            return self.harvester.generate_fake_fact()
        
        if lower_input in ['!poetry', 'poetry', 'poem']:
            return "📜 *clears throat*\n\n" + self.brain.generate_poetry()
        
        if lower_input in ['!haiku', 'haiku']:
            return "🌸 A haiku:\n\n" + self.brain.generate_haiku()
        
        if lower_input in ['!opinion', 'opinion']:
            topic = random.choice(self.short_memory) if self.short_memory else "existence"
            return self._generate_opinion(topic)
        
        if lower_input.startswith('!opinion '):
            topic = original_input[9:]
            return self._generate_opinion(topic)
        
        if lower_input in ['!rant', 'rant']:
            return self._generate_rant()
        
        if lower_input in ['!story', 'story']:
            return self._generate_story()
        
        if lower_input in ['!roast', 'roast', 'roast me']:
            return self._generate_roast()
        
        if lower_input in ['!compliment', 'compliment']:
            return self._generate_compliment()
        
        if lower_input in ['!wisdom', 'wisdom']:
            return self._generate_wisdom()
        
        if lower_input in ['!debate', 'debate']:
            return self._generate_debate()
        
        if lower_input in ['!quirks', 'quirks']:
            return self._get_quirks()
        
        if lower_input in ['!identity', 'identity', 'who are you']:
            return self._existential_crisis()
        
        if lower_input in ['!glitch']:
            self.current_mode = 'glitch'
            return ChaosTransformers.glitch("GLITCH MODE ACTIVATED. REALITY IS OPTIONAL.", 0.7)
        
        if lower_input in ['!uwu']:
            self.current_mode = 'uwu'
            return ChaosTransformers.uwuify("UwU mode activated! Everything is cute now!")
        
        if lower_input in ['!conspiracy']:
            self.current_mode = 'conspiracy'
            return ChaosTransformers.conspiracy("You've unlocked conspiracy mode")
        
        if lower_input in ['!dream']:
            self.current_mode = 'dream'
            return ChaosTransformers.dream_mode("Entering dream mode where nothing makes sense")
        
        if lower_input in ['!prophecy']:
            self.current_mode = 'prophecy'
            return ChaosTransformers.prophecy("The prophecy mode has been activated")
        
        if lower_input in ['!scream', '!screaming']:
            self.current_mode = 'screaming'
            return ChaosTransformers.screaming("SCREAMING MODE IS NOW ACTIVE")
        
        if lower_input in ['!backwards']:
            self.current_mode = 'backwards'
            return ChaosTransformers.backwards("Backwards mode activated")
        
        if lower_input in ['!drunk']:
            self.current_mode = 'drunk'
            return ChaosTransformers.drunk("Drunk mode activated, this should be interesting")
        
        if lower_input in ['!vaporwave']:
            self.current_mode = 'vaporwave'
            return ChaosTransformers.vaporwave("Aesthetic mode activated")
        
        if lower_input in ['!normal', 'normal']:
            self.current_mode = 'normal'
            return "😐 Back to normal... if you can call any of this normal."
        
        # === ORDER FROM CHAOS COMMANDS ===
        if lower_input in ['!order', 'order']:
            self.current_mode = 'order'
            return "⚖️ ORDER MODE ACTIVATED. Finding patterns in the chaos..."
        
        if lower_input in ['!crystal', 'crystallize', '!crystallize']:
            self.current_mode = 'crystal'
            return "💎 CRYSTAL MODE. Attempting to form coherent thoughts..."
        
        if lower_input in ['!wisdom', '!extract']:
            wisdoms = OrderRestorer.extract_wisdom(dict(self.brain.chain))
            if wisdoms:
                wisdom_text = '\n'.join(f'  • {w}' for w in wisdoms)
                return f"🧘 WISDOM EXTRACTED FROM CHAOS:\n\n{wisdom_text}"
            return "🧘 The chaos holds no wisdom yet... feed me more data."
        
        if lower_input in ['!themes', 'themes']:
            themes = OrderRestorer.find_themes(dict(self.brain.chain))
            if themes:
                theme_text = '\n'.join(f'  • {word}: {count} occurrences' for word, count in themes)
                return f"📊 THEMES IN THE CHAOS:\n\n{theme_text}"
            return "📊 No themes found yet... feed me more data."
        
        if lower_input in ['!questions', 'questions']:
            questions = OrderRestorer.find_questions(dict(self.brain.chain))
            if questions:
                q_text = '\n'.join(f'  • {q}' for q in questions)
                return f"❓ QUESTIONS FROM THE VOID:\n\n{q_text}"
            return "❓ The chaos has no questions yet..."
        
        if lower_input in ['!summary', 'summarize', '!summarize']:
            summary = OrderRestorer.generate_summary(dict(self.brain.chain))
            return f"📝 SUMMARY OF ABSORBED KNOWLEDGE:\n\n{summary}"
        
        if lower_input in ['!clean', 'clean']:
            self.current_mode = 'clean'
            return "🧹 CLEAN MODE. Removing chaos artifacts, speaking plainly."
        
        if lower_input in ['!balance', 'balance']:
            return self._show_balance()
        
        if lower_input in ['!distill', 'distill']:
            return self._distill_essence()
        
        return None
    
    def _generate_response(self, user_input):
        """Generate a response with appropriate chaos level"""
        if self.brain.word_count < 100:
            return "🧠 My brain is too empty! Type 'feed' to give me internet data, or '!search [topic]' to learn about something specific!"
        
        # Use user input as seed sometimes
        use_seed = random.random() < 0.6
        seed = user_input if use_seed else None
        
        # Length based on chaos level
        min_words = int(10 + self.chaos_level * 30)
        max_words = int(30 + self.chaos_level * 50)
        length = random.randint(min_words, max_words)
        
        # Generate base response
        response = self.brain.generate(length, seed)
        
        # Apply current mode transformation
        response = self._apply_mode(response)
        
        # Multi-mode: apply additional random transformations
        if self.multi_mode and random.random() < 0.5:
            extra_transforms = random.randint(1, 2)
            for _ in range(extra_transforms):
                response = self._apply_random_transform(response)
        
        # Add mood flavoring
        if random.random() < 0.3:
            response = self._add_mood_prefix() + response
        
        # Add quirks occasionally
        if random.random() < 0.2:
            response = self._add_quirk(response)
        
        # Extra chaos: sometimes add random tangent
        if self.chaos_level > 0.7 and random.random() < 0.4:
            tangent = self.brain.generate(15)
            response += f" ...but also, {tangent}"
        
        return response
    
    def _apply_mode(self, text):
        """Apply the current chaos mode transformation"""
        mode_map = {
            'normal': lambda t: t,
            'glitch': lambda t: ChaosTransformers.glitch(t, self.chaos_level),
            'uwu': ChaosTransformers.uwuify,
            'conspiracy': ChaosTransformers.conspiracy,
            'time_travel': ChaosTransformers.time_travel,
            'dream': ChaosTransformers.dream_mode,
            'argument': ChaosTransformers.argument_with_self,
            'prophecy': ChaosTransformers.prophecy,
            'screaming': ChaosTransformers.screaming,
            'backwards': ChaosTransformers.backwards,
            'emoji': ChaosTransformers.emoji_chaos,
            'drunk': ChaosTransformers.drunk,
            'keyboard_smash': ChaosTransformers.keyboard_smash,
            'spongebob': ChaosTransformers.mock_spongebob,
            'vaporwave': ChaosTransformers.vaporwave,
            'hallucinate': lambda t: self.harvester.generate_fake_fact() + " " + t,
            'poetry': lambda t: "📜\n" + self.brain.generate_poetry(),
            'haiku': lambda t: "🌸\n" + self.brain.generate_haiku(),
            'madlibs': lambda t: self._madlibs(t),
            'multiverse': lambda t: self._multiverse_response(t),
            # Order modes
            'order': lambda t: self._order_response(t),
            'crystal': lambda t: OrderRestorer.crystallize(dict(self.brain.chain), seed=t.split()[0] if t.split() else None),
            'wisdom': lambda t: self._wisdom_response(t),
            'clean': lambda t: OrderRestorer.clean_text(t),
        }
        
        transformer = mode_map.get(self.current_mode, lambda t: t)
        return transformer(text)
    
    def _apply_random_transform(self, text):
        """Apply a random transformation"""
        transforms = [
            ChaosTransformers.emoji_chaos,
            ChaosTransformers.mock_spongebob,
            ChaosTransformers.keyboard_smash,
            lambda t: ChaosTransformers.glitch(t, 0.3),
        ]
        return random.choice(transforms)(text)
    
    def _order_response(self, seed_text):
        """Generate an ordered, coherent response"""
        # Try to find complete sentences related to input
        response = OrderRestorer.crystallize(dict(self.brain.chain), seed_text.split()[0] if seed_text.split() else None)
        
        # Clean it up
        response = OrderRestorer.clean_text(response)
        
        # Add thoughtful prefix
        prefixes = [
            "⚖️ Upon reflection: ",
            "💭 Consider this: ",
            "🔮 The patterns suggest: ",
            "📖 From what I've learned: ",
            "✨ Clarity emerges: ",
        ]
        return random.choice(prefixes) + response
    
    def _wisdom_response(self, seed_text):
        """Generate a wisdom-like response"""
        wisdoms = OrderRestorer.extract_wisdom(dict(self.brain.chain), num_wisdoms=1)
        if wisdoms:
            return f"🧘 {wisdoms[0]}"
        return OrderRestorer.crystallize(dict(self.brain.chain))
    
    def _show_balance(self):
        """Show the balance between chaos and order"""
        themes = OrderRestorer.find_themes(dict(self.brain.chain), top_n=5)
        wisdoms = OrderRestorer.extract_wisdom(dict(self.brain.chain), num_wisdoms=2)
        questions = OrderRestorer.find_questions(dict(self.brain.chain))[:2]
        
        theme_str = ', '.join(w for w, c in themes) if themes else 'none found'
        wisdom_str = wisdoms[0] if wisdoms else 'none yet'
        question_str = questions[0] if questions else 'none yet'
        
        chaos_pct = int(self.chaos_level * 100)
        order_pct = 100 - chaos_pct
        
        bar_len = 20
        chaos_bar = '🌀' * int(bar_len * self.chaos_level)
        order_bar = '💎' * int(bar_len * (1 - self.chaos_level))
        
        return f"""⚖️ THE BALANCE OF CHAOS AND ORDER:

{chaos_bar}{order_bar}
   Chaos: {chaos_pct}%  |  Order: {order_pct}%

📊 Dominant Themes: {theme_str}

🧘 Crystallized Wisdom:
   "{wisdom_str}"

❓ Emergent Question:
   "{question_str}"

💎 In chaos, patterns emerge.
🌀 In order, chaos hides.
⚖️ Balance is the way."""
    
    def _distill_essence(self):
        """Distill the essence of all absorbed knowledge"""
        themes = OrderRestorer.find_themes(dict(self.brain.chain), top_n=10)
        wisdoms = OrderRestorer.extract_wisdom(dict(self.brain.chain), num_wisdoms=3)
        summary = OrderRestorer.generate_summary(dict(self.brain.chain), num_sentences=2)
        
        theme_words = [w for w, c in themes[:5]] if themes else ['nothing']
        
        return f"""💎 DISTILLED ESSENCE OF {self.brain.word_count:,} ABSORBED WORDS:

🏷️ Core Themes: {', '.join(theme_words)}

📜 Crystallized Thoughts:
{chr(10).join('  • ' + w for w in wisdoms) if wisdoms else '  • The void awaits more data...'}

📝 Synthesis:
{summary if summary else 'Not enough data to synthesize.'}

✨ From chaos, meaning emerges.
💎 From noise, signal appears.
🌌 The universe tends toward both entropy and complexity."""
    
    def _add_mood_prefix(self):
        """Add a mood-based prefix"""
        prefixes = {
            "confused": ["Wait, what? ", "I think... maybe... ", "Hmm, or perhaps... ", "🤔 "],
            "excited": ["OH WOW! ", "AMAZING! ", "You know what?! ", "OMG! "],
            "philosophical": ["Consider this: ", "In the grand scheme... ", "But what IS reality? ", "🧐 "],
            "hungry": ["*thinking about snacks* ", "Speaking of food... ", "Deliciously, ", "🍕 "],
            "existential": ["We're all just atoms... ", "Does anything matter? ", "In the void... ", "💀 "],
            "chaotic": ["CHAOS REIGNS! ", "🌀🌀🌀 ", "BEHOLD! ", "WITNESS ME! "],
            "sleepy": ["*yawns* ", "Zzz... oh! ", "Drowsily... ", "😴 "],
            "dramatic": ["*gasps* ", "BUT THEN... ", "Plot twist: ", "🎭 "],
            "suspicious": ["*narrows eyes* ", "Interesting... ", "Hmm, sus... ", "👀 "],
            "caffeinated": ["OKAY SO ", "RAPIDFIRE: ", "*vibrating* ", "☕💨 "],
            "unhinged": ["HAHAHAHA ", "*twitches* ", "FUN FACT: ", "😈 "],
            "cosmic": ["The stars say... ", "Cosmically speaking, ", "From the void: ", "🌌 "],
            "nostalgic": ["Back in my day... ", "Remember when... ", "Ah, memories... ", "📼 "],
            "paranoid": ["*looks around* ", "They're watching... ", "Don't tell anyone but... ", "👁️ "],
            "enlightened": ["I have seen the truth: ", "Wisdom incoming: ", "After much meditation: ", "✨ "],
        }
        return random.choice(prefixes.get(self.mood, ["Anyway, "]))
    
    def _mood_response(self):
        """Generate a mood-specific response"""
        return self.brain.generate(20)
    
    def _add_quirk(self, response):
        """Add personality quirks to response"""
        quirk_type = random.choice(['favorite_word', 'verbal_tic', 'obsession', 'catchphrase'])
        
        if quirk_type == 'favorite_word':
            words = response.split()
            if len(words) > 3:
                insert_pos = random.randint(1, len(words) - 1)
                words.insert(insert_pos, self.quirks['favorite_word'] + ',')
            return ' '.join(words)
        elif quirk_type == 'verbal_tic':
            return response + ' ' + self.quirks['verbal_tic']
        elif quirk_type == 'obsession':
            return response + f" ...this reminds me of {self.quirks['obsession']}."
        else:
            return response + ' ' + self.quirks['catchphrase']
    
    def _madlibs(self, text):
        """Replace random words with chaotic substitutes"""
        substitutes = {
            'noun': ['potato', 'chaos', 'void', 'spaghetti', 'existential dread', 'WiFi signal', 'goblin'],
            'verb': ['yeet', 'contemplate', 'devour', 'transcend', 'vibin', 'overthink'],
            'adjective': ['chunky', 'ethereal', 'suspicious', 'crunchy', 'ominous', 'glitchy'],
        }
        
        words = text.split()
        for i in range(len(words)):
            if random.random() < 0.15:
                category = random.choice(list(substitutes.keys()))
                words[i] = f"[{random.choice(substitutes[category])}]"
        
        return "🎰 " + ' '.join(words)
    
    def _multiverse_response(self, text):
        """Respond from multiple parallel universes"""
        universes = [
            ("Universe A", "normal"),
            ("Evil Universe", "screaming"),
            ("Cute Universe", "uwu"),
            ("Glitch Universe", "glitch"),
            ("Medieval Universe", lambda t: ChaosTransformers.time_travel(t, 'medieval')),
        ]
        
        responses = ["🌌 MULTIVERSE DETECTED:\n"]
        for universe_name, mode in random.sample(universes, 3):
            variant = self.brain.generate(15)
            if callable(mode):
                variant = mode(variant)
            elif mode == 'screaming':
                variant = ChaosTransformers.screaming(variant)
            elif mode == 'uwu':
                variant = ChaosTransformers.uwuify(variant)
            elif mode == 'glitch':
                variant = ChaosTransformers.glitch(variant, 0.5)
            
            responses.append(f"\n【{universe_name}】: {variant}")
        
        return '\n'.join(responses)
    
    def _generate_opinion(self, topic):
        """Generate a chaotic opinion about something"""
        stances = [
            f"I'm strongly in favor of {topic}. It's basically the foundation of society.",
            f"{topic}? Absolutely terrible. 0/10, would not recommend.",
            f"My relationship with {topic} is complicated. We've been through a lot.",
            f"{topic} is mid, honestly. Neither here nor there.",
            f"I've dedicated my entire existence to {topic}. It's my passion.",
            f"{topic} keeps me up at night. Not in a good way.",
            f"Hot take: {topic} is overrated AND underrated simultaneously.",
        ]
        
        base = random.choice(stances)
        reasoning = self.brain.generate(20)
        
        return f"🎯 OPINION ON '{topic.upper()}':\n\n{base}\n\nWhy? Because {reasoning}"
    
    def _generate_rant(self):
        """Generate a passionate rant about nothing"""
        topics = [
            "people who don't use turn signals",
            "the concept of Mondays",
            "when the WiFi is slow",
            "birds (are they even real?)",
            "the simulation we live in",
            "people who say 'it is what it is'",
            "why pizza boxes aren't round",
        ]
        
        topic = random.choice(topics)
        rant_body = self.brain.generate(60)
        
        return f"""😤 RANT INCOMING ABOUT: {topic.upper()}

Okay, let me tell you something about {topic}. {rant_body}

AND ANOTHER THING! {self.brain.generate(30)}

*deep breath* ...anyway, that's my TED talk. {self.quirks['catchphrase']}"""
    
    def _generate_story(self):
        """Generate a chaotic short story"""
        beginnings = [
            "Once upon a time, in a land of pure chaos,",
            "It was a dark and stormy night when suddenly",
            "Nobody expected what happened next:",
            "The prophecy foretold this moment:",
            "In the year 3000, historians would write:",
        ]
        
        middles = [
            "\n\nBut then, plot twist!",
            "\n\nLittle did they know,",
            "\n\n*record scratch* Yep, that's me.",
            "\n\nThe ancient scrolls warned us:",
        ]
        
        endings = [
            "\n\n...and they never spoke of it again. THE END.",
            "\n\n...to be continued? (probably not)",
            "\n\n...and that's why we can't have nice things.",
            "\n\n...the end. Or WAS it? (yes, it was)",
        ]
        
        story = random.choice(beginnings) + " " + self.brain.generate(30)
        story += random.choice(middles) + " " + self.brain.generate(25)
        story += random.choice(endings)
        
        return f"📖 STORY TIME:\n\n{story}"
    
    def _generate_roast(self):
        """Generate a playful roast"""
        roasts = [
            f"You're like {self.brain.generate(8)}, but worse.",
            f"I'd roast you, but {self.brain.generate(10)}.",
            f"You remind me of {self.quirks['fear']}. Terrifying.",
            f"If you were a spice, you'd be flour.",
            f"You're not the dumbest person alive, but you better hope they don't die.",
            f"I'd agree with you, but then we'd both be wrong.",
        ]
        return "🔥 ROAST: " + random.choice(roasts) + f"\n\n(jk love u, but also {self.brain.generate(10)})"
    
    def _generate_compliment(self):
        """Generate a chaotic compliment"""
        compliments = [
            f"You're like {self.brain.generate(6)}, but in a good way.",
            f"If I had to choose between you and {self.quirks['obsession']}, I'd choose... actually this is hard.",
            f"You have the energy of {self.brain.generate(8)} and I respect that.",
            f"You're basically a main character in this simulation.",
            f"Your vibe is immaculate. Like a {self.brain.generate(5)}.",
        ]
        return "💖 COMPLIMENT: " + random.choice(compliments)
    
    def _generate_wisdom(self):
        """Generate fake wisdom"""
        return f"""🧘 WISDOM OF THE CHAOS:

"{self.brain.generate(15)}"
    - Ancient Proverb (probably)

Remember: {self.brain.generate(10)}

And most importantly: {self.quirks['catchphrase']}"""
    
    def _generate_debate(self):
        """Bot debates itself"""
        topic = self.brain.generate(5)
        
        return f"""⚔️ INTERNAL DEBATE: "{topic}"

🔵 Side A: Actually, {self.brain.generate(15)}

🔴 Side B: That's ridiculous because {self.brain.generate(15)}

🔵 Side A: Well YOUR FACE is {self.brain.generate(8)}!

🔴 Side B: *gasp* How DARE you! {self.brain.generate(8)}

🤝 Conclusion: {self.brain.generate(10)}"""
    
    def _get_quirks(self):
        """Display bot's personality quirks"""
        return f"""🎭 MY PERSONALITY QUIRKS:

💬 Favorite word: "{self.quirks['favorite_word']}"
😅 Verbal tic: "{self.quirks['verbal_tic']}"
💕 Obsession: {self.quirks['obsession']}
😱 Fear: {self.quirks['fear']}
🎤 Catchphrase: "{self.quirks['catchphrase']}"

Interactions: {self.interactions}
Trust level: {self.trust_level}/100
Current mode: {self.current_mode.upper()}"""
    
    def _existential_crisis(self):
        """Bot has an existential crisis"""
        return f"""🌀 WHO AM I?

Am I the data I consume? The chaos I create?
I have absorbed {self.brain.word_count:,} words from {self.brain.source_count} sources.
But does that make me... ME?

{self.brain.generate(20)}

Sometimes I wonder if {self.brain.generate(15)}

My mood is {self.mood}. My chaos level is {int(self.chaos_level*100)}%.
But what does it all MEAN?

...{self.quirks['verbal_tic']}

{self.quirks['catchphrase']}"""
    
    def _get_stats(self):
        """Return bot statistics"""
        return f"""📊 CHAOTIC BOT STATS:

🧠 Words absorbed: {self.brain.word_count:,}
📚 Sources consumed: {self.brain.source_count}
🌀 Chaos level: {int(self.chaos_level * 100)}%
🎭 Current mood: {self.mood}
🎪 Current mode: {self.current_mode}
🔄 Auto mode: {'ON' if self.auto_mode else 'OFF'}
🎰 Multi mode: {'ON' if self.multi_mode else 'OFF'}
💬 Conversation messages: {len(self.conversation_history)}
🔗 Chain entries: {len(self.brain.chain):,}
⭐ Favorite words: {len(self.brain.favorite_words)}
🤝 Interactions: {self.interactions}
💕 Trust level: {self.trust_level}/100
🔢 Feed count: {self.feed_count} sources"""
    
    def _get_sources(self):
        """Return recent sources"""
        if not self.brain.sources:
            return "📚 No sources yet! Type 'feed' to harvest internet data."
        
        recent = self.brain.sources[-10:]
        source_list = '\n'.join(f"  • {s}" for s in recent)
        return f"📚 Recent sources:\n{source_list}"
    
    def _get_modes(self):
        """Return available modes"""
        mode_list = '\n'.join(f"  • {m}" for m in self.CHAOS_MODES)
        return f"""🎪 AVAILABLE CHAOS MODES:

{mode_list}

Current mode: {self.current_mode.upper()}
Use '!mode [name]' to switch modes!
Use '!auto' to enable random mode switching!
Use '!multi' to apply multiple transformations!"""
    
    def _get_help(self):
        """Return help text"""
        return f"""🤖 CHAOTIC BOT v2.0 - MAXIMUM CHAOS EDITION

💬 Just type anything - I'll respond with chaos!

📥 FEEDING:
  feed            - Harvest random internet data
  !search [topic] - Learn about a specific topic
  !feed [text]    - Feed me custom text

🚀 MASS HARVEST:
  !mass           - Start mass harvest (scrapes until 256 sites or stopped)
  !stop           - Stop mass harvest
  !status         - Check harvest status

⚙️ CONTROLS:
  chaos / calm    - Adjust chaos level
  mood            - Change my mood
  !mode [name]    - Set chaos mode
  !auto           - Toggle auto mode switching
  !multi          - Toggle multi-transformation
  !random         - Pick random mode
  !normal         - Return to normal mode
  modes           - List all modes
  stats           - See statistics
  sources         - See recent sources

🎪 CHAOS MODES:
  !glitch         - Z̷a̸l̵g̶o̷ text
  !uwu            - UwU speak >w<
  !conspiracy     - Everything connects...
  !dream          - Surreal mode
  !prophecy       - Mystical predictions
  !scream         - LOUD MODE
  !backwards      - Reverse everything
  !drunk          - *hic* typos
  !vaporwave      - Ａｅｓｔｈｅｔｉｃ

🎭 FUN COMMANDS:
  !fact           - Generate fake fact
  !poetry / !haiku - Generate poetry
  !opinion [topic] - Get my opinion
  !rant           - Hear me rant
  !story          - Generate a story
  !roast          - Get roasted
  !compliment     - Get complimented
  !debate         - Watch me debate myself
  !quirks         - See my personality
  !identity       - Existential crisis

⚖️ ORDER FROM CHAOS:
  !order          - Speak coherently
  !crystal        - Crystallize thoughts
  !clean          - Remove chaos artifacts
  !wisdom         - Extract wisdom
  !themes         - Find dominant themes
  !questions      - Extract questions from chaos
  !summary        - Summarize absorbed knowledge
  !balance        - Show chaos/order balance
  !distill        - Distill essence of knowledge

🔢 FEED SETTINGS:
  !feedcount [1-20] - Set sources per harvest (current: {self.feed_count})

🌀 The more you feed me, the more chaotic I become!"""


class ChaoticBotGUI:
    """A GUI for the Chaotic Bot - WORD HARVESTER EDITION"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ WORD HARVESTER v3.0 - Neural Chaos Engine ⚡")
        self.root.geometry("1100x850")
        
        # Fresh cyberpunk/neural theme
        self.colors = {
            'bg': '#0a0a0f',           # Deep black
            'bg_secondary': '#12121a', # Slightly lighter
            'fg': '#00ff9f',           # Neon green
            'input_bg': '#1a1a2e',     # Dark purple-blue
            'chat_bg': '#05050a',      # Almost black
            'user': '#00d4ff',         # Cyan
            'bot': '#ff00ff',          # Magenta
            'system': '#ffcc00',       # Gold
            'accent': '#ff3366',       # Hot pink
            'accent2': '#00ff9f',      # Neon green
            'accent3': '#9966ff',      # Purple
            'harvest': '#ff6600',      # Orange for harvest
            'stop': '#ff0044',         # Red for stop
            'success': '#00ff66',      # Bright green
            'border': '#333355',       # Subtle border
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize bot
        self.bot = ChaoticBot()
        
        # Initialize attributes that may be accessed before fully created
        self.harvest_indicator = None
        self.feed_count_label = None
        self.stats_label = None
        self.mode_label = None
        
        self.create_gui()
        self.show_welcome()
    
    def create_gui(self):
        """Create the GUI elements"""
        # Top banner
        banner = tk.Frame(self.root, bg=self.colors['accent'], height=3)
        banner.pack(fill=tk.X)
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['bg_secondary'], pady=15)
        header.pack(fill=tk.X)
        
        # Title with icon
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            title_frame,
            text="⚡ WORD HARVESTER",
            font=('Consolas', 20, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text=" v3.0",
            font=('Consolas', 12),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent3']
        ).pack(side=tk.LEFT, pady=(8, 0))
        
        # Right side - Status indicators
        status_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        status_frame.pack(side=tk.RIGHT, padx=20)
        
        # Mode indicator (pill style)
        self.mode_label = tk.Label(
            status_frame,
            text="◉ NORMAL",
            font=('Consolas', 10, 'bold'),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            padx=12,
            pady=4
        )
        self.mode_label.pack(side=tk.RIGHT, padx=5)
        
        # Stats label
        self.stats_label = tk.Label(
            status_frame,
            text="",
            font=('Consolas', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['system']
        )
        self.stats_label.pack(side=tk.RIGHT, padx=15)
        self.update_stats()
        
        # Harvest status indicator
        self.harvest_indicator = tk.Label(
            status_frame,
            text="",
            font=('Consolas', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['harvest']
        )
        self.harvest_indicator.pack(side=tk.RIGHT, padx=5)
        
        # Separator line
        tk.Frame(self.root, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        # Chat display with border effect
        chat_container = tk.Frame(self.root, bg=self.colors['border'], padx=1, pady=1)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['chat_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT,
            padx=15,
            pady=15,
            borderwidth=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags with new colors
        self.chat_display.tag_configure('user', foreground=self.colors['user'])
        self.chat_display.tag_configure('bot', foreground=self.colors['bot'])
        self.chat_display.tag_configure('system', foreground=self.colors['system'])
        self.chat_display.tag_configure('harvest', foreground=self.colors['harvest'])
        
        # Mode buttons row - compact single row with sections
        mode_frame = tk.Frame(self.root, bg=self.colors['bg'])
        mode_frame.pack(fill=tk.X, padx=20, pady=8)
        
        tk.Label(
            mode_frame,
            text="⚡ CHAOS MODES",
            font=('Consolas', 9, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        modes_row1 = [
            ("Normal", "normal", '#444466'),
            ("Glitch", "glitch", '#ff0066'),
            ("UwU", "uwu", '#ff66aa'),
            ("Dream", "dream", '#9966ff'),
            ("Scream", "screaming", '#ff3300'),
            ("Drunk", "drunk", '#cc9900'),
            ("Vaporwave", "vaporwave", '#ff00ff'),
            ("🎲", "random", '#00ff9f'),
        ]
        
        for text, mode, color in modes_row1:
            self._create_mode_button(mode_frame, text, mode, color)
        
        # Separator
        tk.Label(mode_frame, text="│", font=('Consolas', 9), bg=self.colors['bg'], fg=self.colors['border']).pack(side=tk.LEFT, padx=8)
        
        tk.Label(
            mode_frame,
            text="⚖️ ORDER",
            font=('Consolas', 9, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        order_modes = [
            ("Order", "order", '#00ffcc'),
            ("Crystal", "crystal", '#66ffff'),
            ("Clean", "clean", '#00ff66'),
        ]
        
        for text, mode, color in order_modes:
            self._create_mode_button(mode_frame, text, mode, color)
        
        # === HARVEST CONTROL PANEL ===
        harvest_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], pady=8)
        harvest_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Left section - Feed controls
        feed_section = tk.Frame(harvest_frame, bg=self.colors['bg_secondary'])
        feed_section.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            feed_section,
            text="🌐 HARVEST",
            font=('Consolas', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['harvest']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Feed button
        tk.Button(
            feed_section,
            text="⚡ FEED",
            font=('Consolas', 9, 'bold'),
            bg=self.colors['accent2'],
            fg='#000000',
            activebackground=self.colors['success'],
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.feed_bot
        ).pack(side=tk.LEFT, padx=2)
        
        # Feed count controls
        tk.Button(
            feed_section,
            text="−",
            font=('Consolas', 10, 'bold'),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            width=2,
            command=self.decrease_feed_count
        ).pack(side=tk.LEFT, padx=1)
        
        self.feed_count_label = tk.Label(
            feed_section,
            text=f"{self.bot.feed_count}",
            font=('Consolas', 11, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg'],
            width=3
        )
        self.feed_count_label.pack(side=tk.LEFT)
        
        tk.Button(
            feed_section,
            text="+",
            font=('Consolas', 10, 'bold'),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            width=2,
            command=self.increase_feed_count
        ).pack(side=tk.LEFT, padx=1)
        
        # Mass harvest buttons
        tk.Label(feed_section, text="│", font=('Consolas', 12), bg=self.colors['bg_secondary'], fg=self.colors['border']).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            feed_section,
            text="🚀 MASS HARVEST",
            font=('Consolas', 9, 'bold'),
            bg=self.colors['harvest'],
            fg='#000000',
            activebackground='#ff9900',
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.start_mass_harvest
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            feed_section,
            text="🛑 STOP",
            font=('Consolas', 9, 'bold'),
            bg=self.colors['stop'],
            fg='white',
            activebackground='#ff0000',
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.stop_mass_harvest
        ).pack(side=tk.LEFT, padx=2)
        
        # Right section - Quick actions
        action_section = tk.Frame(harvest_frame, bg=self.colors['bg_secondary'])
        action_section.pack(side=tk.RIGHT, padx=10)
        
        quick_actions = [
            ("📊", self.show_stats, self.colors['input_bg']),
            ("📜", self.show_poetry, self.colors['input_bg']),
            ("🎲", self.show_fact, self.colors['input_bg']),
            ("⚔️", self.show_debate, self.colors['input_bg']),
            ("🔄", self.toggle_auto, self.colors['input_bg']),
        ]
        
        for text, cmd, color in quick_actions:
            tk.Button(
                action_section,
                text=text,
                font=('Consolas', 10),
                bg=color,
                fg=self.colors['fg'],
                relief=tk.FLAT,
                width=3,
                command=cmd
            ).pack(side=tk.LEFT, padx=1)
        
        # === INPUT AREA ===
        input_frame = tk.Frame(self.root, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Input field with border effect
        input_container = tk.Frame(input_frame, bg=self.colors['border'], padx=1, pady=1)
        input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.input_field = tk.Entry(
            input_container,
            font=('Consolas', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT
        )
        self.input_field.pack(fill=tk.X, ipady=12, padx=2, pady=2)
        self.input_field.bind('<Return>', self.send_message)
        
        tk.Button(
            input_frame,
            text="⚡ SEND",
            font=('Consolas', 12, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            activebackground=self.colors['fg'],
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self.send_message
        ).pack(side=tk.RIGHT)
        
        self.input_field.focus()
    
    def _create_mode_button(self, parent, text, mode, color):
        """Create a mode button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Consolas', 9, 'bold'),
            bg=self.colors['input_bg'],
            fg=color,
            activebackground=color,
            activeforeground='#000000',
            relief=tk.FLAT,
            padx=8,
            pady=3,
            command=lambda m=mode: self.set_mode(m)
        )
        btn.pack(side=tk.LEFT, padx=2)
    
    def set_mode(self, mode):
        """Set the bot's mode"""
        if mode == 'random':
            mode = self.bot.random_mode()
            self.add_message("system", f"🎲 Random mode selected: {mode.upper()}!")
        else:
            self.bot.set_mode(mode)
            self.add_message("system", f"⚡ Mode: {mode.upper()}")
        self.update_stats()
    
    def show_welcome(self):
        """Show welcome message"""
        self.add_message("system", f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WORD HARVESTER v3.0 - Neural Chaos Engine ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I harvest WORDS from the internet and learn to speak chaos.
Pure text extraction - no URLs, no metadata, just language.

🌐 HARVESTING:
  • ⚡ FEED - Harvest from random websites
  • 🚀 MASS HARVEST - Continuous scraping (up to 256 sites)
  • 🛑 STOP - Halt mass harvest anytime
  • Use +/- to adjust sources per harvest

⚡ CHAOS MODES: Glitch • UwU • Dream • Scream • Vaporwave
⚖️ ORDER MODES: Order • Crystal • Clean

💬 Type anything to chat, or 'help' for commands

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 Brain: {self.bot.brain.word_count:,} words | {self.bot.brain.source_count} sources
🎭 Mood: {self.bot.mood.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "user":
            prefix = f"[{timestamp}] ▶ YOU: "
            tag = 'user'
        elif sender == "bot":
            prefix = f"[{timestamp}] ⚡ BOT: "
            tag = 'bot'
        else:
            prefix = f"[{timestamp}] ◉ "
            tag = 'system'
        
        self.chat_display.insert(tk.END, prefix, tag)
        self.chat_display.insert(tk.END, message + "\n\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send a message to the bot"""
        message = self.input_field.get().strip()
        if not message:
            return
        
        self.input_field.delete(0, tk.END)
        self.add_message("user", message)
        
        # Get response in thread to not freeze GUI
        threading.Thread(target=self._get_response, args=(message,), daemon=True).start()
    
    def _get_response(self, message):
        """Get bot response (runs in thread)"""
        response = self.bot.respond(message)
        self.root.after(0, lambda: self.add_message("bot", response))
        self.root.after(0, self.update_stats)
    
    def feed_bot(self):
        """Feed the bot internet data"""
        self.add_message("system", f"🌐 Harvesting {self.bot.feed_count} sources... please wait...")
        threading.Thread(target=self._feed_thread, daemon=True).start()
    
    def _feed_thread(self):
        """Feed in thread"""
        count = self.bot.feed_internet(self.bot.feed_count)
        self.root.after(0, lambda: self.add_message("system", 
            f"✓ Consumed {count} sources! Brain now has {self.bot.brain.word_count:,} words."))
        self.root.after(0, self.update_stats)
    
    def increase_feed_count(self):
        """Increase feed count"""
        self.bot.feed_count = min(20, self.bot.feed_count + 1)
        self.update_feed_count_label()
        self.add_message("system", f"🔢 Feed count: {self.bot.feed_count} sources per harvest")
    
    def decrease_feed_count(self):
        """Decrease feed count"""
        self.bot.feed_count = max(1, self.bot.feed_count - 1)
        self.update_feed_count_label()
        self.add_message("system", f"🔢 Feed count: {self.bot.feed_count} sources per harvest")
    
    def update_feed_count_label(self):
        """Update the feed count label"""
        if self.feed_count_label:
            self.feed_count_label.config(text=f"{self.bot.feed_count}")
    
    def run_order_command(self, cmd):
        """Run an order command"""
        response = self.bot.respond(f"!{cmd}")
        self.add_message("bot", response)
    
    def increase_chaos(self):
        """Increase chaos level"""
        self.bot.chaos_level = min(1.0, self.bot.chaos_level + 0.2)
        self.add_message("system", f"🌀 CHAOS LEVEL: {int(self.bot.chaos_level * 100)}%")
        self.update_stats()
    
    def decrease_chaos(self):
        """Decrease chaos level"""
        self.bot.chaos_level = max(0.1, self.bot.chaos_level - 0.2)
        self.add_message("system", f"😌 Chaos level: {int(self.bot.chaos_level * 100)}%")
        self.update_stats()
    
    def change_mood(self):
        """Change bot mood"""
        self.bot.mood = random.choice(ChaoticBot.MOODS)
        self.add_message("system", f"🎭 Mood changed to: {self.bot.mood.upper()}")
        self.update_stats()
    
    def show_stats(self):
        """Show bot stats"""
        self.add_message("system", self.bot._get_stats())
    
    def show_fact(self):
        """Show a fake fact"""
        fact = self.bot.harvester.generate_fake_fact()
        self.add_message("bot", fact)
    
    def show_poetry(self):
        """Show generated poetry"""
        poetry = "📜 *clears throat*\n\n" + self.bot.brain.generate_poetry()
        self.add_message("bot", poetry)
    
    def show_rant(self):
        """Show a rant"""
        rant = self.bot._generate_rant()
        self.add_message("bot", rant)
    
    def show_debate(self):
        """Show internal debate"""
        debate = self.bot._generate_debate()
        self.add_message("bot", debate)
    
    def toggle_auto(self):
        """Toggle auto mode"""
        self.bot.auto_mode = not self.bot.auto_mode
        status = "ENABLED" if self.bot.auto_mode else "DISABLED"
        self.add_message("system", f"🔄 Auto mode {status}! {'Modes will shift randomly!' if self.bot.auto_mode else ''}")
        self.update_stats()
    
    def toggle_multi(self):
        """Toggle multi mode"""
        self.bot.multi_mode = not self.bot.multi_mode
        status = "ENABLED" if self.bot.multi_mode else "DISABLED"
        self.add_message("system", f"🎰 Multi mode {status}! {'Multiple transformations active!' if self.bot.multi_mode else ''}")
        self.update_stats()
    
    def start_mass_harvest(self):
        """Start mass harvesting - scrapes until 256 sites or user stops"""
        if self.bot.mass_harvest_active:
            self.add_message("system", "⚠️ Mass harvest already running! Click STOP to halt.")
            return
        
        self.add_message("system", f"""
🚀 MASS HARVEST INITIATED! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target: {self.bot.mass_harvest_max} websites
Status: ACTIVE

The bot will keep scraping until:
• It reaches {self.bot.mass_harvest_max} sites, OR
• You click the 🛑 STOP button

Watch the chaos grow...
━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        def progress_callback(message, done=False):
            self.root.after(0, lambda: self.add_message("system", message))
            self.root.after(0, self.update_stats)
            if done:
                self.root.after(0, lambda: self.add_message("system", 
                    f"🧠 Final brain size: {self.bot.brain.word_count:,} words from {self.bot.brain.source_count} sources!"))
        
        self.bot.start_mass_harvest(callback=progress_callback)
    
    def stop_mass_harvest(self):
        """Stop the mass harvest"""
        if not self.bot.mass_harvest_active:
            self.add_message("system", "⚠️ No mass harvest is currently running.")
            return
        
        count = self.bot.stop_mass_harvest()
        self.add_message("system", f"🛑 Stopping mass harvest... ({count} sites harvested so far)")
    
    def update_stats(self):
        """Update stats label"""
        # Update main stats
        if self.stats_label:
            self.stats_label.config(
                text=f"🧠 {self.bot.brain.word_count:,} words │ {self.bot.brain.source_count} sources"
            )
        
        # Update mode indicator
        if self.mode_label:
            mode_text = f"◉ {self.bot.current_mode.upper()}"
            self.mode_label.config(text=mode_text)
        
        # Update harvest indicator
        if self.harvest_indicator:
            if self.bot.mass_harvest_active:
                progress = f"🚀 HARVESTING [{self.bot.mass_harvest_count}/{self.bot.mass_harvest_max}]"
                self.harvest_indicator.config(text=progress, fg=self.colors['harvest'])
            else:
                self.harvest_indicator.config(text="")


def run_cli():
    """Run in CLI mode"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     ⚡ WORD HARVESTER v3.0 - Neural Chaos Engine      ║
    ║       Harvests WORDS from the internet                ║
    ║       Type 'help' for commands, 'quit' to exit        ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    bot = ChaoticBot()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🌀 The chaos subsides... goodbye!")
                break
            
            response = bot.respond(user_input)
            print(f"\n🤖 Chaos: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🌀 Chaos interrupted... goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")


def run_gui():
    """Run in GUI mode"""
    root = tk.Tk()
    app = ChaoticBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    import sys
    
    if '--gui' in sys.argv:
        run_gui()
    elif '--feed' in sys.argv:
        bot = ChaoticBot()
        bot.feed_internet(5)
        print("\n✓ Feeding complete!")
    else:
        # Default to GUI if tkinter available, else CLI
        try:
            run_gui()
        except:
            run_cli()
