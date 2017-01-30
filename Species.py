from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols
from wrapt import ObjectProxy as proxy
from pymatrix import matrix
from utils import generate_switch_extrema, normalise
from SubSpecies import SubSpecies

class Species:
    def __init__(self, switch, choice, distribution=None,sub_distribution=None,col_pruning=False,row_pruning=True,preliminary_subs={}):
        self.num_states = len(choice)
        self.sub_species = []
        self.values = [proxy(0) for i in range(self.num_states)]
        self.svalues = [proxy(0) for i in range(self.num_states)]
        self.value = proxy(0)
        extrema = generate_switch_extrema(matrix(switch))
        preliminary_subs = {symbols(a):b[0] for a,b in preliminary_subs.iteritems()}
        choice = matrix(choice).map(lambda x:parse_expr(str(x)).subs(preliminary_subs))
        for i,e in enumerate(extrema):
            if sub_distribution is not None:
                self.sub_species.append(SubSpecies(choice*e,numbers=sub_distribution[i]))
            elif distribution is not None:
                self.sub_species.append(SubSpecies(choice*e,distribution[i]))
            else:
                self.sub_species.append(SubSpecies(choice*e,1.0))
    def updateValues(self):
        for i in range(self.num_states):
            counter = 0
            for s in self.sub_species:
                counter += s[i]
            self.values[i].__wrapped__ = counter
        self.value.__wrapped__ = sum(self.values)
        normalise(self.svalues,self.values)
    def update(self,smoothing):
        for s in self.sub_species:
            s.update(smoothing)
        self.updateValues()
    def turnOver(self):
        for s in self.sub_species:
            s.turnOver()

