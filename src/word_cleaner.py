import re
from typing import List, Tuple, Optional


class WordCleaner:
    def __init__(self, database_manager):
        self.db = database_manager
        self.words = []

    @staticmethod
    def clean(word: str):
        if not isinstance(word, str):
            raise ValueError("Input word must be a string.")
        cleaned = re.sub(r'[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+', '', word.lower())
        cleaned = cleaned.strip()
        return cleaned if len(cleaned) > 1 else ' '

    def set_valid_words(self):
        valid_words: List[str] = self.db.get_words()
        self.words = valid_words

    def validate(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        if not self.words:
            self.set_valid_words()

        cleaned = self.clean(word)

        if cleaned in self.words:
            return cleaned, None  # valid word
        return None, cleaned  # invalid word
