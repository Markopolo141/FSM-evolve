from utils import addTo
from PaddedFunction import PaddedFunction
from PaddedFunction import functions

matricies = []
class PaddedMatrix:
    def __init__(self, M):
        M = M.map(lambda x:x.simplify())
        self.strM = str(M)
        self.replacements = []
        for r,c,e in M.elements():
            if e.is_constant():
                M[r][c] = float(e)
            else:
                self.replacements.append((r,c,addTo(PaddedFunction(e),functions)))
                M[r][c] = None
        self.M = M
    def update(self):
        for r,c,f in self.replacements:
            self.M[r][c]=f.value
    def __eq__(self, other):
        return self.strM == other.strM
