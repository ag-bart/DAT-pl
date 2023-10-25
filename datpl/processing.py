import sqlite3
import re
from typing import Tuple, Optional, List, Dict
from collections import OrderedDict
import numpy as np


ParsedWords = Dict[str, List[str]]


class DatabaseManager:
    def __init__(self, db_path: str):
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

    def get_words(self) -> List[str]:
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
    def __init__(self, words: List[str]):
        """
        Initialize the DataProcessor instance.

        Parameters:
            words (List[str]): a list of valid Polish words.
        """
        self.words = words

    @staticmethod
    def clean(word: str) -> str:
        if not isinstance(word, str):
            raise ValueError("Input word must be a string.")

        cleaned = re.sub(
            r'[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+', '', word.lower()).strip()

        return cleaned if len(cleaned) > 1 else ''

    def validate(self, word: str) -> Tuple[str, str]:
        """
        Validate the given word against the database.

        Parameters:
            word (str): The word to validate.

        Returns:
            Tuple[str, str]:
                A tuple (word, '') if word is found in the database,
                or ('', word) if not found.
        """
        cleaned = self.clean(word)

        if cleaned in self.words:
            return cleaned, ''  # valid word
        return '', cleaned  # invalid word

    def process_words(self, words: List[str]) -> ParsedWords:
        """
        Process a list of given words into valid and invalid words.

        Parameters:
            words (List[str]): The list of words to process.

        Returns:
            Dict[str, List[str]]:
                A dictionary containing two keys:
                - 'valid_words': List of valid words.
                - 'invalid_words': List of invalid words.
        """
        unique_words = list(OrderedDict.fromkeys(words))
        result = [self.validate(word) for word in unique_words]

        valid_list = [word for word, _ in result if word]
        invalid_list = [word for _, word in result if word]

        return {'valid_words': valid_list, 'invalid_words': invalid_list}

    def process_dataset(self, data) -> Dict[str, ParsedWords]:
        """
        Clean and validate a dataset of DAT responses.

        Parameters:
            data (Dict[str, List[str]]):
                dictionary of participants' word sequences,
                where each participant is identified by a unique key.

        Returns:
            Dict[str, ParsedWords]
                A dictionary containing participant IDs
                and their response split into a dictionary of valid and
                invalid words.
        """
        if isinstance(data, list):
            data = {str(i): words for i, words in enumerate(data)}

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

        Parameters:
            dataset (Dict[str, ParsedWords]):
                The processed dataset containing valid and invalid words.

        Returns:
            Dict[str, List[str]]:
                A dictionary containing participant IDs and their valid words.
        """
        return {
           p_id: response['valid_words'] for p_id, response in dataset.items()
        }

