import sys
import time
import os
import requests
import faiss
from sentence_transformers import SentenceTransformer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QDesktopWidget,
    QLabel, QFrame, QScrollArea, QSpacerItem, QSizePolicy, QSplashScreen
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QTextCursor, QPixmap, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

# Groq API configuration
GROQ_API_KEY = "gsk_h7vopgggG"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Load FAISS index and text data only once at startup
INDEX_PATH = "sop_index.faiss"
TEXTS_PATH = "sop_texts.txt"

class SplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFont(QFont("Inter", 10))
        
        # Progress variables
        self.progress = 0
        self.message = "Initializing..."
        
        # Setup timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # Update every 30ms
        
    def update_progress(self):
        """Update progress bar and messages"""
        self.progress += 0.5  # Increment progress
        
        # Update messages at different stages
        if self.progress < 20:
            self.message = "Loading core modules..."
        elif self.progress < 40:
            self.message = "Initializing UI framework..."
        elif self.progress < 60:
            self.message = "Preparing RAG system..."
        elif self.progress < 80:
            self.message = "Loading story data..."
        else:
            self.message = "Almost ready..."
            
        self.repaint()  # Trigger repaint
        
        if self.progress >= 100:
            self.timer.stop()
            
    def drawContents(self, painter):
        """Custom draw method for splash screen"""
        super().drawContents(painter)
        
        # Setup painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw progress bar background
        bar_rect = QRect(50, self.height() - 60, self.width() - 100, 20)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(50, 50, 70, 200))
        painter.drawRoundedRect(bar_rect, 10, 10)
        
        # Draw progress bar fill
        fill_width = int(bar_rect.width() * (self.progress / 100))
        fill_rect = QRect(bar_rect.x(), bar_rect.y(), fill_width, bar_rect.height())
        
        # Create gradient for progress bar
        gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.topRight())
        gradient.setColorAt(0, QColor(114, 137, 218))  # #7289da
        gradient.setColorAt(1, QColor(90, 100, 200))   # #5a64c8
        painter.setBrush(gradient)
        painter.drawRoundedRect(fill_rect, 10, 10)
        
        # Draw progress text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Inter", 9, QFont.Bold))
        painter.drawText(bar_rect, Qt.AlignCenter, f"{int(self.progress)}%")
        
        # Draw status message
        painter.setFont(QFont("Inter", 11))
        painter.drawText(QRect(50, self.height() - 90, self.width() - 100, 30), 
                         Qt.AlignCenter, self.message)
        
        # Draw title
        painter.setFont(QFont("Inter", 20, QFont.Bold))
        painter.setPen(QColor(180, 180, 255))
        painter.drawText(QRect(0, 40, self.width(), 60), 
                         Qt.AlignCenter, "Story Explainer AI")

def load_rag_resources():
    """Load RAG resources with progress reporting"""
    rag_enabled = False
    index = None
    raw_text = None
    embedder = None
    
    # Check if files exist before loading
    if os.path.exists(INDEX_PATH) and os.path.exists(TEXTS_PATH):
        try:
            # Create splash screen
            splash = SplashScreen(QPixmap(800, 400))
            splash.show()
            QApplication.processEvents()  # Process events to show splash
            
            # Load FAISS index
            splash.message = "Loading FAISS index..."
            QApplication.processEvents()
            time.sleep(0.5)  # Simulate loading
            index = faiss.read_index(INDEX_PATH)
            
            # Load text data
            splash.message = "Loading story text..."
            QApplication.processEvents()
            time.sleep(0.3)  # Simulate loading
            with open(TEXTS_PATH, "r", encoding="utf-8") as f:
                raw_text = f.read().split("<|END|>\n")
            
            # Load sentence transformer
            splash.message = "Loading language model..."
            QApplication.processEvents()
            time.sleep(0.7)  # Simulate loading
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            rag_enabled = True
            splash.message = "Resources loaded successfully!"
            time.sleep(0.5)  # Show success message
            
        except Exception as e:
            print(f"Error loading RAG: {e}")
            rag_enabled = False
            
        finally:
            splash.close()
    else:
        print("RAG files not found. Using fallback responses.")
    
    return rag_enabled, index, raw_text, embedder

