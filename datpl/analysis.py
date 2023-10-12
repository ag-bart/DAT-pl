from itertools import combinations
from typing import List
from scipy.spatial.distance import cosine


class DatComputer:
    def __init__(self, database_manager):
        """
        Initialize the DatComputer instance.

        Parameters:
            database_manager (DatabaseManager):
                An instance of DatabaseManager for database interaction.
        """
        self.db = database_manager

        self._minimum_words = 7

    @property
    def minimum_words(self):
        return self._minimum_words

    @minimum_words.setter
    def minimum_words(self, value):
        if not isinstance(value, int):
            raise ValueError('minimum value must be of type int')
        if value <= 0:
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
            return [
                self.distance(word1, word2)
                for word1, word2 in combinations(subset, 2)
            ]
        return []  # Not enough valid words

    @staticmethod
    def compute_dat_score(distances):
        if len(distances) > 0:
            return (sum(distances) / len(distances)) * 100
        return None

    def dataset_compute_dat_score(self, data):
        """return mean distances multiplied by 100 for each participant"""

        dat_distances = [self.dat(answer) for answer in data]
        dat_scores = list(map(self.compute_dat_score, dat_distances))

        return dat_distances, dat_scores
