from itertools import combinations
from typing import List, Optional
from collections import namedtuple
from scipy.spatial.distance import cosine
from .processing import DatabaseManager


DatResult = namedtuple("DatResult", ["distances", "score"])


class DatComputer:
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize the DatComputer instance.

        Parameters:
            database_manager (DatabaseManager):
                An instance of DatabaseManager for database interaction.
        """
        self.db = database_manager

        self._minimum_words = 7

    @property
    def minimum_words(self) -> int:
        """Return the minimum number of words for distance calculation."""
        return self._minimum_words

    @minimum_words.setter
    def minimum_words(self, value: int):
        if not isinstance(value, int):
            raise ValueError('minimum value must be of type int')
        if value <= 1:
            raise ValueError('minimum value must be greater than 1')
        self._minimum_words = value

    def distance(self, word1: str, word2: str) -> float:
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

            return [self.distance(word1, word2)
                    for word1, word2 in combinations(subset, 2)]
        return []  # Not enough valid words

    @staticmethod
    def compute_dat_score(distances: List[float]) -> Optional[float]:
        """Calculate the DAT score based on distances."""
        if len(distances) > 0:
            return (sum(distances) / len(distances)) * 100
        return None

    def dataset_compute_dat_score(self, data) -> List[DatResult]:
        """Compute DAT scores for a dataset of participants' answers.

        Parameters:
            data (List[List[str]]):
                A list of answers, where each answer is a list of words.

        Returns:
            List[DatResult]:
            A list of DatResult named tuples, each containing distances
            and scores for a set of words in an answer.
        """

        return [
            DatResult(distances=self.dat(answer),
                      score=self.compute_dat_score(self.dat(answer)))
            for answer in data
        ]
