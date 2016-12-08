from copy import deepcopy as copy
import numpy
import math

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
return a matrix, the result of the supplied function f applied to every individual element of matrix M
'''
def matrix_map(M,f):
    MM = [list(a) for a in M]
    for i in range(len(MM)):
        for j in range(len(MM[0])):
            MM[i][j] = f(M[i][j],i,j)
    return MM
