from sympy import symbols, Matrix, diff
from sympy.parsing.sympy_parser import parse_expr
from numpy import matrix
from numpy.linalg import norm
import json
from functools import partial


# load the matrix
with open("input_data2.json","r") as f:
    config = json.load(f)
assert isinstance(config,dict), 'config must be JSON dictionary'
assert 'matrix' in config.keys(), 'config must have "matrix" specified'
data = config['matrix']

# extract the dimensions of the matrix
assert isinstance(data, list), 'matrix must be specified as array of arrays'
N = len(data)
assert False not in [len(d)==N for d in data], 'matrix must be square'

# setup the initial vectors
v = matrix([[0.5] for i in range(N)])
s = ["x{}".format(i) for i in range(N)]
s_symbols = [symbols(x) for x in s]
def get_dict():
    return {s[i]:v[i] for i in range(N)}


# load data as symbolic matrix, and extract genetic symbols
g_symbols = set()
data = [[parse_expr(ddd) for ddd in dd] for dd in data]
for dd in data:
    for ddd in dd:
        for sym in ddd.free_symbols:
            if sym not in s_symbols:
                g_symbols.add(sym)
data = Matrix(data)

# setup the genetic vectors
G = len(g_symbols)
vg = matrix([[0.5] for i in range(G)])
g_symbols = sorted(list(g_symbols))
g = [str(gg) for gg in g_symbols]
def get_g_dict():
    return {g[i]:vg[i] for i in range(G)}


def dumb_lambdify(symbols,element):
    s = "lambda {} : {}".format(",".join(symbols),repr(element))
    return eval(s, globals())

# compile away our sympy expressions - for speed
A = dumb_lambdify(s+g,matrix(data.tolist()))
dA = [dumb_lambdify(s+g,matrix(diff(data,g[gg]).tolist())) for gg in range(G)]

# begin primary loop
inner_incorporation_factor = config.get("inner_incorporation_factor",0.5)
outer_incorporation_factor = config.get("outer_incorporation_factor",0.01)
max_inner_iterations = config.get("max_inner_iterations",200)
inner_iteration_target = config.get("inner_iteration_target", 1e-5)
max_outer_iterations = config.get("max_outer_iterations",200)
outer_iteration_target = config.get("outer_iteration_target",1e-3)

j = 0
outer_difference = float('inf')
while ((j<max_inner_iterations) and 
(outer_difference>outer_iteration_target)):
    j += 1
    # reduce the data to genetic data array
    A_x = partial(A,**get_g_dict())

    # do iterations to find a stable point
    vnorm = None
    i = 0
    inner_difference = float('inf')
    while ((i<max_inner_iterations) and 
    (inner_difference>inner_iteration_target)):
        old_v = v.copy()
        v[:,:] = ((1.0-inner_incorporation_factor)*v + 
            inner_incorporation_factor*A_x(**get_dict())*v)
        vnorm = norm(v)
        v[:,:] = v / vnorm
        inner_difference = norm(v - old_v)
        i += 1
    print("Lambda = {}".format(vnorm))
    print(v)
    
    # calculate the vector of perturbations in eigenvalue
    delta_lambda = []
    arguments = get_dict()
    arguments.update(get_g_dict())
    for gg in range(G):
        delta_lambda.append([(v.transpose()*(dA[gg](**arguments)*v))[0,0]])
    delta_lambda = matrix(delta_lambda)
    delta_lambda = delta_lambda / (1.0+norm(delta_lambda))
    vg[:,:] = vg + outer_incorporation_factor*delta_lambda
    outer_difference = norm(outer_incorporation_factor*delta_lambda)
    print(vg)

