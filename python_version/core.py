from copy import deepcopy as copy
import numpy
import math
from numpy.linalg import eig
import operator

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
given a dictionary defining ranges of iterables in form 
{"count1":{"min":0,"max":5,"step":1},...} return a list of dicts of all combinations of thoes values
note: "step" is optional on each
'''
def multi_iterate(d):
    keys = d.keys()
    amalgum_list = []
    def sub_method(vals,indices,i):
        if i<len(keys):
            count = d[keys[i]]["min"]
            index = 0
            while count < d[keys[i]]["max"]:
                sub_method(vals + [count],indices + [index],i+1)
                count += d[keys[i]].get("step",1)
                index += 1
        else:
            amalgum_list.append({keys[i]:(vals[i],indices[i]) for i in range(len(keys))})
    sub_method([],[],0)
    return amalgum_list

'''
given square pymatrix M, find largest positive eigenvalue and its corresponding eigenvector.
'''
def eigen(M):
    vals,vecs = eig(M)
    index, max_val = max(enumerate(vals), key=operator.itemgetter(1))
    vec = vecs[:,index]
    vec = vec / numpy.sum(vec)
    return max_val, vec

'''
return a matrix, the result of the supplied function f applied to every individual element of matrix M
'''
def matrix_map(M,f):
    MM = [list(a) for a in M]
    for i in range(len(MM)):
        for j in range(len(MM[0])):
            MM[i][j] = f(M[i][j],i,j)
    return MM
