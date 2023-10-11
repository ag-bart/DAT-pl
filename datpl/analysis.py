from itertools import combinations
from typing import List
import os
import time
import pandas as pd
from scipy.spatial.distance import cosine
from datpl.decorators import round_output


class DatComputer:
    def __init__(self, database_manager, processed_data):
        """
        Initialize the DatComputer instance.

        Parameters:
            database_manager (DatabaseManager):
                An instance of DatabaseManager for database interaction.
            processed_data (List[List[str]]):
                The data to compute distances for.
                Processing is implemented in the DataProcessor class.
        """
        self.db = database_manager
        self.data = processed_data
        self._minimum_words = 7

        self.dat_distances = None
        self.dat_scores = None

    @property
    def minimum_words(self):
        return self._minimum_words

    @minimum_words.setter
    def minimum_words(self, value):
        if not isinstance(value, int):
            raise ValueError('minimum value must be of type int')
        if value < 0:
            raise ValueError('minimum value must be greater than 0')
        self._minimum_words = value

    def distance(self, word1: str, word2: str):
        """
        Compute the cosine distance between two words using their word vectors.

        Returns:
            float: The cosine distance between the two words (between 0 and 2).
        """

        return cosine(self.db.get_word_vector(word1),
                      self.db.get_word_vector(word2))

    def dat(self, words: List[str]) -> List[float]:
        """
        Compute pairwise distances for a list of words.
        Distances are computed for the first n valid words found in the list,
        where n is the value set in the minimum parameter.

        Parameters:
            words (List[str]):
                The list of words to compute distances for.

        Returns:
            List[float]: A list of distances between valid word pairs.
                Empty if the wordlist contained fewer valid words than minimum.
        """

        if len(words) >= self.minimum_words:
            subset = words[:self.minimum_words]
        else:
            return []  # Not enough valid words

        distances = [self.distance(word1, word2)
                     for word1, word2 in combinations(subset, 2)]
        return distances

    def dataset_distances(self):
        """
        Compute pairwise distances for all answers in the processed data.

        Returns:
            List[List[float]]:
                Distances computed for each row in the dataset.
        """
        self.dat_distances = [self.dat(answer) for answer in self.data]
        return self.dat_distances

    @round_output
    def dataset_compute_dat(self):
        """return mean distances multiplied by 100 for each participant"""
        self.dat_scores = [((sum(distances) / len(distances)) * 100)
                           if len(distances) > 0 else None
                           for distances in self.dataset_distances()]

        return self.dat_scores

    def save_results(self):
        """Save computed distances to a CSV file in the 'results' folder."""
        columns = ['W'+str(n) for n in range(1, self.minimum_words+1)]

        column_names = [f'{c1}-{c2}'
                        for c1, c2 in combinations(columns, 2)]

        date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
        file_name = f'dat_distances{date}.csv'
        output_path = os.path.join('results', file_name)

        if not os.path.exists(output_path):
            os.makedirs('results', exist_ok=True)

        if not self.dat_distances:
            self.dataset_compute_dat()

        df = pd.DataFrame(self.dat_distances, columns=column_names)
        df['DAT'] = self.dat_scores
        df.to_csv(output_path)
        print('csv file saved in /results.')
