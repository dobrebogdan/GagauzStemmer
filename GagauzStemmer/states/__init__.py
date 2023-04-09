from ..transitions import Transition

__all__ = ["State"]


class State(object):
    def __init__(self, initial_state, final_state, *suffixes):
        self.initial_state = initial_state
        self.final_state = final_state
        if suffixes is None:
            self.suffixes = ()
        else:
            self.suffixes = suffixes

    def add_transitions(self, word, transitions, marked):
        for suffix in self.suffixes:
            if suffix.match(word):
                transitions.append(Transition(self, self.next_state(suffix), word, suffix, marked))

    def next_state(self, suffix):
        raise NotImplementedError("Feature is not implemented.")
