from sympy import symbols
from sympy.utilities.lambdify import lambdify
from copy import deepcopy as copy
import numpy
import sympy
from utils import *

'''
given a switch-matrix, generate the vectors of the pure (or extreme) strategies.
'''
def generate_switch_extrema(switch):
    dist = [sum([a[i] for a in switch]) for i in range(len(switch[0]))]
    dist = [d if d>1 else 0 for d in dist]
    def gen_unit_arrays(n):
        Z = [[0 for i in range(n)] for i in range(n)]
        for i in range(n):
            Z[i][i]=1
        return Z
    ex = [[]]
    for d in dist:
        arrays = gen_unit_arrays(d)
        if len(arrays)>0:
            exx = []
            for a in arrays:
                for e in ex:
                    exx.append(e+[a])
            ex = exx
        else:
            ex = [e+[None] for e in ex]
    return ex
