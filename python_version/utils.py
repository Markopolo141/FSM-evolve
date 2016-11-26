from pymatrix import *
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
generate a manhattan normalized pymatrix column vector of dimension 'size'
'''
def generate_even_vector(size):
    return matrix([[1.0/size] for s in range(size)])

'''
given a pymatrix matrix normalise it so that its entries sum = 1.0
'''
def manhattan_normalize(v):
    s = 0
    for a in v:
        s += abs(a)
    for row in range(v.nrows):
        for col in range(v.ncols):
            if s >0:
                v.grid[row][col] = abs(v.grid[row][col])/s
            else:
                v.grid[row][col] = 1.0/(v.nrows*v.ncols)
    return v    

'''
given square pymatrix M, use power-iterations to find largest positive eigenvalue and its corresponding eigenvector.
i and ip control the number of iterations taken place: the number of iterations is given by: i*2^ip
'''
def eigen(M, ip, i):
    size = M.ncols
    v = generate_even_vector(size)
    for count in range(ip):
        M = M*M
    for count in range(i):
        v = M*v
        s = sum([sum(a) for a in v.grid])
        if s == 0:
            return 0,generate_even_vector(size)
        if math.isnan(s):
            raise Exception("overflow: power_iteration power factor is too big")
        z = 1.0/s
        v = v * z
    return math.pow(s, 1.0/(2**(ip))),v

'''
given a pymatrix of sympy expressions return a pymatrix of thoes expressions evaluated with dictionary d
d is of form {pysymbol:value,pysymbol:value...}
'''
def eval_sympy_matrix(M,d):
    return M.map(lambda x: max(float(x.evalf(subs=d)),0))

'''
given a Matrix of sympy expressions, sequencially substitute each entity according to the given dictionary of values
'''
def subs_sympy_matrix(M,S):
    for k in S.keys():
        M = M.map(lambda x:x.subs(symbols(str(k)),S[k]))
    return M
    
'''
given a pymatrix of math-expression-strings, return corresponding pymatrix of sympy expressions
'''
def parse_matrix_of_expressions(m):
    mm = copy(m)
    for x in range(len(m)):
        for y in range(len(m[0])):
            mm[x][y] = parse_expr(str(m[x][y]))
    return matrix(mm)