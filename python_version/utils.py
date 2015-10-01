from collections import OrderedDict
from sympy import *
from sympy.core.numbers import *
from pymatrix import *
import logging

logger = logging.getLogger(__name__)


def super_range(start, end, step):
    a = start
    while a <= end:
        yield a
        a = a + step

def abs_sum(X):
    s = 0
    for n in X:
        s = s + abs(n)
    return s

def delta(a):
    return 1.0 if a==0 else 0.0

def protected_division(a,b, r=0):
    return r if b==0 else a/b
    
def displace(a, b, proportion):
    return a + proportion*(b-a)

def manhattan_distance(a,b, sub=None):
    if sub is None:
        return abs_sum(b-a)
    else:
        return abs_sum(sub(b, a))
    
def manhattan_normalize(a, mul=None):
    s = sum(a)
    s = delta(s) + s
    if mul is None:
        return (1.0/s)*a
    else:
        return mul((1.0/s), a)
    
def generate_even_vector(size):
    a = 1.0/size
    return matrix([[a]]*size)

def generate_constant_vector(size, val):
    return matrix([[val]]*size)
    
def matrix_size(m):
    return m.nrows, m.ncols

def matrix_len(m):
    return m.nrows * m.ncols
    
def elvis(a, f, *args, **kwargs):
    if a is None:
        return f(*args, **kwargs)
    return a

def get_max_index(obj_list, func=lambda x:x):
    f = float("-inf")
    index = None
    for i,o in enumerate(obj_list):
        funced_val = func(o)
        if funced_val > f:
            f = funced_val
            index = i
    return index

def get_max_of(obj_list, func=lambda x:x):
    f = float("-inf")
    obj = None
    for o in obj_list:
        funced_val = func(o)
        if funced_val > f:
            f = funced_val
            obj = o
    return obj

def is_ergodic(m, iszero=lambda x:x==0):
    if m.ncols != m.nrows:
        return False
    mul = 1
    while (mul < m.ncols):
        m = m * m + m
        mul = mul * 2
    for v in m:
        if iszero(v):
            return False
    return True

def every_element_is_in(m, s):
    for v in m:
        if v not in s:
            return False
    return True

def is_expression_with(v, atoms):
    for a in v.atoms():
        if not ((a.is_number and a.is_real) or (a.is_Symbol and a in atoms)):
            return False
    return True
    
def matrix_is_expressions_with(m, atoms):
    for v in m:
        if not is_expression_with(v, atoms):
            return False
    return True
    
def check_expression_positive_semi_definite(m, start=0.0, end=1.0, step=0.2):
    syms = []
    for a in m.atoms():
        if a.is_Symbol and a not in syms:
            syms.append(a)
    def f(dim):
        if dim > 0:
            for i in super_range(0.0, 1.0, 0.2):
                for z in f(dim-1):
                    yield [i] + z
        else:
            yield []
    
    for nums in f(len(syms)):
        try:
            if m.subs(zip(syms, nums)) < 0:
                return False
        except:
            logger.warn("exception in evaluating positive semi-definiteness of expression {} for trial {}={}".format(m, syms,nums), exc_info=True)
            pass
    return True

def check_matrix_positive_semi_definite(m, start=0.0, end=1.0, step=0.2):
    return False not in [check_expression_positive_semi_definite(v, start, end, step) for v in m]

def variable_translate(nums):
    t = [1.0]
    for n in nums:
        t.append(t[-1]*n/(1.0-n))
    t_sum = sum(t)
    return [a/t_sum for a in t]

def distributed_variable_translate(dist, nums):
    nums = [n for n in nums]
    r = []
    i = 0
    for d in dist:
        if d>0:
            r.append(variable_translate(nums[i:(i+d)]))
        else:
            r.append(None)
        i = i + d
    return r

def get_distribution(m):
    dist = [sum(c) for c in m.cols()]
    return [d-1 if d>1 else 0 for d in dist]

pop_dict = {}
def weight_choice(choice, pop):
    global pop_dict
    if pop.ncols * pop.nrows != len(pop_dict):
        pop_dict = OrderedDict()
        for i,p in enumerate(pop):
            pop_dict[symbols("s{}".format(i))] = p
    else:
        for i,p in enumerate(pop):
            pop_dict[pop_dict.keys()[i]] = p
    weighted_choice = Matrix(choice.nrows, choice.ncols)
    for row_index, row in enumerate(choice.grid):
        for col_index, element in enumerate(row):
            weighted_choice.grid[row_index][col_index] = float(element.evalf(subs=pop_dict))
    return weighted_choice

def weight_switch(switch, nums, dist=None):
    if dist is None:
        dist = get_distribution(switch)
    weighted_switch = switch.copy()
    distributed = distributed_variable_translate(dist, nums)
    for col_index in range(switch.ncols):
        if distributed[col_index]:
            for row_index in range(switch.nrows):
                if switch[row_index][col_index]:
                    weighted_switch.grid[row_index][col_index] = distributed[col_index].pop()
    return weighted_switch

def check_input(switch, choice):
    if not (switch.nrows == choice.ncols and switch.ncols == choice.nrows):
        return False
    m = choice*switch
    if not matrix_is_expressions_with(m, [symbols("s{}".format(i)) for i in range(switch.ncols)]):
        return False
    if not is_ergodic(m, lambda x:x.expand().simplify==0):
        return False
    if not check_matrix_positive_semi_definite(m):
        return False
    return True

