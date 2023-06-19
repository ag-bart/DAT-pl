"""Compute score for Divergent Association Task,
a quick and simple measure of creativity
(Copyright 2021 Jay Olson; see LICENSE)

Modifications and polish adaptation
Copyright 2022 Agnieszka Bartkowska
"""


import re
import itertools
import numpy
import scipy.spatial.distance


class Model:
    """Create model to compute DAT"""

    def __init__(
            self,
            model="glove_100_3_polish.txt",
            dictionary="words.txt",
            pattern="^[a-ząćęłńóśźż][a-ząćęłńóśźż-]*[a-ząćęłńóśźż]$"
                 ):
        """Join model and words matching pattern in dictionary"""

        self.candidates = []

        # Keep unique words matching pattern from file
        words = set()
        with open(dictionary, "r", encoding="utf8") as f:
            for line in f:
                if re.match(pattern, line):
                    words.add(line.rstrip("\n"))

        # Join words with model
        vectors = {}
        with open(model, "r", encoding="utf8") as f:
            for line in f:
                tokens = line.split(" ")
                word = tokens[0]
                if word in words:
                    vector = numpy.asarray(tokens[1:], "float32")
                    vectors[word] = vector
        self.vectors = vectors

    def clean(self, word):
        """Clean up word"""

        # Strip unwanted characters
        clean = re.sub(r"[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+", "", word).strip().lower()
        if len(clean) <= 1:
            return " "  # Word too short

        # Generate candidates for possible compound words
        # "valid" -> ["valid"]
        # "cul de sac" -> ["cul-de-sac", "culdesac"]
        # "top-hat" -> ["top-hat", "tophat"]
        candidates = []
        if " " in clean:
            candidates.append(re.sub(r" +", "-", clean))
            candidates.append(re.sub(r" +", "", clean))
        else:
            candidates.append(clean)
            if "-" in clean:
                candidates.append(re.sub(r"-+", "", clean))
        self.candidates = candidates
        return self.candidates

    def validate(self, word):
        for cleaned in self.clean(word):
            return cleaned if cleaned in self.vectors else None

    def get_invalid(self, word):
        for cleaned in self.clean(word):
            return cleaned if cleaned not in self.vectors else None

    def distance(self, word1, word2):
        """Compute cosine distance (0 to 2) between two words"""

        return scipy.spatial.distance.cosine(self.vectors.get(word1), self.vectors.get(word2))

    def dat(self, words, minimum=7):
        """Compute DAT score"""
        # Keep only valid unique words
        uniques = []
        for word in words:
            valid = self.validate(word)
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
