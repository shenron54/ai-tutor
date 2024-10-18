import sqlite3
from datetime import datetime

class ChatHistory:
    def __init__(self, db_name='chat_history.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                         (timestamp TEXT, role TEXT, content TEXT)''')

    def add_message(self, role, content):
        timestamp = datetime.now().isoformat()
        self.c.execute("INSERT INTO chat_history VALUES (?, ?, ?)", 
                       (timestamp, role, content))
        self.conn.commit()

    def get_all_messages(self):
        self.c.execute("SELECT * FROM chat_history ORDER BY timestamp")
        return self.c.fetchall()

    def close(self):
        self.conn.close()

# Usage
# chat_history = ChatHistory()
# chat_history.add_message("user", "Hello")
# chat_history.add_message("assistant", "Hi there!")
# all_messages = chat_history.get_all_messages()
# chat_history.close()