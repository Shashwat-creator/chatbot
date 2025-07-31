import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QDesktopWidget,
    QLabel, QFrame, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QTextCursor
from PyQt5.QtCore import Qt, QSize, QTimer

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
    Main window for the AI Support Chatbot application.
    This class sets up the user interface, styles, and signal-slot connections.
    """
    def __init__(self):
        super().__init__()
        self.is_bot_typing = False
        self.setWindowTitle("AI Support Chatbot")
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
        self.message_input.setPlaceholderText("Type your message here...")
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
            QTextEdit {
                background-color: red;
                color: #e0e0e0;
                border-radius: 15px;
                border: 1px solid #3a3c54;
                padding: 10px;
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
        self.append_message("AI Support Bot", "Hello! I'm your AI support assistant. How can I help you?", is_user=False)

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

        # Simulate bot thinking time and then respond
        QTimer.singleShot(1500, lambda: self.get_and_show_response(user_text))

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

    def get_and_show_response(self, user_text):
        """Removes typing indicator, gets bot response, and appends it."""
        # Remove the typing indicator
        if hasattr(self, 'typing_indicator_widget'):
            self.typing_indicator_widget.deleteLater()
            del self.typing_indicator_widget

        # Get and append the actual bot response
        bot_response = self.get_bot_response(user_text)
        self.append_message("AI Support Bot", bot_response, is_user=False)
        
        self.is_bot_typing = False
        self.send_button.setEnabled(True)

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

    def get_bot_response(self, user_text):
        """Generates a simple, rule-based response from the bot."""
        user_text_lower = user_text.lower()
        if "password" in user_text_lower:
            return "To reset your password, please visit the company's self-service portal. Would you like me to provide a link?"
        elif "internet" in user_text_lower or "wifi" in user_text_lower:
            return "I see you're having internet issues. Have you tried restarting your router? Unplug it for 30 seconds and plug it back in."
        elif "slow" in user_text_lower and ("computer" in user_text_lower or "pc" in user_text_lower):
            return "A slow computer can be frustrating. Please try closing unused applications and restarting your machine."
        elif "software" in user_text_lower:
            return "For software installation requests, please file a ticket with the IT department through the official portal. This ensures proper licensing and security."
        elif "thank" in user_text_lower or "thanks" in user_text_lower:
            return "You're welcome! Is there anything else I can assist you with?"
        else:
            return "I'm sorry, I'm not sure how to help with that. Could you please rephrase your issue?"

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
    QFont.insertSubstitution("Inter", "Arial")
    window = ChatbotWindow()
    window.show()
    sys.exit(app.exec_())
