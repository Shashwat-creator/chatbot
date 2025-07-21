import sys, os, requests, faiss
from PyQt5 import QtWidgets, QtGui, QtCore
import speech_recognition as sr
from sentence_transformers import SentenceTransformer

# ✅ Load RAG resources
index = faiss.read_index("sop_index.faiss")
with open("sop_texts.txt", "r", encoding="utf-8") as f:
    raw_text = f.read().split("<|END|>\n")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ GROQ API
GROQ_API_KEY = "ddddd"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ChatbotUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🌙 Fancy Dark Chatbot (with RAG)")
        self.setGeometry(200, 100, 900, 650)

        # Dark theme style
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
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 🔹 Top bar
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("💬 Fancy Dark Chatbot")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        top_bar.addWidget(title)

        self.reset_button = QtWidgets.QPushButton("🔄 Reset Chat")
        self.reset_button.setFixedWidth(150)
        self.reset_button.clicked.connect(self.reset_chat)
        top_bar.addStretch(1)
        top_bar.addWidget(self.reset_button)
        main_layout.addLayout(top_bar)

        # 🔹 Chat history
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)
        main_layout.addWidget(self.chat_history, stretch=1)

        # 🔹 Bottom input area
        bottom_layout = QtWidgets.QHBoxLayout()
        self.query_input = QtWidgets.QLineEdit()
        self.query_input.setPlaceholderText("Type your message…")
        self.query_input.returnPressed.connect(self.on_send)
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

    # 🧹 Reset chat
    def reset_chat(self):
        self.chat_history.clear()
        self.append_message("ℹ️", "Chat history cleared.", is_user=False)

    def append_message(self, sender, message, is_user=False):
        if is_user:
            bubble_color = "#0B93F6"
            align = "right"
        else:
            bubble_color = "#3A3B3C"
            align = "left"
        html = f"""
        <div style="background-color:{bubble_color};
                    color:white;
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

        # ---- 🔥 RAG Pipeline ----
        try:
            # Embed query and search top docs
            query_vec = embedder.encode([query], convert_to_numpy=True)
            D, I = index.search(query_vec, k=2)
            context = "\n".join([raw_text[i] for i in I[0]])

            # Prepare prompt for Groq API
            prompt = f"""You are a helpful assistant.
Find the answer from the below story and explain simply in language given in question.

Story Context:
{context}

Question:
{query}
"""

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }

            response = requests.post(GROQ_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
            else:
                answer = f"Error {response.status_code}: {response.text}"
        except Exception as e:
            answer = f"⚠️ Error: {e}"

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
