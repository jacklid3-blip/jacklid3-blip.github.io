"""
Enhanced Neural Chatbot GUI v2
Features: Speech queue display, themes, timestamps, voice controls,
quick replies, search, statistics, export options, and more!
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


class ChatbotGUIv2:
    """Enhanced GUI for the Neural Chatbot with speech queue display"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Chatbot v2 - Enhanced")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        self.root.configure(bg="#1a1a1a")
        
        # Variables
        self.voice_enabled = tk.BooleanVar(value=TTS_AVAILABLE)
        self.chatbot = None
        self.dark_mode = tk.BooleanVar(value=True)
        self.show_timestamps = tk.BooleanVar(value=True)
        self.voice_speed = tk.IntVar(value=175)
        self.font_size = tk.IntVar(value=11)
        self.typing_indicator_active = False
        self.web_search_enabled = tk.BooleanVar(value=True)  # Web search toggle
        
        # Theme colors
        self.themes = {
            'dark': {
                'bg': '#1a1a1a',
                'fg': '#ffffff',
                'accent': '#00ff88',
                'secondary': '#2b2b2b',
                'user': '#00bbff',
                'bot': '#00ff88',
                'system': '#ffaa00'
            },
            'light': {
                'bg': '#f5f5f5',
                'fg': '#333333',
                'accent': '#007acc',
                'secondary': '#ffffff',
                'user': '#0066cc',
                'bot': '#008844',
                'system': '#cc6600'
            }
        }
        self.current_theme = self.themes['dark']
        
        # Conversation stats
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'session_start': datetime.now(),
            'words_typed': 0
        }
        
        # Chat history for search
        self.chat_history = []
        
        # Search panel reference
        self.search_frame = None
        
        # Speech queue
        self.speech_queue = queue.Queue()
        self.queue_items = []  # Track items for display
        self.queue_lock = threading.Lock()
        
        # Load chatbot
        self.load_chatbot()
        
        # Create GUI
        self.create_menu()
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        
        # Start speech worker thread
        if TTS_AVAILABLE:
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
        
        # Auto-save timer (every 5 minutes)
        self.auto_save_interval()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-Return>', lambda e: self.send_message())
        self.root.bind('<Control-l>', lambda e: self.clear_chat())
        self.root.bind('<Control-s>', lambda e: self.save_chat())
        self.root.bind('<Control-f>', lambda e: self.open_search())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Escape>', lambda e: self.close_search())
        self.root.bind('<F1>', lambda e: self.show_shortcuts_help())
    
    def auto_save_interval(self):
        """Auto-save chat every 5 minutes"""
        self.auto_save_chat()
        self.root.after(300000, self.auto_save_interval)  # 5 minutes
    
    def auto_save_chat(self):
        """Silently auto-save chat"""
        try:
            if self.chat_history:
                with open('chat_autosave.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'history': self.chat_history,
                        'stats': {
                            'messages_sent': self.stats['messages_sent'],
                            'messages_received': self.stats['messages_received'],
                            'words_typed': self.stats['words_typed'],
                            'session_start': self.stats['session_start'].isoformat()
                        }
                    }, f, indent=2)
        except:
            pass  # Silent fail for auto-save
    
    def load_chatbot(self):
        """Load or create the chatbot"""
        try:
            # Create instance and try to load saved model
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
            print("Created and trained new chatbot")
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root, bg="#2b2b2b", fg="#ffffff")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="💾 Save Chat", command=self.save_chat)
        file_menu.add_command(label="🗑️ Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Training menu
        train_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="Training", menu=train_menu)
        train_menu.add_command(label="➕ Add Training Data", command=self.train_bot)
        train_menu.add_command(label="📋 View Intents", command=self.view_intents)
        train_menu.add_separator()
        train_menu.add_command(label="📊 Test Accuracy", command=self.test_accuracy)
        train_menu.add_command(label="📈 Increase Accuracy", command=self.increase_accuracy)
        train_menu.add_command(label="🔄 Retrain from Scratch", command=self.retrain_from_scratch)
        
        # Learning menu (NEW!)
        learn_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="Learning", menu=learn_menu)
        learn_menu.add_command(label="📚 Teach Bot New Response", command=self.open_teach_dialog)
        learn_menu.add_command(label="🧠 View Learned Responses", command=self.view_learned_responses)
        learn_menu.add_command(label="📊 Learning Statistics", command=self.show_learning_stats)
        learn_menu.add_separator()
        learn_menu.add_command(label="💾 Save All Learning Data", command=self.save_learning_data)
        learn_menu.add_command(label="🗑️ Clear Learned Data", command=self.clear_learned_data)
        
        # Web Search menu (NEW!)
        web_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="🌐 Web", menu=web_menu)
        web_menu.add_checkbutton(label="🔍 Enable Web Search", variable=self.web_search_enabled, command=self.toggle_web_search)
        web_menu.add_separator()
        web_menu.add_command(label="🌐 Search Wikipedia...", command=self.open_wikipedia_search)
        web_menu.add_command(label="🔎 Search DuckDuckGo...", command=self.open_duckduckgo_search)
        web_menu.add_separator()
        web_menu.add_command(label="ℹ️ Web Search Status", command=self.show_web_search_status)
        
        # Voice menu
        voice_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="Voice", menu=voice_menu)
        voice_menu.add_checkbutton(label="🔊 Enable Voice", variable=self.voice_enabled)
        voice_menu.add_command(label="🧹 Clear Speech Queue", command=self.clear_speech_queue)
        voice_menu.add_command(label="⏭️ Skip Current Speech", command=self.skip_current_speech)
        voice_menu.add_separator()
        voice_menu.add_command(label="🎚️ Voice Settings", command=self.open_voice_settings)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="🌙 Dark Mode", variable=self.dark_mode, command=self.toggle_theme)
        view_menu.add_checkbutton(label="🕐 Show Timestamps", variable=self.show_timestamps)
        view_menu.add_separator()
        view_menu.add_command(label="🔍 Search Chat (Ctrl+F)", command=self.open_search)
        view_menu.add_command(label="📊 Statistics", command=self.show_statistics)
        view_menu.add_separator()
        view_menu.add_command(label="🔼 Increase Font", command=lambda: self.change_font_size(1))
        view_menu.add_command(label="🔽 Decrease Font", command=lambda: self.change_font_size(-1))
        
        # Export menu
        export_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="📄 Export as TXT", command=lambda: self.export_chat('txt'))
        export_menu.add_command(label="📋 Export as JSON", command=lambda: self.export_chat('json'))
        export_menu.add_command(label="🌐 Export as HTML", command=lambda: self.export_chat('html'))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="⌨️ Keyboard Shortcuts (F1)", command=self.show_shortcuts_help)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Title bar
        title_frame = tk.Frame(self.root, bg="#1a1a1a", pady=10)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 Neural Chatbot v2",
            font=("Arial", 20, "bold"),
            bg="#1a1a1a",
            fg="#00ff88"
        )
        title_label.pack()
        
        # Main content area (horizontal split)
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Chat area (takes most space)
        left_panel = tk.Frame(main_frame, bg="#2b2b2b")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Control panel at top of left panel
        control_frame = tk.Frame(left_panel, bg="#2b2b2b", pady=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice toggle
        voice_check = tk.Checkbutton(
            control_frame,
            text="🔊 Voice Enabled",
            variable=self.voice_enabled,
            font=("Arial", 10),
            bg="#2b2b2b",
            fg="#ffffff",
            selectcolor="#1a1a1a",
            activebackground="#2b2b2b",
            activeforeground="#00ff88"
        )
        voice_check.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            control_frame,
            text="🗑️ Clear Chat",
            command=self.clear_chat,
            font=("Arial", 10),
            bg="#ff4444",
            fg="#ffffff",
            activebackground="#cc0000",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Chat display area
        chat_frame = tk.Frame(left_panel, bg="#2b2b2b")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#00ff88",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags for styling
        self.chat_display.tag_config("user", foreground="#00bbff", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("bot", foreground="#00ff88", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("system", foreground="#ffaa00", font=("Consolas", 10, "italic"))
        
        # Input area
        input_frame = tk.Frame(left_panel, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_field = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#00ff88",
            relief=tk.FLAT,
            bd=0
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())
        self.input_field.focus()
        
        # Send button
        send_btn = tk.Button(
            input_frame,
            text="Send ➤",
            command=self.send_message,
            font=("Arial", 11, "bold"),
            bg="#00ff88",
            fg="#000000",
            activebackground="#00cc66",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        send_btn.pack(side=tk.RIGHT)
        
        # Quick Reply Buttons
        quick_reply_frame = tk.Frame(left_panel, bg="#2b2b2b")
        quick_reply_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(
            quick_reply_frame,
            text="Quick:",
            font=("Arial", 9),
            bg="#2b2b2b",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=2)
        
        quick_replies = ["Hello!", "Thanks!", "Help", "Goodbye", "Tell me a joke", "🔍 search:"]
        for reply in quick_replies:
            btn = tk.Button(
                quick_reply_frame,
                text=reply,
                command=lambda r=reply: self.send_quick_reply(r),
                font=("Arial", 8),
                bg="#3a3a3a",
                fg="#ffffff",
                activebackground="#4a4a4a",
                relief=tk.FLAT,
                padx=8,
                pady=3
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Typing indicator (hidden by default)
        self.typing_label = tk.Label(
            left_panel,
            text="",
            font=("Arial", 9, "italic"),
            bg="#2b2b2b",
            fg="#888888"
        )
        self.typing_label.pack(anchor=tk.W, padx=10)
        
        # Right panel - Speech Queue Display
        right_panel = tk.Frame(main_frame, bg="#2b2b2b", width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)  # Fixed width
        
        # Queue header
        queue_header = tk.Frame(right_panel, bg="#333333")
        queue_header.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            queue_header,
            text="🔊 Speech Queue",
            font=("Arial", 12, "bold"),
            bg="#333333",
            fg="#00ff88"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.queue_count_label = tk.Label(
            queue_header,
            text="(0)",
            font=("Arial", 10),
            bg="#333333",
            fg="#888888"
        )
        self.queue_count_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Currently speaking indicator
        self.speaking_frame = tk.Frame(right_panel, bg="#2b2b2b")
        self.speaking_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            self.speaking_frame,
            text="🎙️ Now Speaking:",
            font=("Arial", 9, "bold"),
            bg="#2b2b2b",
            fg="#ffaa00"
        ).pack(anchor=tk.W)
        
        self.current_speech_label = tk.Label(
            self.speaking_frame,
            text="(Nothing)",
            font=("Arial", 9),
            bg="#1a1a1a",
            fg="#ffffff",
            wraplength=220,
            justify=tk.LEFT,
            padx=5,
            pady=5
        )
        self.current_speech_label.pack(fill=tk.X, pady=2)
        
        # Queue list
        queue_list_frame = tk.Frame(right_panel, bg="#2b2b2b")
        queue_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(
            queue_list_frame,
            text="📋 Pending:",
            font=("Arial", 9, "bold"),
            bg="#2b2b2b",
            fg="#00bbff"
        ).pack(anchor=tk.W)
        
        # Listbox for queue items
        self.queue_listbox = tk.Listbox(
            queue_list_frame,
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#ffffff",
            selectbackground="#00ff88",
            selectforeground="#000000",
            relief=tk.FLAT,
            height=15
        )
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Queue control buttons
        queue_btn_frame = tk.Frame(right_panel, bg="#2b2b2b")
        queue_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(
            queue_btn_frame,
            text="⏭️ Skip",
            command=self.skip_current_speech,
            font=("Arial", 9),
            bg="#ff8800",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            queue_btn_frame,
            text="🧹 Clear All",
            command=self.clear_speech_queue,
            font=("Arial", 9),
            bg="#ff4444",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=3
        ).pack(side=tk.RIGHT, padx=2)
        
        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 9),
            bg="#1a1a1a",
            fg="#888888",
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Update window title with bot name
        self.update_title()
        
        # Welcome message
        bot_name = self.chatbot.bot_name if self.chatbot else "Neural Chatbot"
        self.add_message("Bot", f"Hello! I'm {bot_name}. How can I help you today?", speak=True)
    
    def update_title(self):
        """Update window title with bot name"""
        bot_name = self.chatbot.bot_name if self.chatbot else "ChatBot"
        self.root.title(f"{bot_name} - Enhanced Voice & Text v2")
    
    def update_queue_display(self):
        """Update the visual queue display"""
        with self.queue_lock:
            # Update count label
            count = len(self.queue_items)
            self.queue_count_label.config(text=f"({count})")
            
            # Update listbox
            self.queue_listbox.delete(0, tk.END)
            for i, item in enumerate(self.queue_items):
                # Truncate long messages
                display_text = item[:35] + "..." if len(item) > 35 else item
                self.queue_listbox.insert(tk.END, f"{i+1}. {display_text}")
    
    def add_message(self, sender, message, speak=False):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp if enabled
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.show_timestamps.get():
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.tag_config("timestamp", foreground="#666666", font=("Consolas", 9))
        
        if sender == "User":
            self.chat_display.insert(tk.END, "You: ", "user")
            self.stats['messages_sent'] += 1
        elif sender == "Bot":
            bot_name = self.chatbot.bot_name if self.chatbot else "Bot"
            self.chat_display.insert(tk.END, f"{bot_name}: ", "bot")
            self.stats['messages_received'] += 1
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Store in chat history for search/export
        self.chat_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
        
        # Speak all bot messages if voice is enabled
        if self.voice_enabled.get() and sender == "Bot":
            # Add to tracking list
            with self.queue_lock:
                self.queue_items.append(message)
            
            # Update display
            self.root.after(0, self.update_queue_display)
            
            # Add to actual queue
            self.speech_queue.put(message)
    
    def _speech_worker(self):
        """Background worker that processes speech queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break
                
                # Update "Now Speaking" display
                self.root.after(0, lambda t=text: self.current_speech_label.config(
                    text=t[:80] + "..." if len(t) > 80 else t
                ))
                
                # Remove from queue items list
                with self.queue_lock:
                    if text in self.queue_items:
                        self.queue_items.remove(text)
                
                # Update queue display
                self.root.after(0, self.update_queue_display)
                
                print(f"Speaking: {text[:50]}...")  # Debug
                
                # Create fresh engine for each message
                tts_engine = pyttsx3.init()
                tts_engine.setProperty('rate', self.voice_speed.get())
                tts_engine.setProperty('volume', 1.0)
                
                voices = tts_engine.getProperty('voices')
                if len(voices) > 1:
                    tts_engine.setProperty('voice', voices[1].id)
                
                tts_engine.say(text)
                tts_engine.runAndWait()
                tts_engine.stop()
                
                # Clear "Now Speaking" when done
                self.root.after(0, lambda: self.current_speech_label.config(text="(Nothing)"))
                
                print(f"Done speaking")  # Debug
                
            except Exception as e:
                print(f"TTS Error: {e}")
                self.root.after(0, lambda: self.current_speech_label.config(text="(Error)"))
    
    def clear_speech_queue(self):
        """Clear all pending speech items"""
        # Clear the queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        # Clear tracking list
        with self.queue_lock:
            self.queue_items.clear()
        
        self.update_queue_display()
        self.add_message("System", "Speech queue cleared")
    
    def skip_current_speech(self):
        """Skip currently speaking item (note: pyttsx3 doesn't support stopping mid-speech easily)"""
        self.add_message("System", "Skip requested (will take effect after current speech)")
    
    def speak(self, text):
        """Add text to speech queue"""
        if self.voice_enabled.get():
            with self.queue_lock:
                self.queue_items.append(text)
            self.root.after(0, self.update_queue_display)
            self.speech_queue.put(text)
    
    def send_message(self):
        """Handle sending a message"""
        user_input = self.input_field.get().strip()
        
        if not user_input:
            return
        
        # Track words typed for stats
        self.stats['words_typed'] += len(user_input.split())
        
        # Clear input field
        self.input_field.delete(0, tk.END)
        
        # Display user message
        self.add_message("User", user_input)
        
        # Show typing indicator
        self.show_typing_indicator()
        
        # Update status
        self.status_var.set("Thinking...")
        
        # Process in thread to avoid freezing GUI
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        """Process user message and get bot response"""
        try:
            # Get response from chatbot
            response = self.chatbot.get_response(user_input)
            
            # Hide typing indicator
            self.root.after(0, self.hide_typing_indicator)
            
            # Update GUI in main thread
            self.root.after(0, lambda: self.add_message("Bot", response, speak=True))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            # Update title in case bot name changed
            self.root.after(0, self.update_title)
            
        except Exception as e:
            self.root.after(0, self.hide_typing_indicator)
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.add_message("System", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.add_message("System", "Chat cleared")
        self.status_var.set("Chat cleared - Ready")
    
    def save_chat(self):
        """Save chat history to file"""
        try:
            with open("chat_history.txt", "w", encoding="utf-8") as f:
                f.write(self.chat_display.get(1.0, tk.END))
            messagebox.showinfo("Success", "Chat saved to chat_history.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chat: {e}")
    
    def train_bot(self):
        """Open training dialog"""
        train_window = tk.Toplevel(self.root)
        train_window.title("Train Bot")
        train_window.geometry("500x400")
        train_window.configure(bg="#2b2b2b")
        
        tk.Label(train_window, text="Add New Training Data", font=("Arial", 14, "bold"),
                bg="#2b2b2b", fg="#00ff88").pack(pady=10)
        
        # Intent input
        tk.Label(train_window, text="Intent (e.g., greeting, goodbye):", 
                bg="#2b2b2b", fg="#ffffff").pack(pady=5)
        intent_entry = tk.Entry(train_window, font=("Arial", 11), bg="#1a1a1a", 
                               fg="#ffffff", width=40)
        intent_entry.pack(pady=5)
        
        # Pattern input
        tk.Label(train_window, text="Pattern (user input example):", 
                bg="#2b2b2b", fg="#ffffff").pack(pady=5)
        pattern_entry = tk.Entry(train_window, font=("Arial", 11), bg="#1a1a1a", 
                                fg="#ffffff", width=40)
        pattern_entry.pack(pady=5)
        
        # Response input
        tk.Label(train_window, text="Response (bot reply):", 
                bg="#2b2b2b", fg="#ffffff").pack(pady=5)
        response_text = tk.Text(train_window, font=("Arial", 11), bg="#1a1a1a", 
                               fg="#ffffff", width=40, height=5)
        response_text.pack(pady=5)
        
        def add_training():
            intent = intent_entry.get().strip()
            pattern = pattern_entry.get().strip()
            response = response_text.get(1.0, tk.END).strip()
            
            if not intent or not pattern or not response:
                messagebox.showwarning("Missing Data", "Please fill all fields")
                return
            
            # Add to training data
            if intent not in training_data:
                training_data[intent] = []
            training_data[intent].append(pattern)
            
            if intent not in responses:
                responses[intent] = []
            responses[intent].append(response)
            
            # Retrain
            self.add_message("System", f"Training with new intent: {intent}...")
            threading.Thread(target=self.retrain_model, daemon=True).start()
            
            train_window.destroy()
        
        tk.Button(train_window, text="Add & Retrain", command=add_training,
                 bg="#00ff88", fg="#000000", font=("Arial", 11, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def retrain_model(self):
        """Retrain the model with new data"""
        try:
            vocab_size = self.chatbot.build_vocab(training_data)
            self.chatbot.responses = responses
            self.chatbot.generator.train_from_responses(responses)
            
            X, y = self.chatbot.prepare_training_data(training_data)
            
            for epoch in range(500):
                self.chatbot.train(X, y, epochs=1)
            
            self.chatbot.save("chatbot_model.pkl")
            self.root.after(0, lambda: self.add_message("System", "Training complete!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Bot retrained successfully!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Training failed: {e}"))
    
    def view_intents(self):
        """Display all intents in a dialog"""
        intent_window = tk.Toplevel(self.root)
        intent_window.title("Current Intents")
        intent_window.geometry("600x500")
        intent_window.configure(bg="#2b2b2b")
        
        tk.Label(intent_window, text="📋 Current Intents and Patterns", 
                font=("Arial", 14, "bold"), bg="#2b2b2b", fg="#00ff88").pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(intent_window, font=("Consolas", 10),
                                              bg="#1a1a1a", fg="#ffffff", wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for intent, patterns in training_data.items():
            text_area.insert(tk.END, f"\n{'='*60}\n", "header")
            text_area.insert(tk.END, f"Intent: {intent}\n", "intent")
            text_area.insert(tk.END, f"{'='*60}\n", "header")
            text_area.insert(tk.END, f"Patterns ({len(patterns)}):\n", "label")
            for i, pattern in enumerate(patterns[:5], 1):
                text_area.insert(tk.END, f"  {i}. {pattern}\n")
            if len(patterns) > 5:
                text_area.insert(tk.END, f"  ... and {len(patterns) - 5} more\n")
            text_area.insert(tk.END, "\n")
        
        text_area.tag_config("header", foreground="#888888")
        text_area.tag_config("intent", foreground="#00ff88", font=("Consolas", 10, "bold"))
        text_area.tag_config("label", foreground="#00bbff")
        text_area.config(state=tk.DISABLED)
    
    def test_accuracy(self):
        """Test and display model accuracy"""
        try:
            X, y = self.chatbot.prepare_training_data(training_data)
            predictions = self.chatbot.predict(X)
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            
            # Show detailed results
            result_window = tk.Toplevel(self.root)
            result_window.title("Accuracy Test")
            result_window.geometry("500x400")
            result_window.configure(bg="#2b2b2b")
            
            tk.Label(result_window, text="📊 Model Accuracy Test", 
                    font=("Arial", 14, "bold"), bg="#2b2b2b", fg="#00ff88").pack(pady=10)
            
            # Accuracy display
            acc_frame = tk.Frame(result_window, bg="#1a1a1a", padx=20, pady=20)
            acc_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(acc_frame, text=f"{accuracy:.1%}", font=("Arial", 36, "bold"),
                    bg="#1a1a1a", fg="#00ff88").pack()
            tk.Label(acc_frame, text="Current Accuracy", font=("Arial", 12),
                    bg="#1a1a1a", fg="#888888").pack()
            
            # Stats
            stats_text = scrolledtext.ScrolledText(result_window, font=("Consolas", 10),
                                                  bg="#1a1a1a", fg="#ffffff", height=10)
            stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            stats_text.insert(tk.END, f"Total training samples: {len(X)}\n")
            stats_text.insert(tk.END, f"Number of intents: {len(self.chatbot.intents)}\n")
            stats_text.insert(tk.END, f"Vocabulary size: {len(self.chatbot.vocab)}\n")
            stats_text.insert(tk.END, f"\nCorrect predictions: {int(accuracy * len(X))}/{len(X)}\n")
            stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test accuracy: {e}")
    
    def increase_accuracy(self):
        """Augment training data to increase accuracy"""
        if not messagebox.askyesno("Increase Accuracy", 
                                   "This will augment training data and retrain.\nContinue?"):
            return
        
        self.add_message("System", "Augmenting training data...")
        threading.Thread(target=self.perform_augmentation, daemon=True).start()
    
    def perform_augmentation(self):
        """Perform data augmentation"""
        try:
            augmented_count = 0
            
            for intent, phrases in list(training_data.items()):
                new_phrases = []
                for phrase in phrases:
                    words = phrase.split()
                    if len(words) > 2:
                        shorter = ' '.join(words[:-1])
                        if shorter not in phrases and shorter not in new_phrases and len(shorter) > 3:
                            new_phrases.append(shorter)
                    
                    please_phrase = "please " + phrase
                    if please_phrase not in phrases and please_phrase not in new_phrases:
                        new_phrases.append(please_phrase)
                
                for np_phrase in new_phrases[:5]:
                    training_data[intent].append(np_phrase)
                    augmented_count += 1
            
            self.root.after(0, lambda: self.add_message("System", f"Added {augmented_count} augmented phrases. Retraining..."))
            
            # Retrain
            vocab_size = self.chatbot.build_vocab(training_data)
            X, y = self.chatbot.prepare_training_data(training_data)
            
            for epoch in range(1000):
                self.chatbot.train(X, y, epochs=1)
            
            self.chatbot.save("chatbot_model.pkl")
            
            predictions = self.chatbot.predict(X)
            final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            
            self.root.after(0, lambda: self.add_message("System", f"Augmentation complete! New accuracy: {final_accuracy:.1%}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Training complete!\nNew accuracy: {final_accuracy:.1%}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Augmentation failed: {e}"))
    
    def retrain_from_scratch(self):
        """Completely retrain the model"""
        if not messagebox.askyesno("Retrain from Scratch", 
                                   "This will rebuild the model from scratch.\nContinue?"):
            return
        
        self.add_message("System", "Retraining from scratch...")
        threading.Thread(target=self.perform_full_retrain, daemon=True).start()
    
    def perform_full_retrain(self):
        """Perform complete retraining"""
        try:
            vocab_size = self.chatbot.build_vocab(training_data)
            num_intents = len(training_data)
            
            # Create fresh chatbot
            self.chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
            self.chatbot.build_vocab(training_data)
            self.chatbot.responses = responses
            self.chatbot.generator.train_from_responses(responses)
            
            X, y = self.chatbot.prepare_training_data(training_data)
            
            for epoch in range(1000):
                self.chatbot.train(X, y, epochs=1)
            
            self.chatbot.save("chatbot_model.pkl")
            
            predictions = self.chatbot.predict(X)
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            
            self.root.after(0, lambda: self.add_message("System", f"Retraining complete! Accuracy: {accuracy:.1%}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Retraining complete!\nAccuracy: {accuracy:.1%}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Retraining failed: {e}"))
    
    def on_closing(self):
        """Handle window closing"""
        self.chatbot.memory.save("chatbot_memory.pkl")
        # Stop speech thread
        self.speech_queue.put(None)  # Send shutdown signal
        self.root.destroy()
    
    # ==================== NEW FEATURES ====================
    
    def send_quick_reply(self, text):
        """Send a quick reply message"""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, text)
        self.send_message()
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.dark_mode.get():
            self.current_theme = self.themes['dark']
        else:
            self.current_theme = self.themes['light']
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        theme = self.current_theme
        
        # Root and main frames
        self.root.configure(bg=theme['bg'])
        
        # Update chat display
        self.chat_display.config(bg=theme['bg'], fg=theme['fg'])
        self.chat_display.tag_config("user", foreground=theme['user'])
        self.chat_display.tag_config("bot", foreground=theme['bot'])
        self.chat_display.tag_config("system", foreground=theme['system'])
        
        # Update input field
        self.input_field.config(bg=theme['bg'], fg=theme['fg'])
        
        self.status_var.set(f"Theme changed to {'Dark' if self.dark_mode.get() else 'Light'} mode")
    
    def change_font_size(self, delta):
        """Change the font size of the chat display"""
        new_size = self.font_size.get() + delta
        if 8 <= new_size <= 24:
            self.font_size.set(new_size)
            self.chat_display.config(font=("Consolas", new_size))
            self.chat_display.tag_config("user", font=("Consolas", new_size, "bold"))
            self.chat_display.tag_config("bot", font=("Consolas", new_size, "bold"))
            self.status_var.set(f"Font size: {new_size}")
    
    def open_search(self):
        """Open the search panel"""
        if self.search_frame and self.search_frame.winfo_exists():
            self.search_entry.focus()
            return
        
        self.search_frame = tk.Frame(self.root, bg="#333333", pady=5)
        self.search_frame.pack(fill=tk.X, padx=10, before=self.root.winfo_children()[1])
        
        tk.Label(
            self.search_frame,
            text="🔍",
            font=("Arial", 12),
            bg="#333333",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Arial", 11),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#00ff88",
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        self.search_entry.bind("<Return>", lambda e: self.search_chat())
        self.search_entry.focus()
        
        tk.Button(
            self.search_frame,
            text="Find",
            command=self.search_chat,
            font=("Arial", 9),
            bg="#00ff88",
            fg="#000000",
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            self.search_frame,
            text="✕",
            command=self.close_search,
            font=("Arial", 9),
            bg="#ff4444",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=8
        ).pack(side=tk.RIGHT, padx=5)
        
        self.search_result_label = tk.Label(
            self.search_frame,
            text="",
            font=("Arial", 9),
            bg="#333333",
            fg="#888888"
        )
        self.search_result_label.pack(side=tk.LEFT, padx=10)
    
    def search_chat(self):
        """Search for text in the chat"""
        query = self.search_entry.get().lower()
        if not query:
            return
        
        # Remove previous highlights
        self.chat_display.tag_remove("search_highlight", "1.0", tk.END)
        self.chat_display.tag_config("search_highlight", background="#ffff00", foreground="#000000")
        
        # Search and highlight
        count = 0
        start_pos = "1.0"
        while True:
            pos = self.chat_display.search(query, start_pos, tk.END, nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            self.chat_display.tag_add("search_highlight", pos, end_pos)
            start_pos = end_pos
            count += 1
        
        if count > 0:
            self.search_result_label.config(text=f"Found {count} match(es)")
            # Scroll to first match
            first_match = self.chat_display.search(query, "1.0", tk.END, nocase=True)
            if first_match:
                self.chat_display.see(first_match)
        else:
            self.search_result_label.config(text="No matches found")
    
    def close_search(self):
        """Close the search panel"""
        if self.search_frame and self.search_frame.winfo_exists():
            self.chat_display.tag_remove("search_highlight", "1.0", tk.END)
            self.search_frame.destroy()
            self.search_frame = None
    
    def show_statistics(self):
        """Show conversation statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Conversation Statistics")
        stats_window.geometry("400x350")
        stats_window.configure(bg="#2b2b2b")
        
        tk.Label(
            stats_window,
            text="📊 Session Statistics",
            font=("Arial", 16, "bold"),
            bg="#2b2b2b",
            fg="#00ff88"
        ).pack(pady=15)
        
        # Calculate session duration
        duration = datetime.now() - self.stats['session_start']
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_data = [
            ("📤 Messages Sent", self.stats['messages_sent']),
            ("📥 Messages Received", self.stats['messages_received']),
            ("💬 Total Messages", self.stats['messages_sent'] + self.stats['messages_received']),
            ("📝 Words Typed", self.stats['words_typed']),
            ("⏱️ Session Duration", f"{hours}h {minutes}m {seconds}s"),
            ("🎯 Intents Trained", len(training_data)),
            ("📚 Vocabulary Size", len(self.chatbot.vocab) if self.chatbot else 0),
        ]
        
        stats_frame = tk.Frame(stats_window, bg="#1a1a1a", padx=20, pady=15)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for label, value in stats_data:
            row = tk.Frame(stats_frame, bg="#1a1a1a")
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                row,
                text=label,
                font=("Arial", 11),
                bg="#1a1a1a",
                fg="#ffffff",
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=str(value),
                font=("Arial", 11, "bold"),
                bg="#1a1a1a",
                fg="#00ff88",
                anchor=tk.E
            ).pack(side=tk.RIGHT)
    
    def open_voice_settings(self):
        """Open voice settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("🎚️ Voice Settings")
        settings_window.geometry("350x250")
        settings_window.configure(bg="#2b2b2b")
        
        tk.Label(
            settings_window,
            text="🎚️ Voice Settings",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#00ff88"
        ).pack(pady=15)
        
        # Voice speed slider
        speed_frame = tk.Frame(settings_window, bg="#2b2b2b")
        speed_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            speed_frame,
            text="Speech Speed:",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="#ffffff"
        ).pack(anchor=tk.W)
        
        speed_label = tk.Label(
            speed_frame,
            text=f"{self.voice_speed.get()} wpm",
            font=("Arial", 10),
            bg="#2b2b2b",
            fg="#888888"
        )
        speed_label.pack(anchor=tk.E)
        
        def update_speed_label(val):
            speed_label.config(text=f"{int(float(val))} wpm")
            self.voice_speed.set(int(float(val)))
        
        speed_slider = tk.Scale(
            speed_frame,
            from_=100,
            to=300,
            orient=tk.HORIZONTAL,
            variable=self.voice_speed,
            command=update_speed_label,
            bg="#2b2b2b",
            fg="#ffffff",
            highlightthickness=0,
            troughcolor="#1a1a1a",
            length=250
        )
        speed_slider.pack(fill=tk.X)
        
        # Voice enabled checkbox
        tk.Checkbutton(
            settings_window,
            text="🔊 Voice Enabled",
            variable=self.voice_enabled,
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            selectcolor="#1a1a1a"
        ).pack(pady=10)
        
        tk.Button(
            settings_window,
            text="Apply",
            command=settings_window.destroy,
            font=("Arial", 11),
            bg="#00ff88",
            fg="#000000",
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(pady=15)
    
    def export_chat(self, format_type):
        """Export chat in various formats"""
        if not self.chat_history:
            messagebox.showwarning("No Data", "No chat history to export!")
            return
        
        # Get save location
        filetypes = {
            'txt': [("Text Files", "*.txt")],
            'json': [("JSON Files", "*.json")],
            'html': [("HTML Files", "*.html")]
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=filetypes[format_type],
            initialfile=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not filename:
            return
        
        try:
            if format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for msg in self.chat_history:
                        timestamp = msg.get('timestamp', '')
                        f.write(f"[{timestamp}] {msg['sender']}: {msg['message']}\n")
            
            elif format_type == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'export_date': datetime.now().isoformat(),
                        'messages': self.chat_history,
                        'stats': {
                            'total_messages': len(self.chat_history),
                            'session_start': self.stats['session_start'].isoformat()
                        }
                    }, f, indent=2)
            
            elif format_type == 'html':
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Chat Export - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 20px; }}
        .message {{ margin: 10px 0; padding: 10px; border-radius: 8px; }}
        .user {{ background: #0066cc; text-align: right; }}
        .bot {{ background: #008844; }}
        .system {{ background: #cc6600; font-style: italic; }}
        .timestamp {{ font-size: 0.8em; color: #888; }}
        h1 {{ color: #00ff88; }}
    </style>
</head>
<body>
    <h1>🤖 Chat Export</h1>
    <p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
                for msg in self.chat_history:
                    sender_class = msg['sender'].lower() if msg['sender'] in ['User', 'Bot'] else 'system'
                    timestamp = msg.get('timestamp', '')
                    html_content += f"""    <div class="message {sender_class}">
        <span class="timestamp">{timestamp}</span><br>
        <strong>{msg['sender']}:</strong> {msg['message']}
    </div>\n"""
                
                html_content += "</body></html>"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            messagebox.showinfo("Success", f"Chat exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("⌨️ Keyboard Shortcuts")
        help_window.geometry("350x300")
        help_window.configure(bg="#2b2b2b")
        
        tk.Label(
            help_window,
            text="⌨️ Keyboard Shortcuts",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#00ff88"
        ).pack(pady=15)
        
        shortcuts = [
            ("Ctrl + Enter", "Send message"),
            ("Ctrl + L", "Clear chat"),
            ("Ctrl + S", "Save chat"),
            ("Ctrl + F", "Search chat"),
            ("Ctrl + T", "Toggle theme"),
            ("Escape", "Close search"),
            ("F1", "Show this help"),
        ]
        
        shortcuts_frame = tk.Frame(help_window, bg="#1a1a1a", padx=15, pady=10)
        shortcuts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for key, action in shortcuts:
            row = tk.Frame(shortcuts_frame, bg="#1a1a1a")
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(
                row,
                text=key,
                font=("Consolas", 10, "bold"),
                bg="#1a1a1a",
                fg="#00bbff",
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=action,
                font=("Arial", 10),
                bg="#1a1a1a",
                fg="#ffffff",
                anchor=tk.W
            ).pack(side=tk.LEFT)
    
    # ===== LEARNING MENU METHODS =====
    
    def open_teach_dialog(self):
        """Open dialog to teach the bot a new response"""
        if not hasattr(self.chatbot, 'learner') or not self.chatbot.learner:
            messagebox.showwarning("Not Available", "Learning features are not available. Make sure chatbot_learning.py is installed.")
            return
        
        teach_window = tk.Toplevel(self.root)
        teach_window.title("📚 Teach Bot New Response")
        teach_window.geometry("500x350")
        teach_window.configure(bg=self.current_theme['bg'])
        
        tk.Label(
            teach_window,
            text="📚 Teach Me Something New!",
            font=("Arial", 16, "bold"),
            bg=self.current_theme['bg'],
            fg=self.current_theme['accent']
        ).pack(pady=15)
        
        # Input frame
        input_frame = tk.Frame(teach_window, bg=self.current_theme['bg'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="When someone says:",
            font=("Arial", 11),
            bg=self.current_theme['bg'],
            fg=self.current_theme['fg']
        ).pack(anchor=tk.W)
        
        trigger_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['fg'],
            insertbackground=self.current_theme['fg']
        )
        trigger_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(
            input_frame,
            text="I should respond with:",
            font=("Arial", 11),
            bg=self.current_theme['bg'],
            fg=self.current_theme['fg']
        ).pack(anchor=tk.W, pady=(15, 0))
        
        response_entry = tk.Text(
            input_frame,
            font=("Arial", 11),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['fg'],
            insertbackground=self.current_theme['fg'],
            height=4
        )
        response_entry.pack(fill=tk.X, pady=5)
        
        def save_teaching():
            trigger = trigger_entry.get().strip()
            response = response_entry.get("1.0", tk.END).strip()
            
            if not trigger or not response:
                messagebox.showwarning("Missing Info", "Please fill in both fields!")
                return
            
            self.chatbot.learner.learn_response(trigger, response)
            self.chatbot.learner.save()
            
            messagebox.showinfo("Learned!", f"I've learned to respond to '{trigger}' with '{response}'! 🎓")
            teach_window.destroy()
            
            # Show in chat
            self.add_system_message(f"📚 Learned new response for: '{trigger}'")
        
        tk.Button(
            teach_window,
            text="💾 Teach Me!",
            command=save_teaching,
            font=("Arial", 11, "bold"),
            bg=self.current_theme['accent'],
            fg="#000000",
            relief=tk.FLAT,
            padx=30,
            pady=10
        ).pack(pady=20)
        
        tk.Label(
            teach_window,
            text="💡 Tip: You can also teach me by chatting!\nTry saying: 'When I say X, respond with Y'",
            font=("Arial", 9),
            bg=self.current_theme['bg'],
            fg=self.current_theme['system']
        ).pack(pady=10)
    
    def view_learned_responses(self):
        """View all learned responses"""
        if not hasattr(self.chatbot, 'learner') or not self.chatbot.learner:
            messagebox.showwarning("Not Available", "Learning features are not available.")
            return
        
        view_window = tk.Toplevel(self.root)
        view_window.title("🧠 Learned Responses")
        view_window.geometry("600x500")
        view_window.configure(bg=self.current_theme['bg'])
        
        tk.Label(
            view_window,
            text="🧠 What I've Learned",
            font=("Arial", 16, "bold"),
            bg=self.current_theme['bg'],
            fg=self.current_theme['accent']
        ).pack(pady=15)
        
        # Create scrollable frame
        canvas = tk.Canvas(view_window, bg=self.current_theme['secondary'])
        scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.current_theme['secondary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        learned = self.chatbot.learner.learned_responses
        
        if not learned:
            tk.Label(
                scrollable_frame,
                text="I haven't learned any custom responses yet!\n\nTeach me by using the menu or chatting.",
                font=("Arial", 12),
                bg=self.current_theme['secondary'],
                fg=self.current_theme['fg'],
                pady=50
            ).pack()
        else:
            for trigger, responses in learned.items():
                frame = tk.Frame(scrollable_frame, bg=self.current_theme['bg'], pady=10, padx=10)
                frame.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(
                    frame,
                    text=f"📝 '{trigger}'",
                    font=("Arial", 11, "bold"),
                    bg=self.current_theme['bg'],
                    fg=self.current_theme['user'],
                    anchor=tk.W
                ).pack(fill=tk.X)
                
                for resp in responses:
                    tk.Label(
                        frame,
                        text=f"   → {resp}",
                        font=("Arial", 10),
                        bg=self.current_theme['bg'],
                        fg=self.current_theme['bot'],
                        anchor=tk.W
                    ).pack(fill=tk.X)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def show_learning_stats(self):
        """Show learning and personality statistics"""
        if not self.chatbot:
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Learning Statistics")
        stats_window.geometry("450x500")
        stats_window.configure(bg=self.current_theme['bg'])
        
        tk.Label(
            stats_window,
            text="📊 Learning & Personality Stats",
            font=("Arial", 16, "bold"),
            bg=self.current_theme['bg'],
            fg=self.current_theme['accent']
        ).pack(pady=15)
        
        stats_frame = tk.Frame(stats_window, bg=self.current_theme['secondary'], padx=20, pady=15)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Get stats
        stats = self.chatbot.get_learning_stats() if hasattr(self.chatbot, 'get_learning_stats') else {}
        
        # Learning stats
        tk.Label(
            stats_frame,
            text="🧠 Learning",
            font=("Arial", 13, "bold"),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['accent']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        learned_count = stats.get('learned_responses', 0)
        self._add_stat_row(stats_frame, "📚 Learned Responses", learned_count)
        self._add_stat_row(stats_frame, "💬 Total Conversations", stats.get('total_conversations', 0))
        
        # Personality stats
        tk.Label(
            stats_frame,
            text="\n😊 Personality",
            font=("Arial", 13, "bold"),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['accent']
        ).pack(anchor=tk.W, pady=(10, 10))
        
        mood = stats.get('mood', 0.5)
        mood_text = "😄 Very Happy" if mood > 0.8 else "🙂 Happy" if mood > 0.6 else "😐 Neutral" if mood > 0.4 else "😔 Sad"
        self._add_stat_row(stats_frame, "Current Mood", mood_text)
        
        relationship = stats.get('relationship_level', 0)
        rel_text = "Best Friends!" if relationship > 80 else "Good Friends" if relationship > 50 else "Friends" if relationship > 20 else "Getting to know you"
        self._add_stat_row(stats_frame, "🤝 Relationship", rel_text)
        self._add_stat_row(stats_frame, "Relationship Score", f"{int(relationship)}/100")
        
        # Memory stats
        if hasattr(self.chatbot, 'long_memory') and self.chatbot.long_memory:
            tk.Label(
                stats_frame,
                text="\n💾 Memory",
                font=("Arial", 13, "bold"),
                bg=self.current_theme['secondary'],
                fg=self.current_theme['accent']
            ).pack(anchor=tk.W, pady=(10, 10))
            
            profile = self.chatbot.long_memory.user_profile
            self._add_stat_row(stats_frame, "Your Name", profile.get('name') or "Not set")
            self._add_stat_row(stats_frame, "Total Messages", profile.get('total_messages', 0))
            facts_count = len(self.chatbot.long_memory.important_facts)
            self._add_stat_row(stats_frame, "Remembered Facts", facts_count)
    
    def _add_stat_row(self, parent, label, value):
        """Helper to add a stat row"""
        row = tk.Frame(parent, bg=self.current_theme['secondary'])
        row.pack(fill=tk.X, pady=3)
        
        tk.Label(
            row,
            text=label,
            font=("Arial", 10),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['fg'],
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=str(value),
            font=("Arial", 10, "bold"),
            bg=self.current_theme['secondary'],
            fg=self.current_theme['accent'],
            anchor=tk.E
        ).pack(side=tk.RIGHT)
    
    def save_learning_data(self):
        """Manually save all learning data"""
        if self.chatbot:
            if hasattr(self.chatbot, 'learner') and self.chatbot.learner:
                self.chatbot.learner.save()
            if hasattr(self.chatbot, 'long_memory') and self.chatbot.long_memory:
                self.chatbot.long_memory.save()
            self.chatbot.save("chatbot_model.pkl")
            messagebox.showinfo("Saved", "All learning data has been saved! 💾")
    
    def clear_learned_data(self):
        """Clear all learned responses"""
        if not hasattr(self.chatbot, 'learner') or not self.chatbot.learner:
            return
        
        if messagebox.askyesno("Clear Learned Data", 
                               "Are you sure you want to clear all learned responses?\n\n"
                               "This cannot be undone!"):
            self.chatbot.learner.learned_responses.clear()
            self.chatbot.learner.save()
            messagebox.showinfo("Cleared", "All learned responses have been cleared.")
    
    def add_system_message(self, message):
        """Add a system message to the chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n[System] {message}\n", "system")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    # ===== END LEARNING MENU METHODS =====
    
    # ===== WEB SEARCH METHODS =====
    
    def toggle_web_search(self):
        """Toggle web search on/off"""
        if self.chatbot and hasattr(self.chatbot, 'fallback'):
            enabled = self.web_search_enabled.get()
            self.chatbot.fallback.toggle_web_search(enabled)
            status = "enabled 🌐" if enabled else "disabled"
            self.add_system_message(f"Web search {status}")
    
    def show_web_search_status(self):
        """Show web search status dialog"""
        if self.chatbot and hasattr(self.chatbot, 'fallback'):
            available = self.chatbot.fallback.is_web_search_available()
            enabled = self.web_search_enabled.get()
            
            status_text = f"""🌐 Web Search Status

Available: {'✅ Yes' if available else '❌ No (web_search.py missing)'}
Enabled: {'✅ Yes' if enabled else '❌ No'}

Features:
• 🔍 DuckDuckGo instant answers
• 📚 Wikipedia summaries
• 🤖 Auto-search for factual questions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 DIRECT SEARCH COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type these in chat to search directly:

  search: <topic>     - Search the web
  wiki: <topic>       - Search Wikipedia
  ddg: <topic>        - Search DuckDuckGo
  /search <topic>     - Alternative syntax
  look up: <topic>    - Another way to search

Examples:
  search: python programming
  wiki: Albert Einstein
  ddg: climate change

The bot also auto-searches when you ask:
• "What is...?" questions
• "Who invented...?" questions
• About things it doesn't know
"""
        else:
            status_text = "❌ Web search not available"
        
        messagebox.showinfo("🌐 Web Search Status", status_text)
    
    def open_wikipedia_search(self):
        """Open Wikipedia search dialog"""
        search_window = tk.Toplevel(self.root)
        search_window.title("📚 Wikipedia Search")
        search_window.geometry("500x400")
        search_window.configure(bg="#2b2b2b")
        
        tk.Label(
            search_window,
            text="📚 Search Wikipedia",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#00ff88"
        ).pack(pady=15)
        
        # Search input
        input_frame = tk.Frame(search_window, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_entry = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#00ff88"
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        search_entry.focus()
        
        # Result display
        result_frame = tk.Frame(search_window, bg="#2b2b2b")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#1a1a1a",
            fg="#ffffff",
            height=12
        )
        result_text.pack(fill=tk.BOTH, expand=True)
        
        def do_search():
            query = search_entry.get().strip()
            if not query:
                return
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "🔍 Searching Wikipedia...\n")
            result_text.config(state=tk.DISABLED)
            search_window.update()
            
            try:
                from web_search import WebSearch
                searcher = WebSearch()
                result = searcher.search_wikipedia(query)
                
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                
                if result:
                    title = result.get('title', query)
                    result_text.insert(tk.END, f"📖 {title}\n\n", "title")
                    result_text.insert(tk.END, result['answer'])
                    if result.get('url'):
                        result_text.insert(tk.END, f"\n\n🔗 {result['url']}")
                else:
                    result_text.insert(tk.END, "❌ No results found. Try a different search term.")
                
                result_text.config(state=tk.DISABLED)
            except Exception as e:
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"❌ Error: {e}")
                result_text.config(state=tk.DISABLED)
        
        def use_in_chat():
            content = result_text.get(1.0, tk.END).strip()
            if content and not content.startswith("🔍") and not content.startswith("❌"):
                self.add_system_message("Wikipedia result added to chat")
                self.display_message("Bot", content, "bot")
            search_window.destroy()
        
        # Search button
        search_btn = tk.Button(
            input_frame,
            text="🔍 Search",
            command=do_search,
            font=("Arial", 11),
            bg="#00ff88",
            fg="#000000",
            padx=15
        )
        search_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        search_entry.bind("<Return>", lambda e: do_search())
        
        # Use in chat button
        tk.Button(
            search_window,
            text="📋 Use in Chat",
            command=use_in_chat,
            font=("Arial", 11),
            bg="#00bbff",
            fg="#000000",
            padx=15,
            pady=5
        ).pack(pady=10)
    
    def open_duckduckgo_search(self):
        """Open DuckDuckGo search dialog"""
        search_window = tk.Toplevel(self.root)
        search_window.title("🔎 DuckDuckGo Search")
        search_window.geometry("500x400")
        search_window.configure(bg="#2b2b2b")
        
        tk.Label(
            search_window,
            text="🔎 Search DuckDuckGo",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#00ff88"
        ).pack(pady=15)
        
        # Search input
        input_frame = tk.Frame(search_window, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_entry = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#00ff88"
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        search_entry.focus()
        
        # Result display
        result_frame = tk.Frame(search_window, bg="#2b2b2b")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#1a1a1a",
            fg="#ffffff",
            height=12
        )
        result_text.pack(fill=tk.BOTH, expand=True)
        
        def do_search():
            query = search_entry.get().strip()
            if not query:
                return
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "🔍 Searching DuckDuckGo...\n")
            result_text.config(state=tk.DISABLED)
            search_window.update()
            
            try:
                from web_search import WebSearch
                searcher = WebSearch()
                result = searcher.search_duckduckgo(query)
                
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                
                if result:
                    result_text.insert(tk.END, f"📖 {result.get('type', 'Result').title()}\n\n")
                    result_text.insert(tk.END, result['answer'])
                    if result.get('url'):
                        result_text.insert(tk.END, f"\n\n🔗 {result['url']}")
                else:
                    result_text.insert(tk.END, "❌ No instant answer found.\n\nTip: Try more specific questions like:\n• 'What is [topic]?'\n• 'Define [word]'\n• 'Who is [person]?'")
                
                result_text.config(state=tk.DISABLED)
            except Exception as e:
                result_text.config(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"❌ Error: {e}")
                result_text.config(state=tk.DISABLED)
        
        def use_in_chat():
            content = result_text.get(1.0, tk.END).strip()
            if content and not content.startswith("🔍") and not content.startswith("❌"):
                self.add_system_message("DuckDuckGo result added to chat")
                self.display_message("Bot", content, "bot")
            search_window.destroy()
        
        # Search button
        search_btn = tk.Button(
            input_frame,
            text="🔍 Search",
            command=do_search,
            font=("Arial", 11),
            bg="#00ff88",
            fg="#000000",
            padx=15
        )
        search_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        search_entry.bind("<Return>", lambda e: do_search())
        
        # Use in chat button
        tk.Button(
            search_window,
            text="📋 Use in Chat",
            command=use_in_chat,
            font=("Arial", 11),
            bg="#00bbff",
            fg="#000000",
            padx=15,
            pady=5
        ).pack(pady=10)
    
    # ===== END WEB SEARCH METHODS =====
    
    def show_about(self):
        """Show about dialog"""
        about_text = """🤖 Neural Chatbot v2

Enhanced GUI with:
• Speech queue display
• Dark/Light themes
• Message timestamps
• Voice speed control
• Quick reply buttons
• Chat search
• Statistics tracking
• Multiple export formats
• Keyboard shortcuts
• Auto-save feature

🆕 NEW! Learning Features:
• Teach bot new responses
• Bot learns from conversation
• Personality & mood system
• Long-term memory
• Relationship building

🌐 NEW! Web Search:
• Auto-searches when unsure
• Wikipedia integration
• DuckDuckGo instant answers
• No API key required!

Built with Python & Tkinter
Neural Network powered chatbot"""
        
        messagebox.showinfo("About Neural Chatbot v2", about_text)
    
    def show_typing_indicator(self):
        """Show typing indicator"""
        bot_name = self.chatbot.bot_name if self.chatbot else "Bot"
        self.typing_label.config(text=f"{bot_name} is typing...")
        self.typing_indicator_active = True
    
    def hide_typing_indicator(self):
        """Hide typing indicator"""
        self.typing_label.config(text="")
        self.typing_indicator_active = False


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ChatbotGUIv2(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
