import os
import sqlite3
from typing import Set, Dict
import pandas as pd
import numpy as np


class WordValidator:
    def __init__(self, lang_dictionary: str, model: str):

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




validator = WordValidator(lang_dictionary='words.txt',
                          model='glove_100_3_polish.txt')
validator.process_model()


conn = sqlite3.connect('vectors.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE vectors (word TEXT PRIMARY KEY, vector BLOB)''')

for valid_word, word_vector in validator.vectors.items():
    vector_data = word_vector.tobytes()

    cursor.execute('''INSERT INTO vectors (word, vector) VALUES (?, ?)''',
                   (valid_word, vector_data))

conn.commit()
conn.close()
