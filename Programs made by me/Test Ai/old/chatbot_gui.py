"""
Chatbot with GUI and Voice
Separate window interface with text-to-speech
"""
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, simpledialog
import threading
import queue
import pyttsx3
import re
from chatbot import NeuralChatbot, training_data, responses
import numpy as np


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Chatbot - Voice & Text")
        self.root.geometry("700x600")
        self.root.configure(bg="#2b2b2b")
        
        self.voice_enabled = tk.BooleanVar(value=True)
        
        # Speech queue for handling TTS properly
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # Load chatbot
        self.chatbot = None
        self.load_chatbot()
        
        # Setup GUI
        self.create_menu()
        self.create_widgets()
        
    def load_chatbot(self):
        """Load and initialize the chatbot"""
        model_file = "chatbot_model.pkl"
        memory_file = "chatbot_memory.pkl"
        
        # Build vocabulary
        temp_bot = NeuralChatbot([1, 1])
        vocab_size = temp_bot.build_vocab(training_data)
        num_intents = len(training_data)
        
        # Create chatbot
        self.chatbot = NeuralChatbot([vocab_size, 64, 32, num_intents], learning_rate=0.1)
        self.chatbot.vocab = temp_bot.vocab
        self.chatbot.responses = responses
        self.chatbot.generator.train_from_responses(responses)
        
        # Load saved model
        model_loaded = self.chatbot.load(model_file)
        
        if not model_loaded:
            # Train if no saved model
            X, y = self.chatbot.prepare_training_data(training_data)
            for epoch in range(1000):
                self.chatbot.train(X, y, epochs=1)
            self.chatbot.save(model_file)
        
        # Load memory
        self.chatbot.memory.load(memory_file)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg="#1a1a1a", fg="#ffffff")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#ffffff")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat", command=self.save_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Training menu
        train_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#ffffff")
        menubar.add_cascade(label="Training", menu=train_menu)
        train_menu.add_command(label="Train Bot (Add Responses)", command=self.train_bot)
        train_menu.add_command(label="Test Accuracy", command=self.test_accuracy)
        train_menu.add_command(label="Increase Accuracy", command=self.increase_accuracy)
        train_menu.add_command(label="Retrain from Scratch", command=self.retrain_from_scratch)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#ffffff")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View Intents", command=self.view_intents)
        view_menu.add_command(label="Clear Chat", command=self.clear_chat)
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg="#1a1a1a", pady=10)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 Neural Chatbot",
            font=("Arial", 20, "bold"),
            bg="#1a1a1a",
            fg="#00ff88"
        )
        title_label.pack()
        
        # Control panel
        control_frame = tk.Frame(self.root, bg="#2b2b2b", pady=5)
        control_frame.pack(fill=tk.X, padx=10)
        
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
        chat_frame = tk.Frame(self.root, bg="#2b2b2b")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        input_frame = tk.Frame(self.root, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
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
        
        # Status bar
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
        self.root.title(f"{bot_name} - Voice & Text")
    
    def add_message(self, sender, message, speak=False):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "User":
            self.chat_display.insert(tk.END, "You: ", "user")
        elif sender == "Bot":
            bot_name = self.chatbot.bot_name if self.chatbot else "Bot"
            self.chat_display.insert(tk.END, f"{bot_name}: ", "bot")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Speak all bot messages if voice is enabled
        print(f"DEBUG: sender={sender}, voice_enabled={self.voice_enabled.get()}")  # Debug
        if self.voice_enabled.get() and sender == "Bot":
            print(f"DEBUG: Adding to queue: {message[:50]}...")  # Debug
            self.speech_queue.put(message)
            print(f"DEBUG: Queue size now: {self.speech_queue.qsize()}")  # Debug
    
    def _speech_worker(self):
        """Background worker that processes speech queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break
                print(f"Speaking: {text}")  # Debug print
                
                # Create fresh engine for each message (fixes pyttsx3 hanging issue)
                tts_engine = pyttsx3.init()
                tts_engine.setProperty('rate', 175)
                tts_engine.setProperty('volume', 1.0)
                
                voices = tts_engine.getProperty('voices')
                if len(voices) > 1:
                    tts_engine.setProperty('voice', voices[1].id)
                
                tts_engine.say(text)
                tts_engine.runAndWait()
                tts_engine.stop()
                
                print(f"Done speaking")  # Debug
            except Exception as e:
                print(f"TTS Error: {e}")
    
    def speak(self, text):
        """Add text to speech queue"""
        if self.voice_enabled.get():
            self.speech_queue.put(text)
    
    def send_message(self):
        """Handle sending a message"""
        user_input = self.input_field.get().strip()
        
        if not user_input:
            return
        
        # Clear input field
        self.input_field.delete(0, tk.END)
        
        # Display user message
        self.add_message("User", user_input)
        
        # Update status
        self.status_var.set("Thinking...")
        
        # Process in thread to avoid freezing GUI
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        """Process user message and get bot response"""
        try:
            # Get response from chatbot
            response = self.chatbot.get_response(user_input)
            
            # Update GUI in main thread
            self.root.after(0, lambda: self.add_message("Bot", response, speak=True))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            # Update title in case bot name changed
            self.root.after(0, self.update_title)
            
        except Exception as e:
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


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
