import sqlite3
from typing import List, Optional
import numpy as np


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as exc:
            raise ConnectionError(
                f"Error connecting to the database: {str(exc)}") from exc

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_words(self) -> List[str]:
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('SELECT word FROM vectors')
        words = [row[0] for row in cursor.fetchall()]
        return words

    def get_word_vector(self, word: str) -> Optional[np.ndarray]:
        """Retrieve word vector from the database for a given word."""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute('''SELECT vector FROM vectors WHERE word=?''', (word,))
        result = cursor.fetchone()

        if result is not None:
            vector_data = np.frombuffer(result[0])
            return vector_data

        return None