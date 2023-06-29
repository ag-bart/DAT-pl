import sqlite3
import numpy as np
import pandas as pd
from typing import List, Optional


class DatabaseManager:

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)

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
        # Query the database for a specific word
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute('''SELECT vector FROM vectors WHERE word=?''', (word,))
        result = cursor.fetchone()

        if result is not None:
            vector_data = np.frombuffer(result[0])
            return vector_data

        return None


def read_data(path_to_file):
    if path_to_file.endswith('.xlsx'):
        df_upload = pd.read_excel(path_to_file, header=None, dtype=str)

    elif path_to_file.endswith('.csv'):
        df_upload = pd.read_csv(path_to_file, header=None, dtype=str, sep=';')

    else:
        raise ValueError(
            'Unsupported file type. Only XLSX and CSV files are supported.')

    df_upload = df_upload.fillna(value=' ')
    dat_data = df_upload.values.tolist()

    return dat_data
