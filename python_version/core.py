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

'''
given a choice matrix (of sympy expressions), and population vector (of numbers), return the weighted-choice matrix
which is the matrix expressions evaluated according to the numbers of the population vector. 
'''
def weight_choice(choice,pop):
    return eval_sympy_matrix(choice,[a[0,0] for a in pop])

'''
given a switch-matrix, weight the choices available to each state by a supplied .
'''
def weight_switch(switch,vector):
    weighted_switch = copy(switch)
    for col_index in range(len(switch[0])):
        if vector[col_index] is not None:
            i = 0
            for row_index in range(len(switch)):
                if switch[row_index][col_index]:
                    weighted_switch[row_index][col_index] = vector[col_index][i]
                    i = i + 1
    return weighted_switch

'''
given a matrix of sympy expressions (under the assumption that their free-variables are numbered s0,s1,...,s(ps-1))
convert each expression to a lambda-functioni n the matrix
'''
def lambdify_matrix(M, ps):
    symbols = [sympy.symbols("s{}".format(i)) for i in range(ps)]
    for row_index in range(len(M)):
        for col_index in range(len(M[0])):
            M[row_index][col_index] = lambdify(symbols, M[row_index][col_index])
    return M
