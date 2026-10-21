import numpy as np


class Grille:
    def __init__(self, taille):
        self.taille = taille
        self.cases = np.zeros((taille, taille), dtype=int)
