from ..suffixes import NounSuffix
from . import State

TT_VALUES, FT_VALUES, FF_VALUES = dict(), dict(), dict()


class NounState(State):
    def __init__(self, initial_state, final_state, *suffixes):
        super(NounState, self).__init__(initial_state, final_state, *suffixes)

        if self.initial_state and self.final_state:
            self.VALUES = TT_VALUES
        elif (not self.initial_state) and self.final_state:
            self.VALUES = FT_VALUES
        else:
            self.VALUES = FF_VALUES

    def next_state(self, suffix):
        return self.VALUES[suffix]


A = NounState(True, True, *NounSuffix.VALUES)
B = NounState(False, True, NounSuffix.S1, NounSuffix.S2, NounSuffix.S3, NounSuffix.S4, NounSuffix.S5)
C = NounState(False, False, NounSuffix.S6, NounSuffix.S7)
D = NounState(False, False, NounSuffix.S10, NounSuffix.S13, NounSuffix.S14)
E = NounState(False, True, NounSuffix.S1, NounSuffix.S2, NounSuffix.S3, NounSuffix.S4, NounSuffix.S5, NounSuffix.S6,
              NounSuffix.S7, NounSuffix.S18)
F = NounState(False, False, NounSuffix.S6, NounSuffix.S7, NounSuffix.S18)
G = NounState(False, True, NounSuffix.S1, NounSuffix.S2, NounSuffix.S3, NounSuffix.S4, NounSuffix.S5, NounSuffix.S18)
H = NounState(False, True, NounSuffix.S1)
K = NounState(False, True)
L = NounState(False, True, NounSuffix.S18)
M = NounState(False, True, NounSuffix.S1, NounSuffix.S2, NounSuffix.S3, NounSuffix.S4, NounSuffix.S5, NounSuffix.S6,
              NounSuffix.S6, NounSuffix.S7)

ALL = (A, B, C, D, E, F, G, H, K, L, M)

for sfx in (NounSuffix.S8, NounSuffix.S11, NounSuffix.S13):
    TT_VALUES[sfx] = B

for sfx in (NounSuffix.S9, NounSuffix.S16):
    TT_VALUES[sfx] = C

FF_VALUES[NounSuffix.S18] = FT_VALUES[NounSuffix.S18] = TT_VALUES[NounSuffix.S18] = D

for sfx in (NounSuffix.S10, NounSuffix.S17):
    TT_VALUES[sfx] = E

for sfx in (NounSuffix.S12, NounSuffix.S14):
    TT_VALUES[sfx] = F

TT_VALUES[NounSuffix.S15] = G

for sfx in (NounSuffix.S2, NounSuffix.S3, NounSuffix.S4, NounSuffix.S5, NounSuffix.S6):
    FT_VALUES[sfx] = TT_VALUES[sfx] = H

FF_VALUES[NounSuffix.S7] = FT_VALUES[NounSuffix.S7] = TT_VALUES[NounSuffix.S7] = K
FT_VALUES[NounSuffix.S1] = TT_VALUES[NounSuffix.S1] = L
TT_VALUES[NounSuffix.S19] = M

FF_VALUES[NounSuffix.S13] = B
FF_VALUES[NounSuffix.S10] = E
FF_VALUES[NounSuffix.S14] = F
FF_VALUES[NounSuffix.S6] = H
