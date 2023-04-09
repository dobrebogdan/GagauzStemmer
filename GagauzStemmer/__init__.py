# -*- coding: utf-8 -*-
from __future__ import print_function
from .states import NounState, DerivationalState, NominalVerbState
from _collections import deque
from io import open
import functools
import sys, os

__all__ = ["GagauzStemmer"]

# The gagauz characters. They are used for skipping non gagauz words.
ALPHABET = frozenset("aäbcçdeêfghıijklmnoöprsştuüvyz")

# The gagauz vowels.
VOWELS = frozenset("üiıueöaoäê")

# The gagauz consonants.
CONSONANTS = frozenset("bcçdfghjklmnprsştvyz")

# Rounded vowels which are used for checking roundness harmony.
ROUNDED_VOWELS = frozenset("oöuü")

# Vowels that follow rounded vowels. They are combined with ROUNDED_VOWELS to check roundness harmony.
FOLLOWING_ROUNDED_VOWELS = frozenset("aäeêuü")

# The unrounded vowels which are used for checking roundness harmony.
UNROUNDED_VOWELS = frozenset("iıea")

# Front vowels which are used for checking frontness harmony.
FRONT_VOWELS = frozenset("eêiöü")

# Back vowels which are used for checking frontness harmony.
BACK_VOWELS = frozenset("ıuao")

# Last consonant rules
LAST_CONSONANT_RULES = {"b": "p", "c": "ç", "d": "t"}

# The path of the file that contains the default set of protected words.
DEFAULT_PROTECTED_WORDS_FILE = "protected_words.txt"

# The path of the file that contains the default set of vowel harmony exceptions.
DEFAULT_VOWEL_HARMONY_EXCEPTIONS_FILE = "vowel_harmony_exceptions.txt"

# The path of the file that contains the default set of last consonant exceptions.
DEFAULT_LAST_CONSONANT_EXCEPTIONS_FILE = "last_consonant_exceptions.txt"

# The path of the file that contains the default set of average stem size exceptions.
DEFAULT_AVERAGE_STEM_SIZE_EXCEPTIONS_FILE = "average_stem_size_exceptions.txt"

# The average size of Gagauz stems based on which the selection of the final stem is performed.
# The idea behind the selection process is based on the paper
# F.Can, S.Kocberber, E.Balcik, C.Kaynak, H.Cagdas, O.Calan, O.Vursavas
# "Information Retrieval on Turkish Texts"
AVERAGE_STEMMED_SIZE = 4


