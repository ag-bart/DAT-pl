import sqlite3
import re
from typing import Tuple, Optional
from collections import OrderedDict
import numpy as np


class DatabaseManager:
    def __init__(self, db_path):
        """
        Initialize the DatabaseManager instance.

        Parameters:
            db_path (str): Path to the SQLite database file.
        """
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

    def get_words(self):
        """
        Retrieve and return the list of words from the vector database.

        Returns:
            List[str]: A list of words stored in the database.
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute('SELECT word FROM vectors')
        words = [row[0] for row in cursor.fetchall()]

        self.disconnect()
        return words

    def get_word_vector(self, word: str) -> Optional[np.ndarray]:
        """
        Retrieve the word vector from the database for the given word.

        Parameters:
            word (str): The word to retrieve the vector for.

        Returns:
            Optional[numpy.ndarray]:
                The word vector as a NumPy array if found, else None.
        """

        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute('''SELECT vector FROM vectors WHERE word=?''', (word,))
        result = cursor.fetchone()

        if result is not None:
            vector_data = np.frombuffer(result[0])
            return vector_data

        return None


class DataProcessor:
    def __init__(self, words):
        """
        Initialize the DataProcessor instance.

        Parameters:
            words (List[str]): a list of valid Polish words.
        """
        self.words = words

    @staticmethod
    def clean(word: str):
        if not isinstance(word, str):
            raise ValueError("Input word must be a string.")
        cleaned = re.sub(r'[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+', '', word.lower())
        cleaned = cleaned.strip()
        return cleaned if len(cleaned) > 1 else ' '

    def validate(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Validate the given word against the database.

        Parameters:
            word (str): The word to validate.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                A tuple (word, None) if word is found in the database,
                or (None, word) if not found.
        """
        cleaned = self.clean(word)

        if cleaned in self.words:
            return cleaned, None  # valid word
        return None, cleaned  # invalid word

    def process_answer(self, answer):

        unique_words = list(OrderedDict.fromkeys(answer))
        valid, invalid = zip(*(self.validate(word) for word in unique_words))
        valid_list = [word for word in valid if word is not None]
        invalid_list = [word for word in invalid if word is not None]

        return valid_list, invalid_list

    def process_dataset(self, data):
        """
        Process the dataset by cleaning, validating,
        and returning the processed data.

        Returns:
            Tuple[List[List[str]], Dict[int, List[str]]]:
                A tuple containing the processed dataset
                and a dictionary of invalid words by answer index.
        """

        processed_dataset, invalid_words = [], {}

        for i, answer in enumerate(data):
            valid_list, invalid_list = self.process_answer(answer)
            processed_dataset.append(valid_list)
            invalid_words[i] = invalid_list

        invalid_words = {k: v for k, v in invalid_words.items() if v}

        return processed_dataset, invalid_words
