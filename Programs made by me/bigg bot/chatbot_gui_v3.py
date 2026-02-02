"""
Neural Chatbot GUI v3 - Modern Refresh
Features: Enhanced TTS with voice selection, modern UI, web search,
speech queue, themes, timestamps, quick replies, and more!
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import threading
import queue
import numpy as np
import json
import os
from datetime import datetime

# Import chatbot components
from chatbot import NeuralChatbot, training_data, responses

# Text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not installed. Voice features disabled.")


class ModernChatbotGUI:
    """Modern GUI for the Neural Chatbot with enhanced TTS controls"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Chatbot v3")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Modern color scheme
        self.colors = {
            'bg_dark': '#0f0f1a',
            'bg_medium': '#1a1a2e',
            'bg_light': '#252542',
            'bg_card': '#2d2d4a',
            'accent_primary': '#00d9ff',
            'accent_secondary': '#ff6b9d',
            'accent_success': '#00ff9d',
            'accent_warning': '#ffb800',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0c0',
            'text_muted': '#606080',
            'user_msg': '#00d9ff',
            'bot_msg': '#00ff9d',
            'system_msg': '#ffb800',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2',
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Variables
        self.voice_enabled = tk.BooleanVar(value=False)  # Start disabled
        self.voice_speed = tk.IntVar(value=175)
        self.voice_volume = tk.DoubleVar(value=1.0)
        self.selected_voice = tk.StringVar(value="")
        self.show_timestamps = tk.BooleanVar(value=True)
        self.web_search_enabled = tk.BooleanVar(value=True)
        self.font_size = tk.IntVar(value=11)
        
        # TTS Engine and voices
        self.tts_engine = None
        self.available_voices = []
        self.current_speech_stop = False
        self.init_tts_engine()
        
        # Stats
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'session_start': datetime.now(),
            'words_typed': 0
        }
        
        # Chat history
        self.chat_history = []
        
        # Speech queue
        self.speech_queue = queue.Queue()
        self.queue_items = []
        self.queue_lock = threading.Lock()
        
        # Chatbot
        self.chatbot = None
        self.load_chatbot()
        
        # Build UI
        self.create_styles()
        self.create_main_layout()
        self.setup_keyboard_shortcuts()
        
        # Start TTS worker
        if TTS_AVAILABLE:
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
        
        # Welcome message
        self.show_welcome()
    
    def init_tts_engine(self):
        """Initialize TTS engine and get available voices"""
        if not TTS_AVAILABLE:
            return
        
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            self.available_voices = []
            
            for voice in voices:
                # Create friendly name
                name = voice.name
                if 'Microsoft' in name:
                    name = name.replace('Microsoft ', '').replace(' Desktop', '')
                self.available_voices.append({
                    'id': voice.id,
                    'name': name,
                    'languages': voice.languages,
                    'gender': 'Female' if any(x in voice.name.lower() for x in ['zira', 'hazel', 'female', 'woman']) else 'Male'
                })
            
            if self.available_voices:
                self.selected_voice.set(self.available_voices[0]['id'])
            
            self.tts_engine.stop()
            self.tts_engine = None  # Will recreate for each speech
            
        except Exception as e:
            print(f"TTS init error: {e}")
    
    def load_chatbot(self):
        """Load or create the chatbot"""
        try:
            self.chatbot = NeuralChatbot([100, 64, 32, 10], learning_rate=0.1)
            if self.chatbot.load("chatbot_model.pkl"):
                print("Loaded existing chatbot model")
            else:
                raise FileNotFoundError("No saved model")
        except (FileNotFoundError, Exception) as e:
            print("Creating new chatbot...")
            vocab_size = len(set(' '.join([' '.join(phrases) for phrases in training_data.values()]).lower().split()))
            num_intents = len(training_data)
            self.chatbot = NeuralChatbot([vocab_size + 1, 64, 32, num_intents], learning_rate=0.1)
            self.chatbot.build_vocab(training_data)
            self.chatbot.responses = responses
            self.chatbot.generator.train_from_responses(responses)
            
            X, y = self.chatbot.prepare_training_data(training_data)
            for epoch in range(500):
                self.chatbot.train(X, y, epochs=1)
            
            self.chatbot.save("chatbot_model.pkl")
    
    def create_styles(self):
        """Create custom ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Modern.TFrame', background=self.colors['bg_dark'])
        style.configure('Card.TFrame', background=self.colors['bg_card'])
        style.configure('Modern.TLabel', 
                       background=self.colors['bg_dark'], 
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['accent_primary'],
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Modern.TButton',
                       background=self.colors['accent_primary'],
                       foreground=self.colors['bg_dark'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_secondary'])])
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area (3 columns)
        content = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left sidebar - TTS Controls
        self.create_tts_panel(content)
        
        # Center - Chat area
        self.create_chat_panel(content)
        
        # Right sidebar - Quick actions & Queue
        self.create_right_panel(content)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create the header section"""
        header = tk.Frame(parent, bg=self.colors['bg_medium'], height=60)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)
        
        # Left: Logo/Title
        left_header = tk.Frame(header, bg=self.colors['bg_medium'])
        left_header.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        tk.Label(
            left_header,
            text="🤖",
            font=('Segoe UI', 24),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(side=tk.LEFT, pady=10)
        
        title_frame = tk.Frame(left_header, bg=self.colors['bg_medium'])
        title_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        bot_name = self.chatbot.bot_name if self.chatbot else "Neural Bot"
        self.title_label = tk.Label(
            title_frame,
            text=bot_name,
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary']
        )
        self.title_label.pack(anchor=tk.W, pady=(12, 0))
        
        tk.Label(
            title_frame,
            text="AI Assistant • Online",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_success']
        ).pack(anchor=tk.W)
        
        # Right: Quick toggles
        right_header = tk.Frame(header, bg=self.colors['bg_medium'])
        right_header.pack(side=tk.RIGHT, padx=20, fill=tk.Y)
        
        toggles_frame = tk.Frame(right_header, bg=self.colors['bg_medium'])
        toggles_frame.pack(pady=15)
        
        # Web search toggle
        self.web_toggle_btn = tk.Button(
            toggles_frame,
            text="🌐 Web",
            font=('Segoe UI', 9),
            bg=self.colors['accent_success'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.toggle_web_search
        )
        self.web_toggle_btn.pack(side=tk.LEFT, padx=3)
        
        # Settings button
        tk.Button(
            toggles_frame,
            text="⚙️",
            font=('Segoe UI', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=8,
            pady=2,
            command=self.open_settings
        ).pack(side=tk.LEFT, padx=3)
    
    def create_tts_panel(self, parent):
        """Create the TTS controls panel (left sidebar)"""
        tts_panel = tk.Frame(parent, bg=self.colors['bg_medium'], width=280)
        tts_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        tts_panel.pack_propagate(False)
        
        # Panel header
        header = tk.Frame(tts_panel, bg=self.colors['bg_light'])
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header,
            text="🔊 Voice Controls",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['accent_primary'],
            padx=10,
            pady=8
        ).pack(anchor=tk.W)
        
        # Voice On/Off Toggle
        toggle_frame = tk.Frame(tts_panel, bg=self.colors['bg_medium'])
        toggle_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            toggle_frame,
            text="Text-to-Speech",
            font=('Segoe UI', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary']
        ).pack(side=tk.LEFT)
        
        self.tts_toggle_btn = tk.Button(
            toggle_frame,
            text="OFF",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['text_muted'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            width=6,
            command=self.toggle_tts
        )
        self.tts_toggle_btn.pack(side=tk.RIGHT)
        
        # TTS Status indicator
        self.tts_status_label = tk.Label(
            tts_panel,
            text="🔇 Voice Disabled" if not TTS_AVAILABLE else "🔇 Voice Off",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_muted'],
            pady=5
        )
        self.tts_status_label.pack()
        
        # Divider
        tk.Frame(tts_panel, bg=self.colors['bg_light'], height=1).pack(fill=tk.X, padx=15, pady=10)
        
        # Voice Selection
        voice_frame = tk.Frame(tts_panel, bg=self.colors['bg_medium'])
        voice_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            voice_frame,
            text="Voice",
            font=('Segoe UI', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W)
        
        # Voice dropdown
        voice_names = [v['name'] for v in self.available_voices] if self.available_voices else ["No voices available"]
        self.voice_combo = ttk.Combobox(
            voice_frame,
            values=voice_names,
            state='readonly',
            font=('Segoe UI', 10),
            width=25
        )
        self.voice_combo.pack(fill=tk.X, pady=5)
        if voice_names and voice_names[0] != "No voices available":
            self.voice_combo.current(0)
        self.voice_combo.bind('<<ComboboxSelected>>', self.on_voice_change)
        
        # Speed Control
        speed_frame = tk.Frame(tts_panel, bg=self.colors['bg_medium'])
        speed_frame.pack(fill=tk.X, padx=15, pady=10)
        
        speed_header = tk.Frame(speed_frame, bg=self.colors['bg_medium'])
        speed_header.pack(fill=tk.X)
        
        tk.Label(
            speed_header,
            text="Speed",
            font=('Segoe UI', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.speed_value_label = tk.Label(
            speed_header,
            text="175 wpm",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        )
        self.speed_value_label.pack(side=tk.RIGHT)
        
        self.speed_slider = tk.Scale(
            speed_frame,
            from_=80,
            to=350,
            orient=tk.HORIZONTAL,
            variable=self.voice_speed,
            command=self.on_speed_change,
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            troughcolor=self.colors['bg_light'],
            activebackground=self.colors['accent_primary'],
            sliderrelief=tk.FLAT,
            showvalue=False,
            length=220
        )
        self.speed_slider.pack(fill=tk.X, pady=5)
        
        # Volume Control
        vol_frame = tk.Frame(tts_panel, bg=self.colors['bg_medium'])
        vol_frame.pack(fill=tk.X, padx=15, pady=10)
        
        vol_header = tk.Frame(vol_frame, bg=self.colors['bg_medium'])
        vol_header.pack(fill=tk.X)
        
        tk.Label(
            vol_header,
            text="Volume",
            font=('Segoe UI', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.volume_value_label = tk.Label(
            vol_header,
            text="100%",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        )
        self.volume_value_label.pack(side=tk.RIGHT)
        
        self.volume_slider = tk.Scale(
            vol_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.on_volume_change,
            bg=self.colors['bg_medium'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            troughcolor=self.colors['bg_light'],
            activebackground=self.colors['accent_primary'],
            sliderrelief=tk.FLAT,
            showvalue=False,
            length=220
        )
        self.volume_slider.set(100)
        self.volume_slider.pack(fill=tk.X, pady=5)
        
        # Divider
        tk.Frame(tts_panel, bg=self.colors['bg_light'], height=1).pack(fill=tk.X, padx=15, pady=10)
        
        # Test Voice Button
        test_frame = tk.Frame(tts_panel, bg=self.colors['bg_medium'])
        test_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Button(
            test_frame,
            text="🎤 Test Voice",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.test_voice
        ).pack(fill=tk.X)
        
        # Current Speech Display
        tk.Frame(tts_panel, bg=self.colors['bg_light'], height=1).pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            tts_panel,
            text="🎙️ Now Speaking",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_warning']
        ).pack(anchor=tk.W, padx=15)
        
        self.now_speaking_label = tk.Label(
            tts_panel,
            text="(Nothing)",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            wraplength=240,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        self.now_speaking_label.pack(fill=tk.X, padx=15, pady=5)
        
        # Skip button
        tk.Button(
            tts_panel,
            text="⏭️ Skip",
            font=('Segoe UI', 9),
            bg=self.colors['accent_warning'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.skip_speech
        ).pack(pady=10)
    
    def create_chat_panel(self, parent):
        """Create the main chat panel (center)"""
        chat_panel = tk.Frame(parent, bg=self.colors['bg_medium'])
        chat_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Chat display
        chat_frame = tk.Frame(chat_panel, bg=self.colors['bg_dark'])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground=self.colors['accent_primary'],
            selectforeground=self.colors['bg_dark']
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags
        self.chat_display.tag_config("user", foreground=self.colors['user_msg'], font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config("bot", foreground=self.colors['bot_msg'], font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config("system", foreground=self.colors['system_msg'], font=('Segoe UI', 10, 'italic'))
        self.chat_display.tag_config("timestamp", foreground=self.colors['text_muted'], font=('Segoe UI', 9))
        
        # Input area
        input_frame = tk.Frame(chat_panel, bg=self.colors['bg_medium'])
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Input container with rounded appearance
        input_container = tk.Frame(input_frame, bg=self.colors['bg_light'])
        input_container.pack(fill=tk.X)
        
        self.input_field = tk.Entry(
            input_container,
            font=('Segoe UI', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=12, padx=15)
        self.input_field.bind("<Return>", lambda e: self.send_message())
        self.input_field.focus()
        
        # Send button
        tk.Button(
            input_container,
            text="Send ➤",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_dark'],
            activebackground=self.colors['accent_secondary'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.send_message
        ).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Quick replies
        quick_frame = tk.Frame(chat_panel, bg=self.colors['bg_medium'])
        quick_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            quick_frame,
            text="Quick:",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_muted']
        ).pack(side=tk.LEFT, padx=5)
        
        quick_buttons = ["Hello!", "Thanks!", "Help", "search help", "🔍 search:"]
        for text in quick_buttons:
            btn = tk.Button(
                quick_frame,
                text=text,
                font=('Segoe UI', 9),
                bg=self.colors['bg_light'],
                fg=self.colors['text_secondary'],
                activebackground=self.colors['accent_primary'],
                activeforeground=self.colors['bg_dark'],
                relief=tk.FLAT,
                padx=10,
                pady=4,
                command=lambda t=text: self.quick_reply(t)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Typing indicator
        self.typing_label = tk.Label(
            chat_panel,
            text="",
            font=('Segoe UI', 9, 'italic'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_muted']
        )
        self.typing_label.pack(anchor=tk.W, padx=15)
    
    def create_right_panel(self, parent):
        """Create the right sidebar with actions and queue"""
        right_panel = tk.Frame(parent, bg=self.colors['bg_medium'], width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Actions section
        actions_header = tk.Frame(right_panel, bg=self.colors['bg_light'])
        actions_header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            actions_header,
            text="⚡ Actions",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['accent_secondary'],
            padx=10,
            pady=8
        ).pack(anchor=tk.W)
        
        # Action buttons
        actions = [
            ("🗑️ Clear Chat", self.clear_chat),
            ("💾 Save Chat", self.save_chat),
            ("📊 Statistics", self.show_statistics),
            ("🎓 Train Bot", self.open_training),
            ("📋 View Intents", self.view_intents),
            ("🌐 Web Search", self.manual_web_search),
        ]
        
        for text, cmd in actions:
            tk.Button(
                right_panel,
                text=text,
                font=('Segoe UI', 10),
                bg=self.colors['bg_light'],
                fg=self.colors['text_primary'],
                activebackground=self.colors['accent_primary'],
                activeforeground=self.colors['bg_dark'],
                relief=tk.FLAT,
                anchor=tk.W,
                padx=15,
                pady=8,
                command=cmd
            ).pack(fill=tk.X, padx=10, pady=2)
        
        # Speech Queue section
        tk.Frame(right_panel, bg=self.colors['bg_light'], height=1).pack(fill=tk.X, padx=10, pady=15)
        
        queue_header = tk.Frame(right_panel, bg=self.colors['bg_medium'])
        queue_header.pack(fill=tk.X, padx=10)
        
        tk.Label(
            queue_header,
            text="📋 Speech Queue",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(side=tk.LEFT)
        
        self.queue_count_label = tk.Label(
            queue_header,
            text="(0)",
            font=('Segoe UI', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_muted']
        )
        self.queue_count_label.pack(side=tk.RIGHT)
        
        # Queue listbox
        self.queue_listbox = tk.Listbox(
            right_panel,
            font=('Consolas', 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_secondary'],
            selectbackground=self.colors['accent_primary'],
            selectforeground=self.colors['bg_dark'],
            relief=tk.FLAT,
            height=8,
            activestyle='none'
        )
        self.queue_listbox.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear queue button
        tk.Button(
            right_panel,
            text="🧹 Clear Queue",
            font=('Segoe UI', 9),
            bg=self.colors['accent_warning'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.clear_speech_queue
        ).pack(pady=5)
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_light'], height=30)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready • Type a message to start chatting")
        
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_muted'],
            padx=15
        ).pack(side=tk.LEFT, fill=tk.Y)
        
        # TTS indicator
        self.tts_indicator = tk.Label(
            status_frame,
            text="🔇 TTS Off",
            font=('Segoe UI', 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_muted'],
            padx=15
        )
        self.tts_indicator.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-Return>', lambda e: self.send_message())
        self.root.bind('<Control-l>', lambda e: self.clear_chat())
        self.root.bind('<Control-s>', lambda e: self.save_chat())
        self.root.bind('<F1>', lambda e: self.show_help())
    
    # ==================== TTS Methods ====================
    
    def toggle_tts(self):
        """Toggle TTS on/off"""
        if not TTS_AVAILABLE:
            messagebox.showwarning("TTS Unavailable", "Text-to-speech is not available.\nInstall pyttsx3: pip install pyttsx3")
            return
        
        self.voice_enabled.set(not self.voice_enabled.get())
        
        if self.voice_enabled.get():
            self.tts_toggle_btn.config(text="ON", bg=self.colors['accent_success'])
            self.tts_status_label.config(text="🔊 Voice Enabled", fg=self.colors['accent_success'])
            self.tts_indicator.config(text="🔊 TTS On", fg=self.colors['accent_success'])
        else:
            self.tts_toggle_btn.config(text="OFF", bg=self.colors['text_muted'])
            self.tts_status_label.config(text="🔇 Voice Off", fg=self.colors['text_muted'])
            self.tts_indicator.config(text="🔇 TTS Off", fg=self.colors['text_muted'])
    
    def on_voice_change(self, event=None):
        """Handle voice selection change"""
        selection_idx = self.voice_combo.current()
        if selection_idx >= 0 and selection_idx < len(self.available_voices):
            voice = self.available_voices[selection_idx]
            self.selected_voice.set(voice['id'])
    
    def on_speed_change(self, val):
        """Handle speed slider change"""
        speed = int(float(val))
        self.voice_speed.set(speed)
        self.speed_value_label.config(text=f"{speed} wpm")
    
    def on_volume_change(self, val):
        """Handle volume slider change"""
        volume = int(float(val))
        self.voice_volume.set(volume / 100.0)
        self.volume_value_label.config(text=f"{volume}%")
    
    def test_voice(self):
        """Test the current voice settings"""
        if not TTS_AVAILABLE:
            messagebox.showwarning("TTS Unavailable", "Text-to-speech is not available.")
            return
        
        # Get current voice name
        voice_idx = self.voice_combo.current()
        voice_name = self.available_voices[voice_idx]['name'] if voice_idx >= 0 and self.available_voices else "default"
        
        test_text = f"Hello! This is a test of the {voice_name} voice at {self.voice_speed.get()} words per minute."
        
        # Speak in background
        threading.Thread(target=self._speak_text, args=(test_text,), daemon=True).start()
        self.status_var.set("Testing voice...")
    
    def _speak_text(self, text):
        """Speak text using current settings (runs in background)"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_speed.get())
            engine.setProperty('volume', self.voice_volume.get())
            
            if self.selected_voice.get():
                engine.setProperty('voice', self.selected_voice.get())
            
            # Update UI
            self.root.after(0, lambda: self.now_speaking_label.config(
                text=text[:80] + "..." if len(text) > 80 else text
            ))
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
            self.root.after(0, lambda: self.now_speaking_label.config(text="(Nothing)"))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"TTS Error: {e}"))
    
    def skip_speech(self):
        """Request to skip current speech"""
        self.current_speech_stop = True
        self.add_message("System", "Skip requested - will take effect after current word")
    
    def clear_speech_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        with self.queue_lock:
            self.queue_items.clear()
        
        self.update_queue_display()
        self.add_message("System", "Speech queue cleared")
    
    def _speech_worker(self):
        """Background worker for processing speech queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:
                    break
                
                # Update display
                self.root.after(0, lambda t=text: self.now_speaking_label.config(
                    text=t[:80] + "..." if len(t) > 80 else t
                ))
                
                # Remove from tracking
                with self.queue_lock:
                    if text in self.queue_items:
                        self.queue_items.remove(text)
                
                self.root.after(0, self.update_queue_display)
                
                # Speak
                engine = pyttsx3.init()
                engine.setProperty('rate', self.voice_speed.get())
                engine.setProperty('volume', self.voice_volume.get())
                
                if self.selected_voice.get():
                    engine.setProperty('voice', self.selected_voice.get())
                
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                
                self.root.after(0, lambda: self.now_speaking_label.config(text="(Nothing)"))
                
            except Exception as e:
                print(f"TTS Worker Error: {e}")
    
    def update_queue_display(self):
        """Update the queue display"""
        with self.queue_lock:
            count = len(self.queue_items)
            self.queue_count_label.config(text=f"({count})")
            
            self.queue_listbox.delete(0, tk.END)
            for i, item in enumerate(self.queue_items):
                display = item[:30] + "..." if len(item) > 30 else item
                self.queue_listbox.insert(tk.END, f"{i+1}. {display}")
    
    # ==================== Chat Methods ====================
    
    def add_message(self, sender, message, speak=False):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        if self.show_timestamps.get():
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Sender
        if sender == "User":
            self.chat_display.insert(tk.END, "You: ", "user")
            self.stats['messages_sent'] += 1
        elif sender == "Bot":
            bot_name = self.chatbot.bot_name if self.chatbot else "Bot"
            self.chat_display.insert(tk.END, f"{bot_name}: ", "bot")
            self.stats['messages_received'] += 1
        else:
            self.chat_display.insert(tk.END, f"⚡ ", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # History
        self.chat_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
        
        # Speak bot messages if TTS enabled
        if speak and self.voice_enabled.get() and sender == "Bot":
            with self.queue_lock:
                self.queue_items.append(message)
            self.root.after(0, self.update_queue_display)
            self.speech_queue.put(message)
    
    def send_message(self):
        """Send user message"""
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        self.stats['words_typed'] += len(user_input.split())
        self.input_field.delete(0, tk.END)
        
        self.add_message("User", user_input)
        self.show_typing()
        self.status_var.set("Thinking...")
        
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        """Process message and get response"""
        try:
            response = self.chatbot.get_response(user_input)
            
            self.root.after(0, self.hide_typing)
            self.root.after(0, lambda: self.add_message("Bot", response, speak=True))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, self.update_title)
            
        except Exception as e:
            self.root.after(0, self.hide_typing)
            self.root.after(0, lambda: self.add_message("System", f"Error: {e}"))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
    
    def quick_reply(self, text):
        """Handle quick reply button"""
        if text == "🔍 search:":
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, "search: ")
            self.input_field.focus()
        else:
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, text)
            self.send_message()
    
    def show_typing(self):
        """Show typing indicator"""
        bot_name = self.chatbot.bot_name if self.chatbot else "Bot"
        self.typing_label.config(text=f"{bot_name} is typing...")
    
    def hide_typing(self):
        """Hide typing indicator"""
        self.typing_label.config(text="")
    
    def update_title(self):
        """Update window title"""
        bot_name = self.chatbot.bot_name if self.chatbot else "Neural Bot"
        self.root.title(f"{bot_name} - AI Assistant v3")
        self.title_label.config(text=bot_name)
    
    def show_welcome(self):
        """Show welcome message"""
        bot_name = self.chatbot.bot_name if self.chatbot else "Neural Bot"
        welcome = f"""Welcome! I'm {bot_name}, your AI assistant.

💡 **Quick Tips:**
• Type `search: topic` to search the web
• Type `search help` for all search commands
• Use the Voice Controls panel to enable TTS
• Click Quick buttons below for common actions

How can I help you today?"""
        self.add_message("Bot", welcome)
    
    # ==================== Action Methods ====================
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history.clear()
        self.add_message("System", "Chat cleared")
    
    def save_chat(self):
        """Save chat to file"""
        if not self.chat_history:
            messagebox.showwarning("No Data", "No chat history to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json")],
            initialfile=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.chat_history, f, indent=2)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for msg in self.chat_history:
                            f.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}\n\n")
                
                messagebox.showinfo("Saved", f"Chat saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def show_statistics(self):
        """Show statistics dialog"""
        stats_win = tk.Toplevel(self.root)
        stats_win.title("📊 Statistics")
        stats_win.geometry("400x350")
        stats_win.configure(bg=self.colors['bg_medium'])
        
        tk.Label(
            stats_win,
            text="📊 Session Statistics",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(pady=15)
        
        # Calculate duration
        duration = datetime.now() - self.stats['session_start']
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_data = [
            ("📤 Messages Sent", self.stats['messages_sent']),
            ("📥 Messages Received", self.stats['messages_received']),
            ("📝 Words Typed", self.stats['words_typed']),
            ("⏱️ Session Duration", f"{hours}h {minutes}m {seconds}s"),
            ("🎯 Total Intents", len(training_data)),
            ("📚 Vocabulary Size", len(self.chatbot.vocab) if self.chatbot else 0),
            ("🔊 TTS Enabled", "Yes" if self.voice_enabled.get() else "No"),
        ]
        
        frame = tk.Frame(stats_win, bg=self.colors['bg_card'], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for label, value in stats_data:
            row = tk.Frame(frame, bg=self.colors['bg_card'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=label, font=('Segoe UI', 11),
                    bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
            tk.Label(row, text=str(value), font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['bg_card'], fg=self.colors['accent_success']).pack(side=tk.RIGHT)
    
    def open_training(self):
        """Open training dialog"""
        train_win = tk.Toplevel(self.root)
        train_win.title("🎓 Train Bot")
        train_win.geometry("500x400")
        train_win.configure(bg=self.colors['bg_medium'])
        
        tk.Label(
            train_win,
            text="🎓 Add Training Data",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(pady=15)
        
        # Intent
        tk.Label(train_win, text="Intent:", font=('Segoe UI', 10),
                bg=self.colors['bg_medium'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=30)
        intent_entry = tk.Entry(train_win, font=('Segoe UI', 11),
                               bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                               insertbackground=self.colors['accent_primary'], width=50)
        intent_entry.pack(padx=30, pady=5)
        
        # Pattern
        tk.Label(train_win, text="Pattern (user input):", font=('Segoe UI', 10),
                bg=self.colors['bg_medium'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=30)
        pattern_entry = tk.Entry(train_win, font=('Segoe UI', 11),
                                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                insertbackground=self.colors['accent_primary'], width=50)
        pattern_entry.pack(padx=30, pady=5)
        
        # Response
        tk.Label(train_win, text="Response:", font=('Segoe UI', 10),
                bg=self.colors['bg_medium'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=30)
        response_text = tk.Text(train_win, font=('Segoe UI', 11),
                               bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                               insertbackground=self.colors['accent_primary'], width=50, height=5)
        response_text.pack(padx=30, pady=5)
        
        def train():
            intent = intent_entry.get().strip()
            pattern = pattern_entry.get().strip()
            response = response_text.get(1.0, tk.END).strip()
            
            if not all([intent, pattern, response]):
                messagebox.showwarning("Missing Data", "Please fill all fields!")
                return
            
            if intent not in training_data:
                training_data[intent] = []
            training_data[intent].append(pattern)
            
            if intent not in responses:
                responses[intent] = []
            responses[intent].append(response)
            
            self.add_message("System", f"Training with new intent: {intent}...")
            train_win.destroy()
            
            # Retrain in background
            threading.Thread(target=self.retrain_model, daemon=True).start()
        
        tk.Button(
            train_win,
            text="Train Bot",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent_success'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=train
        ).pack(pady=20)
    
    def retrain_model(self):
        """Retrain the model"""
        try:
            self.chatbot.build_vocab(training_data)
            self.chatbot.responses = responses
            self.chatbot.generator.train_from_responses(responses)
            
            X, y = self.chatbot.prepare_training_data(training_data)
            for _ in range(500):
                self.chatbot.train(X, y, epochs=1)
            
            self.chatbot.save("chatbot_model.pkl")
            self.root.after(0, lambda: self.add_message("System", "✅ Training complete!"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("System", f"❌ Training failed: {e}"))
    
    def view_intents(self):
        """View all intents"""
        intents_win = tk.Toplevel(self.root)
        intents_win.title("📋 Intents")
        intents_win.geometry("600x500")
        intents_win.configure(bg=self.colors['bg_medium'])
        
        tk.Label(
            intents_win,
            text="📋 Current Intents",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(pady=15)
        
        text_area = scrolledtext.ScrolledText(
            intents_win,
            font=('Consolas', 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            wrap=tk.WORD
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        for intent, patterns in training_data.items():
            text_area.insert(tk.END, f"\n{'═'*50}\n")
            text_area.insert(tk.END, f"📌 {intent.upper()}\n")
            text_area.insert(tk.END, f"{'═'*50}\n")
            text_area.insert(tk.END, f"Patterns ({len(patterns)}):\n")
            for i, p in enumerate(patterns[:5], 1):
                text_area.insert(tk.END, f"  {i}. {p}\n")
            if len(patterns) > 5:
                text_area.insert(tk.END, f"  ... and {len(patterns)-5} more\n")
        
        text_area.config(state=tk.DISABLED)
    
    def manual_web_search(self):
        """Open manual web search dialog"""
        search_win = tk.Toplevel(self.root)
        search_win.title("🌐 Web Search")
        search_win.geometry("500x400")
        search_win.configure(bg=self.colors['bg_medium'])
        
        tk.Label(
            search_win,
            text="🌐 Search the Web",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(pady=15)
        
        # Search input
        input_frame = tk.Frame(search_win, bg=self.colors['bg_medium'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary']
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        search_entry.focus()
        
        # Result area
        result_text = scrolledtext.ScrolledText(
            search_win,
            font=('Segoe UI', 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            wrap=tk.WORD,
            height=12
        )
        result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def do_search():
            query = search_entry.get().strip()
            if not query:
                return
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "🔍 Searching...\n")
            result_text.config(state=tk.DISABLED)
            search_win.update()
            
            try:
                from web_search import WebSearch
                ws = WebSearch()
                result = ws.search(query)
                
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                
                if result:
                    result_text.insert(tk.END, f"📖 {result.get('title', 'Result')}\n\n")
                    result_text.insert(tk.END, result['answer'])
                    if result.get('url'):
                        result_text.insert(tk.END, f"\n\n🔗 {result['url']}")
                else:
                    result_text.insert(tk.END, "❌ No results found.")
                
                result_text.config(state=tk.DISABLED)
            except Exception as e:
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"❌ Error: {e}")
                result_text.config(state=tk.DISABLED)
        
        def use_result():
            content = result_text.get(1.0, tk.END).strip()
            if content and not content.startswith("🔍") and not content.startswith("❌"):
                self.add_message("Bot", content)
            search_win.destroy()
        
        tk.Button(
            input_frame,
            text="🔍 Search",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=15,
            command=do_search
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        search_entry.bind("<Return>", lambda e: do_search())
        
        tk.Button(
            search_win,
            text="📋 Use in Chat",
            font=('Segoe UI', 10),
            bg=self.colors['accent_success'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=use_result
        ).pack(pady=10)
    
    def toggle_web_search(self):
        """Toggle web search"""
        self.web_search_enabled.set(not self.web_search_enabled.get())
        
        if self.web_search_enabled.get():
            self.web_toggle_btn.config(bg=self.colors['accent_success'], text="🌐 Web")
            if self.chatbot and hasattr(self.chatbot, 'fallback'):
                self.chatbot.fallback.toggle_web_search(True)
        else:
            self.web_toggle_btn.config(bg=self.colors['text_muted'], text="🌐 Off")
            if self.chatbot and hasattr(self.chatbot, 'fallback'):
                self.chatbot.fallback.toggle_web_search(False)
    
    def open_settings(self):
        """Open settings dialog"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("⚙️ Settings")
        settings_win.geometry("450x450")
        settings_win.configure(bg=self.colors['bg_medium'])
        
        tk.Label(
            settings_win,
            text="⚙️ Settings",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent_primary']
        ).pack(pady=15)
        
        # Timestamps toggle
        ts_frame = tk.Frame(settings_win, bg=self.colors['bg_medium'])
        ts_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(ts_frame, text="Show Timestamps", font=('Segoe UI', 11),
                bg=self.colors['bg_medium'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        tk.Checkbutton(
            ts_frame,
            variable=self.show_timestamps,
            bg=self.colors['bg_medium'],
            activebackground=self.colors['bg_medium'],
            selectcolor=self.colors['bg_light']
        ).pack(side=tk.RIGHT)
        
        # Web search toggle
        ws_frame = tk.Frame(settings_win, bg=self.colors['bg_medium'])
        ws_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(ws_frame, text="Enable Web Search", font=('Segoe UI', 11),
                bg=self.colors['bg_medium'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        tk.Checkbutton(
            ws_frame,
            variable=self.web_search_enabled,
            bg=self.colors['bg_medium'],
            activebackground=self.colors['bg_medium'],
            selectcolor=self.colors['bg_light']
        ).pack(side=tk.RIGHT)
        
        # API Key section
        api_frame = tk.Frame(settings_win, bg=self.colors['bg_medium'])
        api_frame.pack(fill=tk.X, padx=30, pady=15)
        
        tk.Label(
            api_frame, 
            text="🔑 OpenAI API Key", 
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg_medium'], 
            fg=self.colors['accent_warning']
        ).pack(anchor=tk.W)
        
        tk.Label(
            api_frame, 
            text="For AI-enhanced responses when online", 
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'], 
            fg=self.colors['text_muted']
        ).pack(anchor=tk.W)
        
        api_entry_frame = tk.Frame(api_frame, bg=self.colors['bg_medium'])
        api_entry_frame.pack(fill=tk.X, pady=5)
        
        self.api_key_var = tk.StringVar()
        # Load existing API key if available
        if self.chatbot and self.chatbot.api_learning and self.chatbot.api_learning.api_key:
            self.api_key_var.set("••••••••" + self.chatbot.api_learning.api_key[-4:])
        elif os.environ.get("OPENAI_API_KEY"):
            key = os.environ.get("OPENAI_API_KEY")
            self.api_key_var.set("••••••••" + key[-4:])
        
        api_entry = tk.Entry(
            api_entry_frame,
            textvariable=self.api_key_var,
            font=('Segoe UI', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief=tk.FLAT,
            width=30
        )
        api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        def save_api_key():
            key = self.api_key_var.get().strip()
            if key and not key.startswith("••••"):
                if self.chatbot:
                    self.chatbot.setup_api_learning(api_key=key)
                    if self.chatbot.api_learning and self.chatbot.api_learning.is_enabled:
                        messagebox.showinfo("Success", "✅ API key saved and enabled!")
                        self.api_key_var.set("••••••••" + key[-4:])
                        # Save to environment for persistence
                        os.environ["OPENAI_API_KEY"] = key
                    else:
                        messagebox.showerror("Error", "❌ Invalid API key or OpenAI not installed")
            elif not key:
                messagebox.showwarning("Warning", "Please enter an API key")
        
        tk.Button(
            api_entry_frame,
            text="Save",
            font=('Segoe UI', 9),
            bg=self.colors['accent_success'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=10,
            command=save_api_key
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # API status indicator
        api_status_frame = tk.Frame(api_frame, bg=self.colors['bg_medium'])
        api_status_frame.pack(fill=tk.X, pady=5)
        
        status_text = "❌ Not configured"
        status_color = self.colors['text_muted']
        if self.chatbot and self.chatbot.api_learning:
            status = self.chatbot.api_learning.get_status()
            if status.get('enabled'):
                if status.get('online'):
                    status_text = "🟢 Enabled & Online"
                    status_color = self.colors['accent_success']
                else:
                    status_text = "🟡 Enabled (Offline)"
                    status_color = self.colors['accent_warning']
        
        tk.Label(
            api_status_frame,
            text=f"Status: {status_text}",
            font=('Segoe UI', 9),
            bg=self.colors['bg_medium'],
            fg=status_color
        ).pack(anchor=tk.W)
        
        tk.Button(
            settings_win,
            text="Close",
            font=('Segoe UI', 11),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_dark'],
            relief=tk.FLAT,
            padx=30,
            pady=8,
            command=settings_win.destroy
        ).pack(pady=20)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """🤖 Neural Chatbot v3 - Help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎤 VOICE CONTROLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Toggle TTS on/off with the button
• Select different voices from dropdown
• Adjust speed (80-350 wpm)
• Adjust volume (0-100%)
• Test voice before chatting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 WEB SEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type in chat:
• search: <topic>
• wiki: <topic>
• ddg: <topic>
• search help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⌨️ SHORTCUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ctrl+Enter: Send message
• Ctrl+L: Clear chat
• Ctrl+S: Save chat
• F1: This help
"""
        messagebox.showinfo("Help", help_text)
    
    def on_closing(self):
        """Handle window close"""
        if self.chatbot:
            self.chatbot.save("chatbot_model.pkl")
        self.speech_queue.put(None)  # Stop speech worker
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ModernChatbotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
