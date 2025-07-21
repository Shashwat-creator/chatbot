import sys
import speech_recognition as sr
from PyQt5 import QtWidgets, QtGui, QtCore

class ChatbotUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 🖥️ Window
        self.setWindowTitle("🌙 Fancy Dark Chatbot")
        self.setGeometry(200, 100, 900, 650)

        # 🌌 Dark theme stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #F1F1F1;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border-radius: 18px;
                padding: 12px 18px;
                font-size: 16px;
                border: 1px solid #3C3C3C;
            }
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 18px;
                padding: 10px 18px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QTextEdit {
                background-color: #252526;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 10px;
                font-size: 15px;
                border: 1px solid #3C3C3C;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #3A86FF;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5fa3ff;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 🔹 Top bar with title and reset button
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("💬 Fancy Dark Chatbot")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        top_bar.addWidget(title)

        # Reset Chat button
        self.reset_button = QtWidgets.QPushButton("🔄 Reset Chat")
        self.reset_button.setFixedWidth(150)
        self.reset_button.clicked.connect(self.reset_chat)
        top_bar.addStretch(1)
        top_bar.addWidget(self.reset_button)

        main_layout.addLayout(top_bar)

        # 🔹 Chat history
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.chat_history, stretch=1)

        # 🔹 Bottom input area
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.query_input = QtWidgets.QLineEdit()
        self.query_input.setPlaceholderText("Message Chatbot…")
        self.query_input.returnPressed.connect(self.on_send)  # Enter key
        bottom_layout.addWidget(self.query_input, stretch=1)

        self.mic_button = QtWidgets.QPushButton("🎤")
        self.mic_button.setFixedWidth(50)
        self.mic_button.clicked.connect(self.on_mic)
        bottom_layout.addWidget(self.mic_button)

        self.send_button = QtWidgets.QPushButton("➤")
        self.send_button.setFixedWidth(60)
        self.send_button.clicked.connect(self.on_send)
        bottom_layout.addWidget(self.send_button)

        main_layout.addLayout(bottom_layout)

    # 🧹 Reset chat history
    def reset_chat(self):
        self.chat_history.clear()
        self.append_message("ℹ️", "Chat history cleared.", is_user=False)

    # Append message with styled bubble
    def append_message(self, sender, message, is_user=False):
        if is_user:
            bubble_color = "#0B93F6"  # blue for user
            text_color = "#FFFFFF"
            align = "right"
        else:
            bubble_color = "#3A3B3C"
            text_color = "#FFFFFF"
            align = "left"

        html = f"""
        <div style="background-color:{bubble_color};
                    color:{text_color};
                    border-radius:12px;
                    padding:10px;
                    margin:6px;
                    max-width:75%;
                    float:{align};
                    clear:both;">
            <b>{sender}:</b> {message}
        </div>
        <div style="clear:both;"></div>
        """
        self.chat_history.insertHtml(html)
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def on_send(self):
        query = self.query_input.text().strip()
        if not query:
            return
        self.append_message("You", query, is_user=True)
        self.query_input.clear()

        # 🔥 Replace with your RAG or API logic
        answer = f"This is a sample response to: {query}"
        self.append_message("Bot", answer, is_user=False)

    def on_mic(self):
        self.append_message("🎤 Mic", "Listening...")
        QtWidgets.QApplication.processEvents()
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, phrase_time_limit=5)
                text = recognizer.recognize_google(audio)
                self.query_input.setText(text)
                self.on_send()
        except sr.UnknownValueError:
            self.append_message("⚠️", "Sorry, I couldn't understand.", is_user=False)
        except sr.RequestError:
            self.append_message("⚠️", "Speech recognition error.", is_user=False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ChatbotUI()
    window.show()
    sys.exit(app.exec_())
