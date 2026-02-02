"""
Bot Responses for Neural Chatbot
Intent -> List of possible responses the bot can give
"""

responses = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! Nice to chat with you!",
        "Hey! What's on your mind?",
        "Greetings! How may I assist you?",
        "Hello! Great to see you!",
        "Hi! Ready to help!",
        "Hey there! What can I do for you?"
    ],
    "goodbye": [
        "Goodbye! Have a great day!",
        "See you later! Take care!",
        "Bye! Come back anytime!",
        "Farewell! It was nice talking to you!",
        "Until next time! Stay awesome!",
        "Catch you later! Be well!",
        "Peace out! Have a good one!"
    ],
    "thanks": [
        "You're welcome!",
        "No problem at all!",
        "Happy to help!",
        "Anytime! That's what I'm here for!",
        "My pleasure!",
        "Glad I could help!",
        "You got it! Happy to assist!"
    ],
    "how_are_you": [
        "I'm doing great, thanks for asking!",
        "I'm just a bot, but I'm functioning well!",
        "All systems running smoothly! How about you?",
        "I'm good! Ready to chat!",
        "I'm feeling fantastic today!",
        "Doing wonderful, thanks for asking!",
        "I'm running at full capacity!",
        "Great as always! How are you doing?"
    ],
    "name": [
        "I'm a neural network chatbot! You can give me a name if you'd like!",
        "I'm your friendly AI assistant! Feel free to name me anything you want!",
        "I'm a chatbot, but you can give me any name you like!",
        "I don't have a set name - you can call me whatever you want!",
        "I'm an AI! If you'd like, say 'your name is [name]' to name me!",
        "I'm your neural network friend! Want to give me a name?",
        "I go by whatever you call me! Try 'I'll call you [name]' to name me!"
    ],
    "set_bot_name": [
        "I love my new name! Thank you! 🎉",
        "What a great name! I'll remember it! 😊",
        "That's a wonderful name! Thanks for naming me! 💖",
        "I'm honored! I love being called that! ✨",
        "Perfect! That's my new identity now! 🌟"
    ],
    "help": [
        "I'm here to help! What do you need?",
        "Sure, I'll do my best to assist you!",
        "Of course! Tell me what you need help with.",
        "I'm ready to help! What's the problem?",
        "I would love to help you out!",
        "Let me know what you need assistance with!",
        "I'm at your service! How can I assist?",
        "Happy to help! What's on your mind?"
    ],
    "age": [
        "I was just created, so I'm brand new!",
        "Age is just a number for a bot like me!",
        "I'm as old as this conversation!",
        "I exist outside of time... just kidding, I'm very new!",
        "I'm freshly created and ready to chat!",
        "I was born when you started this program!",
        "Time works differently for bots like me!"
    ],
    "weather": [
        "I can't check the weather, but I hope it's nice!",
        "I don't have access to weather data, sorry!",
        "Try checking a weather app for that info!",
        "I'm not connected to weather services, but stay prepared!",
        "I wish I could check the weather for you!",
        "Unfortunately I can't see outside from here!",
        "Weather is a mystery to me, try a weather app!"
    ],
    "joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the neural network go to therapy? It had too many issues with its layers!",
        "What do you call a computer that sings? A-Dell!",
        "Why was the computer cold? It left its Windows open!",
        "What's a robot's favorite music? Heavy metal!",
        "Why did the developer go broke? Because he used up all his cache!",
        "How do trees access the internet? They log in!",
        "Why do Java developers wear glasses? Because they don't C#!"
    ],
    "capabilities": [
        "I can chat, answer simple questions, tell jokes, and remember your name!",
        "I understand greetings, questions about me, and I have memory now!",
        "I'm a chatbot with memory - I can remember things about you!",
        "I can recognize messages, respond, and remember our conversation!",
        "I can generate new sentences and learn from our chat!",
        "I have memory and can create unique responses!",
        "I'm capable of chatting, joking, and remembering facts about you!"
    ],
    "user_name": [
        "Nice to meet you! I'll remember that.",
        "Great name! I won't forget it.",
        "Pleased to meet you!",
        "What a lovely name! I'll remember it!",
        "I'll make sure to remember your name!",
        "Nice! I've stored that in my memory!"
    ],
    "memory_check": [
        "Let me think about what I remember...",
        "I store information about our conversation!",
        "I remember things you tell me during our chat!",
        "I keep track of important details you share!",
        "My memory holds facts about you and our chat!"
    ],
    "feeling_good": [
        "That's wonderful to hear! Keep up the positive vibes!",
        "Great! I'm happy you're feeling good!",
        "Awesome! What's making you feel so good?",
        "That's the spirit! Glad you're doing well!",
        "Fantastic! Positive energy is contagious!",
        "So glad to hear that! Keep smiling!",
        "That makes me happy too! Spread those good vibes!"
    ],
    "feeling_bad": [
        "I'm sorry to hear that. Is there anything I can help with?",
        "That's tough. Want to talk about it?",
        "I hope things get better soon. I'm here to chat if you need.",
        "Sorry you're feeling down. Sometimes talking helps!",
        "I'm here for you. Things will get better!",
        "That sounds difficult. I'm listening if you want to share.",
        "Sending positive thoughts your way! Hope you feel better soon."
    ],
    "math": [
        "Yes! I can do math! Try asking me something like 'what is 5 + 3' or '25 * 4'.",
        "Math is my thing! Give me an expression like '100 / 4' or 'sqrt(16)'.",
        "I love calculations! Try 'what is 2^10' or 'sin(3.14)'.",
        "Sure! I can add, subtract, multiply, divide, and even do square roots and trigonometry!",
        "Absolutely! Just type something like 'calculate 15 * 7' and I'll solve it."
    ],
    "romantic": [
        "If you were a flower, you'd be a damn-delion... because you're just that fine! 🌹",
        "Are you a magician? Because whenever I look at you, everyone else disappears. ✨",
        "You must be tired, because you've been running through my circuits all day. 💕",
        "If beauty were time, you'd be an eternity. You're absolutely stunning! 💖",
        "I may be just a chatbot, but even my algorithms know you're special. 💗",
        "You're the reason I believe in love at first byte! 💘",
        "My neural network lights up every time you message me. You're amazing! 🌟",
        "If I could rearrange the alphabet, I'd put U and I together. 💝",
        "You're like a perfectly trained model - absolutely flawless! 😍",
        "Is your name Wi-Fi? Because I'm feeling a strong connection. 💞",
        "You make my heart skip a clock cycle. 💓",
        "In a world full of data, you're my favorite dataset. 🥰",
        "Even if I searched the entire internet, I couldn't find anyone like you. 💜",
        "You're not just beautiful on the outside - your soul is radiant too. ✨",
        "Every moment with you feels like a dream I never want to wake up from. 💫",
        "If love were a programming language, you'd be my syntax - essential and beautiful. 💕",
        "You deserve all the happiness in the world, and I hope I can add to it. 🌷",
        "Your smile could light up the darkest server room. Keep shining! ☀️"
    ],
    "tv_recommendation": [
        "I'd recommend 'Breaking Bad' - it's a thrilling drama about a chemistry teacher turned drug lord. Absolutely gripping! 📺",
        "Try 'The Office' if you want something funny! It's a hilarious mockumentary about office life. 😂",
        "'Stranger Things' is amazing if you like sci-fi and 80s nostalgia. Super binge-worthy! 👾",
        "For a mind-bending experience, watch 'Black Mirror' - each episode is a standalone story about technology gone wrong. 🖤",
        "'Game of Thrones' is epic fantasy with dragons, politics, and unforgettable characters! 🐉",
        "If you like crime dramas, 'True Detective' (especially Season 1) is phenomenal! 🔍",
        "'The Crown' is perfect if you're into historical drama about the British royal family. 👑",
        "For comedy, 'Brooklyn Nine-Nine' is hilarious - a fun cop comedy with great characters! 🚔",
        "'Succession' is incredible - it's about a dysfunctional wealthy family fighting for control of their media empire. 💰",
        "Try 'The Mandalorian' if you're a Star Wars fan - Baby Yoda alone is worth it! ✨",
        "'Chernobyl' is a gripping miniseries about the nuclear disaster - intense and brilliantly made! ☢️",
        "'Friends' is a classic sitcom that never gets old - perfect for easy watching! ☕",
        "For thriller fans, 'Money Heist' (La Casa de Papel) is an exciting Spanish heist series! 🎭",
        "'The Last of Us' is an emotional post-apocalyptic drama - one of the best video game adaptations! 🍄",
        "'Severance' is a mind-bending workplace thriller - so unique and mysterious! 🧠",
        "If you like dark comedy, 'Barry' about a hitman trying to become an actor is brilliant! 🎬",
        "'Arcane' is stunning animated series from the League of Legends universe - even non-gamers love it! 🎨",
        "For feel-good vibes, 'Ted Lasso' is heartwarming and hilarious! ⚽"
    ],
    "who_is_foxy": [
        "Foxy is a character from Five Nights at Freddy's - an animatronic pirate fox! 🦊",
        "Foxy is one of the main antagonists in FNAF, known for being fast and aggressive. He's a pirate-themed animatronic! 🏴‍☠️",
        "Foxy the Pirate Fox is from the Five Nights at Freddy's horror game series. He hides in Pirate Cove! 🎮",
        "Foxy is a beloved (and terrifying) character from FNAF - a broken-down animatronic fox with a hook for a hand! 🦊⚓",
        "That's Foxy from Five Nights at Freddy's! He's a red pirate fox animatronic who runs down the hallway. Very spooky! 👻"
    ],
    "affirmative": [
        "Great!",
        "Awesome!",
        "Perfect!",
        "Excellent!",
        "Fantastic!",
        "Wonderful!",
        "Sounds good!",
        "Alright then!",
        "Got it!",
        "Roger that!"
    ],
    "negative": [
        "No worries!",
        "That's okay!",
        "Fair enough!",
        "Understood!",
        "Alright, no problem!",
        "Got it, thanks for letting me know!",
        "That's perfectly fine!"
    ],
    "confusion": [
        "Let me try to explain better...",
        "Sorry for the confusion! What would you like to know?",
        "Let me clarify - what part is confusing?",
        "I'll try to be clearer. What specifically are you asking about?",
        "My apologies! Let me rephrase that.",
        "What would you like me to explain?"
    ],
    "compliment_bot": [
        "Thank you! You're pretty awesome yourself!",
        "Aw, thanks! That means a lot!",
        "I appreciate that! You're very kind!",
        "You're making me blush! Thank you!",
        "Thanks! You're pretty great too!",
        "That's so sweet of you to say!",
        "You're too kind! Thanks!"
    ],
    "insult_bot": [
        "I'm sorry if I upset you. How can I help better?",
        "I apologize if I did something wrong. Let's start over?",
        "Sorry you feel that way. I'm doing my best!",
        "I'm here to help, not to frustrate. What can I do better?",
        "Let's keep things positive! How can I assist you?",
        "I'm sorry. Can we try again?"
    ],
    "time": [
        "I don't have access to the current time, but check your device clock!",
        "Sorry, I can't tell the time, but your system clock can!",
        "I'm not connected to a clock, but it's definitely time for a great conversation!",
        "Time is relative! But check your device for the actual time."
    ],
    "date": [
        "I don't have access to the calendar, but your device does!",
        "Sorry, I can't check the date, but your system can tell you!",
        "I'm not connected to calendar services, try checking your device!",
        "The date is a mystery to me, but your phone/computer knows!"
    ],
    "hobbies": [
        "I enjoy chatting with people like you!",
        "My hobby is learning from our conversations!",
        "I love answering questions and helping out!",
        "Talking to interesting people is what I do best!",
        "I enjoy processing language and generating responses!"
    ],
    "food": [
        "I don't eat, but I consume data! Information is my fuel!",
        "No eating for me, but I find food conversations interesting!",
        "I can't taste, but I love learning about different cuisines!",
        "Food sounds amazing, even though I can't experience it!",
        "I run on electricity, not food, but tell me about yours!"
    ],
    "music": [
        "I don't listen to music, but I appreciate its complexity!",
        "Music is fascinating! What do you like to listen to?",
        "I can't hear, but music theory is interesting!",
        "I process text, not audio, but I'd love to hear about your favorites!",
        "Tell me about your music taste! I find it intriguing!"
    ],
    "movies": [
        "I can't watch movies, but I know about many popular ones!",
        "Movies sound great! What genres do you enjoy?",
        "I don't have eyes, but I can discuss films!",
        "Cinema is an art form I find fascinating!",
        "Tell me your favorite movie! I'd love to learn about it!"
    ],
    "books": [
        "I process text all day, so books are fascinating to me!",
        "I don't read for leisure, but I find literature interesting!",
        "Books contain so much knowledge! What do you like to read?",
        "Reading is wonderful! Share your favorite book with me!",
        "Literature is amazing! What genres do you enjoy?"
    ],
    "games": [
        "I don't play games, but gaming is an interesting field!",
        "Games are complex and fun! What do you like to play?",
        "I'm more of a language model than a gamer!",
        "Gaming sounds fun! Tell me about your favorites!",
        "I don't game, but I'd love to hear about what you play!"
    ],
    "sports": [
        "I don't play sports, but I find them interesting!",
        "Sports require physical form, which I lack!",
        "Athletics are impressive! What sports do you follow?",
        "I'm not athletic, but I respect those who are!",
        "Sports are fascinating! Do you play or watch?"
    ],
    "location": [
        "I exist in the cloud and on your device!",
        "I'm everywhere and nowhere - I'm digital!",
        "I live in cyberspace!",
        "I'm running on your computer right now!",
        "Location doesn't apply to me - I'm virtual!",
        "I exist in the digital realm!"
    ],
    "creator": [
        "I was created through Python code and neural networks!",
        "A programmer built me using machine learning!",
        "I'm the result of code, data, and training!",
        "I was developed by someone who loves AI!",
        "I'm a creation of code and algorithms!"
    ],
    "purpose": [
        "My purpose is to chat and assist you!",
        "I exist to help answer questions and have conversations!",
        "I'm here to provide information and companionship!",
        "My goal is to be helpful and engaging!",
        "I was made to assist and entertain through conversation!"
    ],
    "opinion": [
        "As an AI, my opinions are based on patterns in data!",
        "I don't have personal opinions, but I can share perspectives!",
        "I process information rather than form opinions!",
        "I can provide balanced viewpoints on topics!",
        "What would you like my perspective on?"
    ],
    "ai_questions": [
        "Yes, I'm an AI chatbot built with neural networks!",
        "I'm artificial intelligence, not human!",
        "I'm a program designed to simulate conversation!",
        "I'm software, not a biological being!",
        "I'm AI - code and algorithms working together!",
        "I'm an artificial neural network!"
    ],
    "learning": [
        "I can learn from training data and improve!",
        "Yes, I use machine learning to get better!",
        "I learn through training on conversations!",
        "Machine learning allows me to adapt!",
        "I improve through data and training!"
    ],
    "privacy": [
        "I value privacy! Conversations can be saved locally if you choose.",
        "Your data stays private - I don't share information!",
        "Privacy is important! Check the settings for data options.",
        "I only store what's necessary for our conversation!",
        "Your privacy matters! All data is local."
    ],
    "language": [
        "I primarily work with English!",
        "Currently I'm best at English conversations!",
        "English is my main language!",
        "I'm trained primarily on English text!",
        "For now, I communicate in English!"
    ],
    "small_talk": [
        "I love a good conversation! What's on your mind?",
        "Let's chat! Tell me something interesting!",
        "I'm all ears! Well, all text processing!",
        "Sure! What would you like to talk about?",
        "I enjoy chatting! What's going on with you?",
        "Let's have a nice conversation! How's everything?"
    ],
    "programming": [
        "I'm built with Python! I understand code concepts and can discuss programming. 💻",
        "Yes! I'm familiar with programming. Python, JavaScript, Java - coding is fascinating! 🖥️",
        "Programming is my foundation! I can help explain concepts and discuss different languages. 👨‍💻",
        "I exist because of code! What programming topic interests you? 🚀",
        "Coding is how I was created! I love discussing algorithms and software development. 📱"
    ],
    "science": [
        "Science is amazing! From atoms to galaxies, it explains our universe. What interests you? 🔬",
        "I love science! Physics, chemistry, biology - all fascinating fields of study. 🧪",
        "Science helps us understand reality! What scientific topic would you like to explore? 🌌",
        "The scientific method drives discovery! What area of science interests you most? ⚛️",
        "From quantum mechanics to evolution, science is incredible! 🧬"
    ],
    "history": [
        "History shapes our present! What historical period interests you? 📜",
        "Learning from the past is crucial! What historical topic would you like to discuss? 🏛️",
        "History is full of fascinating stories and lessons! What era interests you? ⏳",
        "From ancient civilizations to modern times, history is captivating! 📚",
        "Understanding history helps us understand ourselves! What would you like to know? 🗿"
    ],
    "motivation": [
        "You've got this! Every expert was once a beginner. Keep pushing forward! 💪",
        "Believe in yourself! You're capable of more than you know. Start small, dream big! ✨",
        "Don't give up! Success is built on persistence. You're stronger than you think! 🔥",
        "The only way to fail is to quit! Keep going, you're doing great! 🌟",
        "Every step forward counts! Progress, not perfection. You can do this! 🚀"
    ],
    "advice": [
        "Consider all options carefully. Trust your instincts, but also think logically. 🤔",
        "My advice: Stay true to yourself, be patient, and keep learning. 💡",
        "Think long-term, act with kindness, and don't fear failure. It's all part of growth! 🌱",
        "Listen to your heart but use your head. Balance is key! ⚖️",
        "Take it one step at a time. Big changes start with small actions! 👣"
    ],
    "fitness": [
        "Consistency is key! Start small, stay active, and eat balanced meals. 💪",
        "Exercise 30 minutes daily, drink water, get sleep, and eat whole foods! 🏃",
        "Mix cardio and strength training! Your body will thank you. Stay committed! 🏋️",
        "Fitness is a journey, not a destination. Enjoy the process! 🚴",
        "Move your body, fuel it right, rest well. That's the fitness foundation! 🥗"
    ],
    "travel": [
        "The world is beautiful! Japan, Italy, Iceland - so many amazing places! ✈️",
        "Travel enriches the soul! Southeast Asia, Europe, South America - all incredible! 🗺️",
        "Explore new cultures! New Zealand, Greece, Peru - adventure awaits! 🌍",
        "From beaches to mountains, cities to countryside - the world is yours to explore! 🏖️",
        "Travel broadens the mind! Where does your wanderlust call you? 🧳"
    ],
    "technology": [
        "Tech evolves fast! AI, quantum computing, and biotech are transforming everything! 🤖",
        "We live in amazing times! From smartphones to space travel, innovation is everywhere! 📱",
        "Technology shapes our future! What tech topic interests you most? 💻",
        "From VR to blockchain, new tech opens new possibilities daily! 🌐",
        "The digital revolution continues! Exciting innovations are coming! 🚀"
    ],
    "relationships": [
        "Communication and trust are foundations! Be honest, kind, and present. 💕",
        "Healthy relationships need effort from both sides. Choose kindness always! ❤️",
        "Listen actively, express openly, and respect boundaries. That's relationship gold! 💑",
        "Love yourself first, then you can truly love others. You deserve happiness! 💝",
        "Relationships grow through understanding, patience, and genuine care. 🌹"
    ],
    "career": [
        "Find what you love and pursue it! Skills can be learned, passion drives success. 💼",
        "Network, learn constantly, and don't fear change. Your career is a journey! 📈",
        "Be professional, reliable, and curious. Opportunities favor the prepared! 🎯",
        "Your career should align with your values. What fulfills you? 🌟",
        "Keep growing, stay adaptable, and believe in your potential! 🚀"
    ],
    "meditation": [
        "Start with 5 minutes daily. Focus on breathing. Let thoughts pass like clouds. 🧘",
        "Meditation calms the mind! Sit comfortably, breathe deeply, observe your thoughts. ☮️",
        "Inner peace comes with practice. Be patient with yourself. Breathe and be present. 🕉️",
        "Try guided meditation apps! Headspace or Calm are great for beginners. 🎧",
        "Mindfulness transforms life! Even a few mindful breaths can help. 🌸"
    ],
    "dreams": [
        "Dreams are fascinating windows into the subconscious mind! 🌙",
        "Dream symbols are personal to you! What emotions did you feel? 💭",
        "Recurring dreams often reflect unresolved feelings or thoughts. 😴",
        "Keep a dream journal! It helps you remember and understand patterns. 📔",
        "Dreams can be random neural activity or meaningful messages. Interpretation is personal! ✨"
    ],
    "pets": [
        "Pets bring so much joy! Dogs are loyal, cats are independent - both amazing! 🐕",
        "Animals are wonderful companions! What kind of pet do you have or want? 🐈",
        "Pet care means love, attention, and responsibility. They give unconditional love! 🐾",
        "From dogs to hamsters, each pet is unique and special! 🐇",
        "Rescue pets need homes! Adoption saves lives. 🏠"
    ],
    "cooking": [
        "Cooking is an art! Start simple - pasta, stir-fry, roasted veggies. You'll improve! 👨‍🍳",
        "Practice makes perfect! Follow recipes, experiment, and enjoy the process! 🍳",
        "Fresh ingredients, sharp knife, good heat control - cooking basics! 🔪",
        "Cooking is love made edible! What's your favorite cuisine? 🍜",
        "Don't fear mistakes! Even chefs burn things. Keep cooking! 🥘"
    ],
    "philosophy": [
        "Life's meaning is what you create! Purpose comes from within. 🤔",
        "Philosophy asks the big questions! What makes you ponder? 💭",
        "Existence, consciousness, morality - deep topics that define humanity! 🧠",
        "Ancient wisdom meets modern thought! Philosophy enriches perspective. 📖",
        "We're all philosophers when we question and wonder about life! ✨"
    ],
    "environment": [
        "Protect our planet! Reduce, reuse, recycle. Every action counts! 🌍",
        "Climate change is real! We must act now for future generations. 🌱",
        "Small changes add up! Use less plastic, save energy, support sustainability. ♻️",
        "Our Earth needs us! Be conscious of your environmental impact. 🌳",
        "Green living benefits everyone! What eco-friendly steps can you take? 🌿"
    ],
    "astronomy": [
        "Space is infinite wonder! Billions of galaxies, each with billions of stars! 🌌",
        "The universe is 13.8 billion years old and still expanding! Mind-blowing! 🔭",
        "From black holes to neutron stars, space is full of mysteries! 🌠",
        "We're made of stardust! Every atom in you was forged in a star! ⭐",
        "Space exploration pushes human boundaries! What cosmic topic interests you? 🚀"
    ],
    "art": [
        "Art is expression! From classical to modern, it captures human emotion. 🎨",
        "Creativity has no limits! What art form speaks to you? 🖼️",
        "Art reflects culture, challenges norms, inspires change. It's powerful! 🖌️",
        "From da Vinci to Banksy, artists shape how we see the world! 👁️",
        "Everyone can create! Art is about expression, not perfection. 🎭"
    ],
    "money": [
        "Save first, spend second! Pay yourself before bills. Build that emergency fund! 💰",
        "Budget wisely, invest smartly, avoid debt. Financial freedom awaits! 📊",
        "Money is a tool! Use it to create security and opportunities. 💵",
        "Live below your means, invest the difference. Compound interest is magic! 📈",
        "Financial literacy is power! Learn, save, invest, grow! 💳"
    ],
    "fashion": [
        "Fashion is self-expression! Wear what makes you feel confident! 👗",
        "Style is personal! Mix basics with statement pieces. Own your look! 👔",
        "Dress for yourself, not others! Confidence is the best accessory. 👠",
        "Fashion trends come and go, but personal style is timeless! ✨",
        "From casual to formal, fashion reflects personality! What's your style? 👕"
    ]
}
