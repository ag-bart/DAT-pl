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
        self.dat_distances = None
        self.dat_values = None

    def distance(self, word1: str, word2: str):
        """
        Compute the cosine distance between two words using their word vectors.

        Returns:
            float: The cosine distance between the two words (between 0 and 2).
        """

        return cosine(self.db.get_word_vector(word1),
                      self.db.get_word_vector(word2))

    def dat(self, words: List[str], minimum: int = 7) -> List[float]:
        """
        Compute pairwise distances for a list of words.
        Distances are computed for the first n valid words found in the list,
        where n is the value set in the minimum parameter.

        Parameters:
            words (List[str]):
                The list of words to compute distances for.
            minimum (int):
                The minimum number of valid words needed to compute distances.

        Returns:
            List[float]: A list of distances between valid word pairs.
                Empty if the wordlist contained fewer valid words than minimum.
        """

        if len(words) >= minimum:
            subset = words[:minimum]
        else:
            return []  # Not enough valid words

        distances = [self.distance(word1, word2)
                     for word1, word2 in combinations(subset, 2)]
        return distances

    @round_output
    def compute_dat(self):
        """return mean distances multiplied by 100 for each participant"""
        self.dat_values = [((sum(distances) / len(distances)) * 100)
                           if len(distances) != 0 else None
                           for distances in self.distances_by_pairs()]

        return self.dat_values

    def distances_by_pairs(self):
        """
        Compute pairwise distances for all answers in the processed data.

        Returns:
            List[List[float]]:
                A list of lists with distances for each answer's word pairs.
        """
        self.dat_distances = [self.dat(answer) for answer in self.data]
        return self.dat_distances

    def save_distances(self):
        """Save computed distances to a CSV file in the 'results' folder."""
        columns = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']
        column_names = [f'{c1}-{c2}'
                        for c1, c2 in combinations(columns, 2)]

        date = time.strftime('%Y-%b-%d__%H_%M_%S', time.localtime())
        file_name = f'dat_distances{date}.csv'
        output_path = os.path.join('results', file_name)

        if not os.path.exists(output_path):
            os.makedirs('results', exist_ok=True)

        if not self.dat_distances:
            self.compute_dat()

        df = pd.DataFrame(self.dat_distances, columns=column_names)
        df['DAT'] = self.dat_values
        df.to_csv(output_path)
        print('csv file saved in /results.')
