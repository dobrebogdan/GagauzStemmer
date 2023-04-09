import re

__all__ = ["Suffix"]


class Suffix(object):
    def __init__(self, name, pattern, optionalLetter, checkHarmony):
        self.name = name
        self.pattern = re.compile("(" + pattern + ")$", re.UNICODE)

        if optionalLetter is None:
            self.optionalLetterCheck = False
            self._optionalLetterPattern = None
        else:
            self.optionalLetterCheck = True
            self._optionalLetterPattern = re.compile("(" + optionalLetter + ")$", re.UNICODE)

        self.checkHarmony = checkHarmony

    def match(self, word):
        return self.pattern.search(word)

    def optional_letter(self, word):
        if self.optionalLetterCheck:
            match = self._optionalLetterPattern.search(word)
            if match:
                return match.group()

    def remove_suffix(self, word):
        return self.pattern.sub("", word)

    @property
    def check_harmony(self):
        return self.checkHarmony
