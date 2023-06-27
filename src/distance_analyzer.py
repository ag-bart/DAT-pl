"""Compute score for Divergent Association Task,
a quick and simple measure of creativity
(Copyright 2021 Jay Olson; see LICENSE)

Modifications and polish adaptation
Copyright 2022 Agnieszka Bartkowska
"""
import scipy.spatial.distance
import itertools


class DistanceAnalyzer:

    def __init__(self, database_manager, word_cleaner):
        self.db = database_manager
        self.cleaner = word_cleaner

    def distance(self, word1, word2):
        """Compute cosine distance (0 to 2) between two words"""

        return scipy.spatial.distance.cosine(self.db.get_word_vector(word1),
                                             self.db.get_word_vector(word2))

    def dat(self, words, minimum=7):
        """Compute DAT score"""

        # Keep only valid unique words
        uniques = []
        for word in words:
            valid = self.cleaner.validate(word)
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
