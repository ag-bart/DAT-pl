import itertools
from typing import List
import scipy.spatial.distance


class DistanceAnalyzer:
    def __init__(self, database_manager, word_cleaner):
        """
        Initialize the DistanceAnalyzer instance.

        Parameters:
            database_manager (DatabaseManager):
                An instance of the DatabaseManager class.
            word_cleaner (WordCleaner):
                An instance of the WordCleaner class.
        """
        self.db = database_manager
        self.cleaner = word_cleaner

    def distance(self, word1: str, word2: str):
        """
        Compute the cosine distance between two words using their word vectors.

        Returns:
            float: The cosine distance between the two words (between 0 and 2).
        """

        return scipy.spatial.distance.cosine(self.db.get_word_vector(word1),
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
                Empty if the word list contained less valid words than minimum.
        """
        uniques = []
        for word in words:
            valid, _ = self.cleaner.validate(word)
            if valid and valid not in uniques:
                uniques.append(valid)

        # Keep subset of words
        if len(uniques) >= minimum:
            subset = uniques[:minimum]
        else:
            return []  # Not enough valid words

        distances = []
        # Compute distances between each pair of words
        for word1, word2 in itertools.combinations(subset, 2):
            dist = self.distance(word1, word2)
            distances.append(dist)
        return distances