class GagauzStemmer:
    """Stemmer for Gagauz words
        
    Args:
    protectedWords (set): set of protected words. (default: DEFAULT_PROTECTED_WORDS)
    vowelHarmonyExceptions (set): set of vowel harmony exceptions. (default: DEFAULT_VOWEL_HARMONY_EXCEPTIONS)
    lastConsonantExceptions (set): set of last consonant exceptions. (default: DEFAULT_LAST_CONSONANT_EXCEPTIONS)
    averageStemSizeExceptions (set): set of average stem size exceptions. (default: DEFAULT_AVERAGE_STEM_SIZE_EXCEPTIONS)
    """

    def __init__(self, **kwargs):
        self.protectedWords = kwargs.get("protectedWords", DefaultSetHolder.DEFAULT_PROTECTED_WORDS)
        self.vowelHarmonyExceptions = kwargs.get("vowelHarmonyExceptions",
                                                 DefaultSetHolder.DEFAULT_VOWEL_HARMONY_EXCEPTIONS)
        self.lastConsonantExceptions = kwargs.get("lastConsonantExceptions",
                                                  DefaultSetHolder.DEFAULT_LAST_CONSONANT_EXCEPTIONS)
        self.averageStemSizeExceptions = kwargs.get("averageStemSizeExceptions",
                                                    DefaultSetHolder.DEFAULT_AVERAGE_STEM_SIZE_EXCEPTIONS_FILE)

    def stem(self, word):
        """Finds the stem of a given word.
        Args:
        word (str): the word to stem

        Returns:
        str: the stemmed word
        """
        if not self.proceed_to_stem(word):
            return word

        stems = set()

        # Process the word with the nominal verb suffix state machine.
        self.nominal_verb_suffix_stripper(word, stems),

        wordsToStem = stems.copy()
        wordsToStem.add(word)

        for stem in wordsToStem:
            # Process each possible stem with the noun suffix state machine.
            self.noun_suffix_stripper(stem, stems)

        wordsToStem = stems.copy()
        wordsToStem.add(word)

        for stem in wordsToStem:
            # Process each possible stem with the derivational suffix state machine.
            self.derivational_suffix_stripper(stem, stems)

        return self.post_process(stems, word)

    def nominal_verb_suffix_stripper(self, word, stems):
        """
        This method implements the state machine about nominal verb suffixes.
        It finds the possible stems of a word after applying the nominal verb
        suffix removal.

        Args:
        word (str): the word that will get stemmed

        Returns:
        set: a set of stems to populate
        """
        initial_state = NominalVerbState.A
        self._generic_suffix_stripper(initial_state, word, stems, "NominalVerb")

    def noun_suffix_stripper(self, word, stems):
        """
        This method implements the state machine about noun suffixes.
        It finds the possible stems of a word after applying the noun suffix removal.

        Args:
        word (str): the word that will get stemmed

        Returns:
        set: a set of stems to populate
        """
        initial_state = NounState.A
        self._generic_suffix_stripper(initial_state, word, stems, "Noun")

    def derivational_suffix_stripper(self, word, stems):
        """
        This method implements the state machine about derivational suffixes.
        It finds the possible stems of a word after applying the derivational
        suffix removal.

        Args:
        word (str): the word that will get stemmed

        Returns:
        set: a set of stems to populate
        """
        initial_state = DerivationalState.A
        self._generic_suffix_stripper(initial_state, word, stems, "Derivational")

    def _generic_suffix_stripper(self, initial_state, word, stems, machine):
        """
        Given the initial state of a state machine, it adds possible stems to a set of stems.

        Args:
        initial_state (State): an initial state
        word (str): the word to stem
        stems (set): the set to populate
        machine (str): a string representing the name of the state machine. It is used for debugging reasons only.
        """
        transitions = deque()
        initial_state.add_transitions(word, transitions, False)

        while transitions:
            transition = transitions.popleft()
            wordToStem = transition.word
            stem = self.stem_word(wordToStem, transition.suffix)
            if stem != wordToStem:
                if transition.nextState.final_state:
                    for transitionToRemove in tuple(transitions):
                        if ((transitionToRemove.start_state == transition.start_state and
                             transitionToRemove.nextState == transition.nextState) or
                                transitionToRemove.marked):
                            transitions.remove(transitionToRemove)
                    stems.add(stem)
                    transition.nextState.add_transitions(stem, transitions, False)
                else:
                    for similarTransition in transition.similarTransitions(transitions):
                        similarTransition.marked = True
                    transition.nextState.add_transitions(stem, transitions, True)

    def stem_word(self, word, suffix):
        """Removes a certain suffix from the given word.

        Args:
        word (str): the word to remove the suffix from
        suffix (Suffix): the suffix to be removed from the word

        Returns:
        str: the stemmed word
        """
        stemmedWord = word
        if self.should_be_marked(word, suffix) and suffix.match(word):
            stemmedWord = suffix.remove_suffix(stemmedWord)
        optionalLetter = suffix.optional_letter(stemmedWord)
        if optionalLetter is not None:
            if valid_optional_letter(stemmedWord, optionalLetter):
                stemmedWord = "".join(stemmedWord[:-1])
            else:
                stemmedWord = word
        return stemmedWord

    def post_process(self, stems, originalWord):
        """It performs a post stemming process and returns the final stem.

        Args:
        stems (set): a set of possible stems
        originalWord (str): the original word that was stemmed

        Returns:
        str: final stem
        """
        finalStems = set()
        if originalWord in stems:
            stems.remove(originalWord)
        for word in stems:
            if count_syllables(word) > 0:
                finalStems.add(self.last_consonant(word))

        def comparer(s1, s2):
            if s1 in self.averageStemSizeExceptions:
                return -1
            if s2 in self.averageStemSizeExceptions:
                return 1
            average_distance = abs(len(s1) - AVERAGE_STEMMED_SIZE) - abs(len(s2) - AVERAGE_STEMMED_SIZE)
            return len(s1) - len(s2) if average_distance == 0 else average_distance

        finalStems = list(finalStems)
        finalStems.sort(key=functools.cmp_to_key(comparer))
        return finalStems[0] if finalStems else originalWord

    def proceed_to_stem(self, word):
        """
        Checks whether a stem process should proceed or not.

        Args:
        word (str): the word to check for stem

        Returns: 
        bool: whether to proceed or not
        """
        if not word:
            return False

        if not is_gagauz(word):
            return False

        if self.protectedWords and word in self.protectedWords:
            return False

        if count_syllables(word) < 2:
            return False

        return True

    def should_be_marked(self, word, suffix):
        """
        Checks if a word should be stemmed or not.

        Args:
        word (str): the word to be checked
        suffix (Suffix): the suffix that will be removed from the word

        Returns:
        bool: whether the word should be stemmed or not
        """
        return (word not in self.protectedWords and
                ((suffix.check_harmony and has_vowel_harmony(word) or
                  word in self.vowelHarmonyExceptions) or
                 not suffix.check_harmony))

    def last_consonant(self, word):
        """
        Checks the last consonant rule of a word.

        Args:
        word (str): the word to check its last consonant

        Returns:
        str: the new word affected by the last consonant rule
        """
        if word in self.lastConsonantExceptions:
            return word

        lastChar = word[-1:]
        replaceChar = LAST_CONSONANT_RULES.get(lastChar)
        if replaceChar:
            return "".join((word[:-1], replaceChar))
        return word