class ChatBubble(QFrame):
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setup_ui(text)
        
    def setup_ui(self, text):
        self.setMinimumWidth(200)
        self.setMaximumWidth(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        
        self.message_label = QLabel(text)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.message_label.setFont(QFont("Inter", 11))
        self.message_label.setStyleSheet("color: white;" if self.is_user else "color: #e1e1e3;")
        
        layout.addWidget(self.message_label)
        
        # Style based on sender
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #7289da;
                    border-radius: 18px;
                    border-bottom-right-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2f3136;
                    border-radius: 18px;
                    border-bottom-left-radius: 6px;
                    border: 1px solid #3a3c54;
                }
            """)

class ChatbotWindow(QMainWindow):
    """
    Main window for the AI Support Chatbot application with RAG integration.
    """
    def __init__(self, rag_enabled, index, raw_text, embedder):
        super().__init__()
        self.rag_enabled = rag_enabled
        self.index = index
        self.raw_text = raw_text
        self.embedder = embedder
        
        self.is_bot_typing = False
        self.setWindowTitle("Story Explainer Chatbot")
        self.init_ui()
        self.apply_styles()
        self.connect_signals()
        self.add_initial_message()
        self.center_and_resize()

    def init_ui(self):
        """
        Initializes the main UI components and layout.
        """
        # --- Central Widget and Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Status label to show RAG status
        status_text = "RAG: Enabled" if self.rag_enabled else "RAG: Disabled - Using fallback responses"
        self.status_label = QLabel(status_text)
        self.status_label.setFont(QFont("Inter", 9))
        self.status_label.setStyleSheet("color: #7289da;" if self.rag_enabled else "color: #ff6b6b;")
        self.status_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.status_label)

        # --- Chat Display Area ---
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("""
            QScrollArea {
                background-color: #25283b;
                border-radius: 15px;
                border: 1px solid #3a3c54;
            }
            QScrollBar:vertical {
                background: #25283b;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3a3c54;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #25283b;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(25, 25, 25, 25)
        self.chat_layout.setSpacing(18)
        self.chat_layout.addStretch()  # Add stretch to push content to top
        
        self.chat_area.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_area)

        # --- Input Controls Layout ---
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        # --- Reset Button ---
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Inter", 10, QFont.Bold))
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setToolTip("Clear the chat history")
        input_layout.addWidget(self.reset_button)

        # --- Message Input Field ---
        self.message_input = QLineEdit()
        self.message_input.setFont(QFont("Inter", 11))
        self.message_input.setPlaceholderText("Ask about the story...")
        self.message_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        input_layout.addWidget(self.message_input)

        # --- Send Button ---
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Inter", 10, QFont.Bold))
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setToolTip("Send your message")
        input_layout.addWidget(self.send_button)
        
        # --- Mic Button ---
        self.mic_button = QPushButton("🎤")
        self.mic_button.setFont(QFont("Arial", 14))
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.setToolTip("Use microphone (feature not implemented)")
        self.mic_button.setFixedSize(44, 44)
        input_layout.addWidget(self.mic_button)

        main_layout.addLayout(input_layout)

    def center_and_resize(self):
        """
        Resizes the window to a fraction of the screen size and centers it.
        """
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.4)
        height = int(screen.height() * 0.7)
        self.resize(width, height)
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

    def apply_styles(self):
        """
        Applies a modern, dark theme to the application using QSS (Qt Style Sheets).
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1c1c2e;
            }
           
            QLineEdit {
                background-color: #25283b;
                color: #e1e1e3;
                border-radius: 22px;
                border: 1px solid #3a3c54;
                padding: 10px 20px;
                height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #8a63f7;
            }
            QPushButton {
                background-color: #7289da;
                color: white;
                border-radius: 22px;
                padding: 10px 15px;
                border: none;
                height: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #677bc4;
            }
            QPushButton:pressed {
                background-color: #5b6eae;
            }
            #reset_button { background-color: #4f545c; }
            #reset_button:hover { background-color: #5a6069; }
            #mic_button { background-color: #25283b; border-radius: 22px; border: 1px solid #3a3c54; }
            #mic_button:hover { background-color: #3a3c54; }
        """)
        self.reset_button.setObjectName("reset_button")
        self.mic_button.setObjectName("mic_button")

    def connect_signals(self):
        """Connects widget signals to their corresponding handler methods."""
        self.send_button.clicked.connect(self.handle_send)
        self.message_input.returnPressed.connect(self.handle_send)
        self.reset_button.clicked.connect(self.reset_chat)
        self.mic_button.clicked.connect(self.mic_button_clicked)

    def add_initial_message(self):
        """Adds the initial welcome message from the bot to the chat."""
        self.append_message("Story Explainer", 
                           "Hello! I'm your story explainer assistant. Ask me anything about the story!", 
                           is_user=False)

    def handle_send(self):
        """
        Handles the logic for sending a message, showing the typing indicator,
        and generating a bot response.
        """
        if self.is_bot_typing:
            return  # Don't allow sending while bot is typing

        user_text = self.message_input.text().strip()
        if user_text:
            self.append_message("You", user_text, is_user=True)
            self.message_input.clear()
            self.show_typing_indicator_and_respond(user_text)

    def show_typing_indicator_and_respond(self, user_text):
        """Shows typing indicator, then gets and shows the bot response."""
        self.is_bot_typing = True
        self.send_button.setEnabled(False)
        
        # Append the "Typing..." message
        self.append_typing_indicator()
        QApplication.processEvents()  # Force UI update

        # Use QTimer to run the RAG process in the background
        QTimer.singleShot(100, lambda: self.process_rag_query(user_text))

    def process_rag_query(self, query):
        """Processes the user query using the RAG pipeline."""
        try:
            if self.rag_enabled:
                # Embed query
                query_vec = self.embedder.encode([query], convert_to_numpy=True)
                
                # Search top matches
                D, I = self.index.search(query_vec, k=2)
                context = "\n".join([self.raw_text[i] for i in I[0]])
                
                # Create prompt for LLM
                prompt = f"""You are a story explainer.
                Find the answer from the below story and explain simply in hindi.

                Story Context:
                {context}

                Question:
                {query}
                """
                
                # Call Groq API
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that explains stories in simple hindi."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                }

                response = requests.post(GROQ_URL, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    bot_response = result["choices"][0]["message"]["content"]
                else:
                    bot_response = "I encountered an error processing your request. Please try again."
            else:
                # Fallback response if RAG is not enabled
                bot_response = self.get_fallback_response(query)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            bot_response = "I encountered an error processing your request. Please try again."
            
        # Update UI with the response
        QTimer.singleShot(100, lambda: self.finish_rag_response(bot_response))

    def finish_rag_response(self, bot_response):
        """Finishes the RAG response process by updating the UI."""
        # Remove the typing indicator
        if hasattr(self, 'typing_indicator_widget'):
            self.typing_indicator_widget.deleteLater()
            del self.typing_indicator_widget

        # Append the actual bot response
        self.append_message("Story Explainer", bot_response, is_user=False)
        
        self.is_bot_typing = False
        self.send_button.setEnabled(True)

    def append_typing_indicator(self):
        """Adds a typing indicator to the chat."""
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create typing bubble
        typing_bubble = QFrame()
        typing_bubble.setMinimumWidth(100)
        typing_bubble.setMaximumWidth(200)
        typing_layout = QVBoxLayout(typing_bubble)
        typing_layout.setContentsMargins(15, 12, 15, 12)
        
        typing_label = QLabel("Typing...")
        typing_label.setFont(QFont("Inter", 11))
        typing_label.setStyleSheet("color: #96989d; font-style: italic;")
        
        typing_layout.addWidget(typing_label)
        typing_bubble.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 18px;
                border-bottom-left-radius: 6px;
                border: 1px solid #3a3c54;
            }
        """)
        
        # Add spacer to push to left
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        container_layout.addWidget(typing_bubble)
        container_layout.addWidget(spacer)
        
        # Add to chat layout and remember for removal
        self.typing_indicator_widget = container
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        self.scroll_to_bottom()

    def append_message(self, sender, message, is_user=False):
        """
        Appends a message to the chat display with correct alignment.
        - User messages: right-aligned with blue styling
        - Bot messages: left-aligned with green styling
        """
        # Create chat bubble
        bubble = ChatBubble(message, is_user)
        
        # Create container for alignment
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create spacer for alignment
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add widgets based on alignment
        if is_user:  # Right-align user messages
            container_layout.addWidget(spacer)
            container_layout.addWidget(bubble)
        else:        # Left-align bot messages
            container_layout.addWidget(bubble)
            container_layout.addWidget(spacer)
        
        # Insert into chat layout above the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scrolls the chat area to the bottom."""
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()))
            
    def get_fallback_response(self, user_text):
        """Fallback response generator if RAG is not available."""
        user_text_lower = user_text.lower()
        
        if "who" in user_text_lower:
            return "I'm sorry, I don't have the story context to answer that. Please ensure the RAG files are available."
        elif "what" in user_text_lower:
            return "Without the story context, I can't provide a detailed explanation."
        elif "where" in user_text_lower:
            return "Location details would be in the story, which I don't have access to."
        elif "why" in user_text_lower:
            return "I need the story context to explain the reasons behind events."
        elif "how" in user_text_lower:
            return "The process would be explained in the story, which I can't access."
        else:
            return "I'm a story explainer, but I don't have the story data. Please check that the RAG files are in place."

    def reset_chat(self):
        """Clears the chat display and adds the initial welcome message again."""
        # Clear all widgets except the stretch at the end
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Reset state and add initial message
        self.add_initial_message()
        self.is_bot_typing = False
        self.send_button.setEnabled(True)

    def mic_button_clicked(self):
        """Placeholder function for the microphone button."""
        self.append_message("System", "Microphone input is not yet implemented.", is_user=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create splash screen and load resources
    rag_enabled, index, raw_text, embedder = load_rag_resources()
    
    # Set font substitution
    QFont.insertSubstitution("Inter", "Arial")
    
    # Create and show main window
    window = ChatbotWindow(rag_enabled, index, raw_text, embedder)
    window.show()
    
    sys.exit(app.exec_())
