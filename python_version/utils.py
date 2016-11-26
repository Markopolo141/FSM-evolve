import numpy
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols
from copy import deepcopy as copy
import math

'''
a better version of range
'''
def super_range(start, end, step):
    a = start
    while a <= end:
        yield a
        a = a + step

'''
given a dictionary defining ranges of iterables in form 
{"count1":{"min":0,"max":5,"step":1},...} return a list of dicts of all combinations of thoes values
note: "step" is optional on each
'''
def multi_iterate(d):
    keys = d.keys()
    amalgum_list = []
    def sub_method(vals,i):
        if i<len(keys):
            for count in super_range(d[keys[i]]["min"], d[keys[i]]["max"], d[keys[i]].get("step",1)):
                sub_method(vals + [count],i+1)
        else:
            amalgum_list.append(dict(zip(keys,vals)))
    sub_method([],0)
    return amalgum_list
        

'''
generate a manhattan normalized matrix column vector of dimension 'size'
'''
def generate_even_vector(size):
    return numpy.matrix([[1.0/size] for s in range(size)])

'''
given a list of numbers normalise it so that its entries sum to 1.0
'''
def manhattan_normalize(v):
    s = 0
    for a in v:
        s += abs(a)
    if s>0:
        v = [abs(a)/s for a in v]
    else:
        v = [1.0/s for a in v]
    return v    

'''
given square pymatrix M, use power-iterations to find largest positive eigenvalue and its corresponding eigenvector.
i and ip control the number of iterations taken place: the number of iterations is given by: i*2^ip
'''
def eigen(M, ip, i):
    size = M.shape[0]
    v = generate_even_vector(size)
    for count in range(ip):
        M = M*M
    for count in range(i):
        v = M*v
        s = v.sum()
        if s == 0:
            return 0,generate_even_vector(size)
        if math.isnan(s):
            raise Exception("overflow: power_iteration power factor is too big")
        z = 1.0/s
        v = v * z
    return math.pow(s, 1.0/(2**(ip))),v

'''
given a matrix of lambda expressions return a matrix of thoes expressions evaluated with arguments in list d
d is of form [arg1,arg2,...]
'''
def eval_sympy_matrix(M,d):
    #MM = copy(M)
    MM = [list(a) for a in M]
    for i in range(len(M)):
        for j in range(len(M[0])):
            MM[i][j] = MM[i][j](*d)
    return MM

'''
given a Matrix of sympy expressions, sequencially substitute each entity according to the given dictionary of values
'''
def subs_sympy_matrix(M,S):
    MM = copy(M)
    for k in S.keys():
        func = lambda x:x.subs(symbols(str(k)),S[k])
        for i in range(len(M)):
            for j in range(len(M[0])):
                MM[i][j] = func(MM[i][j])
    return MM
    
'''
given a list-of-lists matrix of math-expression-strings, return list-of-list matrix of sympy expressions
'''
def parse_matrix_of_expressions(m):
    mm = copy(m)
    for x in range(len(m)):
        for y in range(len(m[0])):
            mm[x][y] = parse_expr(str(m[x][y]))
    return mm