def is_gagauz(word):
    """
    Checks whether a word is written in Turkish alphabet or not.

    Args: 
    word (str): the word to check its letters

    Returns:
    bool: whether contains only Turkish letters or not.
    """
    return all(n in ALPHABET for n in word)


def vowels(word):
    """
    Gets the vowels of a word.

    Args:
    word (str): the word to get its vowels

    Returns: 
    str: the vowels
    """
    return "".join(n for n in word if n in VOWELS)


def count_syllables(word):
    """
    Gets the number of syllables of a word.

    Args:
    word (str): the word to count its syllables

    Returns:
    int: the number of syllables
    """
    return len(vowels(word))


def has_frontness(vowel, candidate):
    """
    Checks the frontness harmony of two characters. 

    Args:
    vowel (str): the first character
    candidate (str): candidate the second character

    Returns:
    bool: whether the two characters have frontness harmony or not.
    """
    return ((vowel in FRONT_VOWELS and candidate in FRONT_VOWELS) or
            (vowel in BACK_VOWELS and candidate in BACK_VOWELS))


def has_roundness(vowel, candidate):
    """
    Checks the roundness harmony of two characters.

    Args:
    vowel (str): the first character
    candidate (str): candidate the second character

    Returns:
    bool: whether the two characters have roundness harmony or not.
    """
    return ((vowel in UNROUNDED_VOWELS and candidate in UNROUNDED_VOWELS) or
            (vowel in ROUNDED_VOWELS and candidate in FOLLOWING_ROUNDED_VOWELS))


def vowel_harmony(vowel, candidate):
    """
    Checks the vowel harmony of two characters.

    Args:
    vowel (str): the first character
    candidate (str): candidate the second character

    Returns:
    bool: whether the two characters have vowel harmony or not.
    """
    return has_roundness(vowel, candidate) and has_frontness(vowel, candidate);


def has_vowel_harmony(word):
    """
    Checks the vowel harmony of a word.

    Args:
    word (str): word  the word to check its vowel harmony

    Returns:
    bool: whether the word has vowel harmony or not.
    """
    vowelsOfWord = vowels(word)
    try:
        vowel = vowelsOfWord[-2]
    except IndexError:
        return True
    try:
        candidate = vowelsOfWord[-1]
    except IndexError:
        return True
    return vowel_harmony(vowel, candidate)


def valid_optional_letter(word, candidate):
    """
    Checks whether an optional letter is valid or not.

    Args:
    word (str): the word to check its last letter
    candidate (str): the last character candidate

    Returns:
    bool: whether is valid or not
    """
    try:
        previousChar = word[-2]
    except IndexError:
        return False

    if candidate in VOWELS:
        return previousChar in CONSONANTS
    else:
        return previousChar in VOWELS


def load_word_set(path):
    """
    Creates a set from a file

    Args:
    path (str): relative path to file

    Returns:
    set: the set
    """
    result = set()
    try:
        path_to_file = os.path.join(os.path.dirname(__file__), "resources", path)
        with open(path_to_file, encoding="utf-8") as f:
            for line in f:
                result.add(line.strip())
    except IOError:
        print("Unable to load {}", path, file=sys.stderr)
    return frozenset(result)


class DefaultSetHolder:
    DEFAULT_PROTECTED_WORDS = load_word_set(DEFAULT_PROTECTED_WORDS_FILE)
    DEFAULT_VOWEL_HARMONY_EXCEPTIONS = load_word_set(DEFAULT_VOWEL_HARMONY_EXCEPTIONS_FILE)
    DEFAULT_LAST_CONSONANT_EXCEPTIONS = load_word_set(DEFAULT_LAST_CONSONANT_EXCEPTIONS_FILE)
    DEFAULT_AVERAGE_STEM_SIZE_EXCEPTIONS_FILE = load_word_set(DEFAULT_AVERAGE_STEM_SIZE_EXCEPTIONS_FILE)
