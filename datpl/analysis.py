from itertools import combinations
from typing import List, Optional, Dict
from collections import namedtuple

from scipy.spatial.distance import cosine

from .processing import DatabaseManager


DatResult = namedtuple("DatResult", ["distances", "score"])


class DatComputer:
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize DatComputer instance.

        :param database_manager: An instance of DatabaseManager for database interaction.
        :type database_manager: DatabaseManager
        """
        self.db = database_manager

        self._minimum_words = 7

    @property
    def minimum_words(self) -> int:
        """
        Get the minimum number of words required for distance calculation.

        :return: The minimum number of words for distance calculation.
        :rtype: int
        """
        return self._minimum_words

    @minimum_words.setter
    def minimum_words(self, value: int):
        """
        Set the minimum number of words required for distance calculation.

        :param value: The minimum value to set (must be an integer greater than 1).
        :type value: int

        :raises ValueError: If the provided value is not an integer or is less than or equal to 1.
        """
        if not isinstance(value, int):
            raise ValueError('minimum value must be of type int')
        if value <= 1:
            raise ValueError('minimum value must be greater than 1')
        self._minimum_words = value

    def distance(self, word1: str, word2: str) -> float:
        """
        Calculate the cosine distance between two words using their word vectors.

        :param word1: The first word.
        :type word1: str
        :param word2: The second word.
        :type word2: str

        :return: The cosine distance between the two words (a value between 0 and 2).
        :rtype: float
        """
        return cosine(self.db.get_word_vector(word1),
                      self.db.get_word_vector(word2))

    def dat(self, words: List[str]) -> List[float]:
        """
        Calculate pairwise distances for a list of words.

        Distances are computed for the first 'n' valid words found in the list, where 'n' is the minimum value set.

        :param words: The list of words to compute distances for.
        :type words: List[str]

        :return: A list of distances between valid word pairs. If the word list contains fewer valid words than the minimum, an empty list is returned.
        :rtype: List[float]
        """
        if len(words) >= self.minimum_words:
            subset = words[:self.minimum_words]

            return [self.distance(word1, word2)
                    for word1, word2 in combinations(subset, 2)]
        return []  # Not enough valid words

    @staticmethod
    def compute_dat_score(distances: List[float]) -> Optional[float]:
        """
        Calculate the DAT (Divergent Association Task) score based on distances.

        :param distances: A list of distances between valid word pairs.
        :type distances: List[float]

        :return: The computed DAT score, or None if no distances are available.
        :rtype: Optional[float]
        """
        if len(distances) > 0:
            return (sum(distances) / len(distances)) * 100
        return None

    def dataset_compute_dat_score(self, data: Dict) -> Dict[str, DatResult]:
        """
        Compute DAT scores for a dataset of participants' answers.

        :param data: A dictionary of participants' answers, where each answer is a list of words.
        :type data: Dict[str, List[str]]

        :return: A dictionary containing participant IDs as keys and DatResult named tuples as values, each containing computed distances and DAT score.
        :rtype: Dict[str, DatResult]
        """

        scored_dataset = {}
        for i, answer in data.items():
            scored_dataset[i] = DatResult(
                distances=self.dat(answer),
                score=self.compute_dat_score(self.dat(answer))
            )
        return scored_dataset
