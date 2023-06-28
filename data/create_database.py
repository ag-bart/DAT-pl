import sqlite3
import numpy as np
from typing import Set, Dict


class WordValidator:
    def __init__(self, lang_dictionary: str, model: str):

        self.lang_dictionary = lang_dictionary
        self.model = model
        self.words: Set[str] = set()
        self.vectors: Dict[str, np.ndarray] = {}

    def load_dictionary(self):
        with open(self.lang_dictionary, "r", encoding="utf-8") as f:
            self.words = {word.strip() for word in f}

    def process_model(self):
        if not self.words:
            self.load_dictionary()

        with open(self.model, "r", encoding="utf8") as f:
            for line in f:
                tokens = line.split(" ")
                word = tokens[0]
                if word in self.words:
                    vector = np.array([float(val) for val in tokens[1:]])
                    self.vectors[word] = vector


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
