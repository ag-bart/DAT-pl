import sqlite3
import os
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
                            dict_path: str = 'words.txt',
                            model_path: str = 'glove_100_3_polish.txt'):

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
            print('Database created successfully.')

        except Exception as exc:
            raise RuntimeError(f'Error creating the database: {exc}') from exc
    else:
        print(f'Database already exists at: {database_path}')

if __name__ == "__main__":
    # Example usage:
    create_vectors_database(database_path='vectors.db',
                            dict_path='words.txt',
                            model_path='glove_100_3_polish.txt')
