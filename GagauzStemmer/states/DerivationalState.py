from ..suffixes import DerivationalSuffix
from . import State


class DerivationalState(State):
    def __init__(self, initial_state, final_state, *suffixes):
        super(DerivationalState, self).__init__(initial_state, final_state, *suffixes)

    def next_state(self, suffix):
        if self.initial_state:
            return B


A = DerivationalState(True, False, *DerivationalSuffix.VALUES)
B = DerivationalState(False, True)
