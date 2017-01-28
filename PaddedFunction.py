from sympy.utilities.lambdify import lambdify

class PaddedFunction:
    def __init__(self, expr):
        self.strE = str(expr)
        self.atoms = [a for a in list(expr.atoms()) if not a.is_constant()]
        self.values = {str(a):None for a in self.atoms}
        self.value = None
        self.f = lambdify(self.atoms,expr,dummify=False)
    def update(self):
        self.value = self.f(**self.values)
    def connect(self,dictionary):
        for k in self.values.keys():
            try:
                d = dictionary[k]
            except KeyError:
                print "Error: cannot connect function {} with atoms {}, to dictionary with keys {}".format(self.strE,self.values.keys(),dictionary.keys())
                raise
            self.values[k] = d
    def __eq__(self,other):
        return self.strE == other.strE
