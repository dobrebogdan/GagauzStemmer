__all__ = ["Transition"]


class Transition(object):
    def __init__(self, start_state, nextState, word, suffix, marked):
        self.start_state = start_state
        self.nextState = nextState
        self.word = word
        self.suffix = suffix
        self.marked = False

    def similarTransitions(self, transitions):
        for transition in transitions:
            if (self.start_state == transition.start_state and
                    self.nextState == transition.nextState):
                yield transition
