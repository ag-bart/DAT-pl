import sqlite3
import os
import argparse
from typing import Set, Dict
import numpy as np


class ModelProcessor:
    def __init__(self, lang_dictionary: str, model: str):
        """
        Initialize the ModelProcessor instance.

        Parameters:
            lang_dictionary: path to file containing the dictionary.
            model: path to file containing the GloVe model.
        """
        self.lang_dictionary = lang_dictionary
        self.model = model
        self.words: Set[str] = set()
        self.vectors: Dict[str, np.ndarray] = {}

    def load_dictionary(self):
        try:
            with open(self.lang_dictionary, 'r',
                      encoding='utf-8') as dict_file:
                self.words = {word.strip() for word in dict_file}

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f'Language dictionary file not found: '
                f'{self.lang_dictionary}') from exc

        except Exception as exc:
            raise RuntimeError(
                f'Error loading language dictionary: {exc}') from exc

    def process_model(self):
        """
        Extract from model only the words found in the language dictionary.
        Store vectors for valid words in the WordValidator instance.
        """
        if not self.words:
            self.load_dictionary()

        try:
            with open(self.model, 'r', encoding='utf-8') as model_file:
                for line in model_file:
                    tokens = line.split(' ')
                    word = tokens[0]
                    if word in self.words:
                        vector = np.array([float(val) for val in tokens[1:]])
                        self.vectors[word] = vector

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f'Word vectors model file not found: {self.model}') from exc

        except Exception as exc:
            raise RuntimeError(
                f'Error processing word vectors model: 'f'{exc}') from exc


def create_vectors_database(database_path: str,
                            dict_path: str,
                            model_path: str):

    if not os.path.exists(database_path):

        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE
                              vectors (word VARCHAR(40) PRIMARY KEY, vector BLOB)''')

            validator = ModelProcessor(lang_dictionary=dict_path,
                                       model=model_path)
            validator.process_model()

            for valid_word, word_vector in validator.vectors.items():
                vector_data = word_vector.tobytes()

                cursor.execute(
                    '''INSERT INTO vectors (word, vector) VALUES (?, ?)''',
                    (valid_word, vector_data))

            conn.commit()
            conn.close()

        except Exception as exc:
            raise RuntimeError(f'Error creating the database: {exc}') from exc
    else:
        print(f'Database already exists at: {database_path}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a database of word vectors.")
    parser.add_argument("--database-path",
                        type=str, required=True,
                        help=" Target path to the database file")
    parser.add_argument("--dict-path",
                        type=str, required=True,
                        help="Path to the Polish dictionary file")
    parser.add_argument("--model-path",
                        type=str, required=True,
                        help="Path to the GloVe model file")

    args = parser.parse_args()
    create_vectors_database(
        database_path=args.database_path,
        dict_path=args.dict_path,
        model_path=args.model_path)
