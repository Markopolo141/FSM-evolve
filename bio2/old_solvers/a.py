import sympy
from sympy import symbols, Matrix, N, diff
import json
#import numpy as np
from sympy.parsing.sympy_parser import parse_expr


# load the matrix
with open("input_data.json","r") as f:
    data = json.load(f)

# extract the dimensions of the matrix
N = len(data)
assert False not in [len(d)==N for d in data]

# load data as symbolic matrix
data = Matrix([[parse_expr(ddd) for ddd in dd] for dd in data])

# setup the initial vectors
v = Matrix([0.5 for i in range(N)])
s = ["x{}".format(i) for i in range(N)]
s_symbols = [symbols(x) for x in s]
def get_symbols_dict():
    return {s_symbols[i]:v[i] for i in range(N)}

# setup the genetic vectors
G = 3
vg = Matrix([0.5 for i in range(G)])
g = ["g{}".format(i) for i in range(G)]
g_symbols = [symbols(x) for x in g]
def get_g_symbols_dict():
    return {g_symbols[i]:vg[i] for i in range(G)}


inner_incorporation_factor = 0.5
outer_incorporation_factor = 0.01
outer_iterations = 20
for j in range(outer_iterations):
    # reduce the data to genetic data array
    datag = data.subs(get_g_symbols_dict())

    # do initial iterations to find a stable point
    inner_iterations = 20
    vnorm = None
    for i in range(inner_iterations):
        old_v = v.copy()
        v[:,:] = ((1.0-inner_incorporation_factor)*v + 
            inner_incorporation_factor*datag.subs(get_symbols_dict())*v)
        vnorm = v.norm()
        v[:,:] = v / vnorm
        # print("   inner_difference is:", (v - old_v).norm())
    print("Lambda = {}".format(vnorm))
    print(v)

    # calculate the vector of perturbations in eigenvalue
    delta_lambda = []
    for gg in range(G):
        data_g = diff(data,g[gg]).subs(get_g_symbols_dict()).subs(get_symbols_dict())
        delta_lambda.append((v.transpose()*(data_g*v))[0])
    delta_lambda = Matrix(delta_lambda)
    delta_lambda = delta_lambda / (1.0+delta_lambda.norm())
    old_vg = vg.copy()
    vg[:,:] = vg + outer_incorporation_factor*delta_lambda
    #print("outer_difference is:", (vg - old_vg).norm())
    print(vg)


