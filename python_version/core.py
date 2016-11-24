from collections import OrderedDict
from sympy import symbols
from pymatrix import *
from utils import *

'''
given a switch-matrix, generate the vectors of the pure (or extreme) strategies.
'''
def generate_switch_extrema(switch):
    dist = [sum(c) for c in switch.cols()]
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

'''
given a choice matrix (of sympy expressions), and population vector (of numbers), return the weighted-choice matrix
which is the matrix expressions evaluated according to the numbers of the population vector. 
'''
symbol_dict = {}
def weight_choice(choice,pop):
    global symbol_dict
    if id(choice) not in symbol_dict:
        Z = OrderedDict()
        for i in range(choice.nrows):
            Z[symbols("s{}".format(i))]=None
        symbol_dict[id(choice)]=Z
    dictionary = symbol_dict[id(choice)]
    keys = dictionary.keys()
    for i,p in enumerate(pop):
        dictionary[keys[i]] = p
    return eval_sympy_matrix(choice,dictionary)

'''
given a switch-matrix, weight the choices available to each state by a supplied .
'''
def weight_switch(switch,vector):
    weighted_switch = switch.copy()
    for col_index in range(switch.ncols):
        if vector[col_index] is not None:
            i = 0
            for row_index in range(switch.nrows):
                if switch[row_index][col_index]:
                    weighted_switch.grid[row_index][col_index] = vector[col_index][i]
                    i = i + 1
    return weighted_switch