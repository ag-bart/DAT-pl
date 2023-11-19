import sqlite3
import re
from typing import Tuple, Optional, List, Dict
from collections import OrderedDict

import numpy as np

ParsedWords = Dict[str, List[str]]



class DatabaseManager:
    def __init__(self, db_path: str):
        """
        Initialize  DatabaseManager instance.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """
        Establish a connection to the SQLite database.

        :raises ConnectionError: If there is an error connecting to the database.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as exc:
            raise ConnectionError(
                f"Error connecting to the database: {str(exc)}") from exc

    def disconnect(self):
        """
        Close the connection to the database.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_words(self) -> List[str]:
        """
        Retrieve and return the list of words from the vector database.

        :return: A list of words stored in the database.
        :rtype: List[str]
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
        Retrieve word vector from the database for a given word.

        :param word: The word to retrieve the vector for.
        :type word: str

        :return: The word vector as a NumPy array if found, else None.
        :rtype: Optional[numpy.ndarray]
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
    def __init__(self, words: List[str]):
        """
        Initialize DataProcessor instance.

        :param words: A list of valid Polish words.
        :type words: List[str]
        """
        self.words = words

    @staticmethod
    def clean(word: str) -> str:
        """
        Clean a word by removing non-alphabetic characters and converting it to lowercase.

        :param word: The word to clean.
        :type word: str

        :return: The cleaned word.
        :rtype: str
        """
        if not isinstance(word, str):
            raise ValueError("Input word must be a string.")

        cleaned = re.sub(
            r'[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+', '', word.lower()).strip()

        return cleaned if len(cleaned) > 1 else ''

    def validate(self, word: str) -> Tuple[str, str]:
        """
        Validate a word against the database.

        :param word: The word to validate.
        :type word: str

        :return: A tuple (valid_word, '') if the word is found in the database, or ('', invalid_word) if not found.
        :rtype: Tuple[str, str]
        """
        cleaned = self.clean(word)

        if cleaned in self.words:
            return cleaned, ''  # valid word
        return '', cleaned  # invalid word

    def process_words(self, words: List[str]) -> ParsedWords:
        """
        Process a list of words into valid and invalid words.

        :param words: The list of words to process.
        :type words: List[str]

        :return: A dictionary containing two keys:
            - 'valid_words': List of valid words.
            - 'invalid_words': List of invalid words.
        :rtype: Dict[str, List[str]]
        """
        unique_words = list(OrderedDict.fromkeys(words))
        result = [self.validate(word) for word in unique_words]

        valid_list = [word for word, _ in result if word]
        invalid_list = [word for _, word in result if word]

        return {'valid_words': valid_list, 'invalid_words': invalid_list}

    def process_dataset(self, data) -> Dict[str, ParsedWords]:
        """
        Clean and validate a dataset of DAT responses.

        :param data: A dictionary of participants' word sequences, where each participant is identified by a unique key.
        :type data: Dict[str, List[str]]

        :return: A dictionary containing participant IDs and their responses split into a dictionary of valid and invalid words.
        :rtype: Dict
        """

        processed_dataset = {}

        for p_id, response in data.items():
            result = self.process_words(response)
            processed_dataset[p_id] = {
                'valid_words': result['valid_words'],
                'invalid_words': result['invalid_words']}

        return processed_dataset

    @staticmethod
    def extract_valid_words(
            dataset: Dict[str, ParsedWords]) -> Dict[str, List[str]]:
        """
        Extract valid words from the processed dataset.

        :param dataset: The processed dataset containing valid and invalid words.
        :type dataset: Dict

        :return: A dictionary containing participant IDs and their valid words.
        :rtype: Dict[str, List[str]]
        """
        return {
           p_id: response['valid_words'] for p_id, response in dataset.items()
        }

