import re


class WordCleaner:

    def __init__(self, database_manager):
        self.db = database_manager
        self.words = None

    @staticmethod
    def clean(word):
        """Clean up word"""

        # Strip unwanted characters
        clean = re.sub(r"[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+", "",
                       word).strip().lower()
        if len(clean) <= 1:
            return " "  # Word too short

        # Generate candidates for possible compound words
        candidates = []
        if " " in clean:
            candidates.append(re.sub(r" +", "-", clean))
            candidates.append(re.sub(r" +", "", clean))
        else:
            candidates.append(clean)
            if "-" in clean:
                candidates.append(re.sub(r"-+", "", clean))
        return candidates

    def set_valid_words(self):
        valid_words = self.db.get_words()
        self.words = valid_words

    def validate(self, word):

        if not self.words:
            self.set_valid_words()

        for cleaned in self.clean(word):
            return cleaned if cleaned in self.words else None

    def get_invalid(self, word):

        if not self.words:
            self.set_valid_words()

        for cleaned in self.clean(word):
            return cleaned if cleaned not in self.words else None
