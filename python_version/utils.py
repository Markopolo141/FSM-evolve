import numpy
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols
from copy import deepcopy as copy
import math

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
            count = d[keys[i]]["min"]
            while count <= d[keys[i]]["max"]:
                sub_method(vals + [count],i+1)
                count += d[keys[i]].get("step",1)
        else:
            amalgum_list.append(dict(zip(keys,vals)))
    sub_method([],0)
    return amalgum_list

'''
given square pymatrix M, use power-iterations to find largest positive eigenvalue and its corresponding eigenvector.
i and ip control the number of iterations taken place: the number of iterations is given by: i*2^ip
'''
def eigen(M, ip, i):
    size = M.shape[0]
    v = numpy.matrix([[1.0/size] for s in range(size)])
    for count in range(ip):
        M = M*M
    for count in range(i):
        v = M*v
        s = v.sum()
        if s == 0:
            return 0,numpy.matrix([[1.0/size] for s in range(size)])
        if math.isnan(s):
            raise Exception("overflow: power_iteration power factor is too big")
        z = 1.0/s
        v = v * z
    return math.pow(s, 1.0/(2**(ip))),v

'''

'''
def matrix_map(M,f):
    MM = [list(a) for a in M]
    for i in range(len(MM)):
        for j in range(len(MM[0])):
            MM[i][j] = f(M[i][j],i,j)
    return MM
