from solver import *
import numpy as np
from collections import defaultdict
from tqdm import tqdm

logging.getLogger().setLevel(logging.WARNING)

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.INFO)

#from sympy import symbols, Matrix
#import json

#https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret



coords = {
"age" : ["S","Y","O","P","K"], # super-young, young, old, old-prosperous
}
coords_keys = sorted(coords.keys())
hypermodel_symbols = keydefaultdict(symbols)


def dict_combinations(extant_combinations,dictionary,keys):
    if len(keys)>0:
        new_extant_combinations = []
        for element in dictionary[keys[0]]:
            for e in extant_combinations:
                new_extant_combinations.append(e+[element])
        return dict_combinations(new_extant_combinations,dictionary,keys[1:])
    return extant_combinations

def to_dict(l):
    return {coords_keys[i]:l[i] for i in range(len(l))}
def from_dict(d):
    return [d[k] for k in coords_keys]

index_combinations = dict_combinations([[]],coords,sorted(coords.keys()))

N = len(index_combinations)

def get_symbol(combination):
    return symbols("x{}".format(index_combinations.index(combination)))

def apply(matrix,func):
    for i in range(N):
        for j in range(N):
            matrix[i,j] = func(matrix[i,j], (i,j), to_dict(index_combinations[i]), to_dict(index_combinations[j])  )


    


def sex_propagate(old,coords,from_t,to_t):
    #offspring must be young
    if to_t['age']!="S" or from_t['age']=='S' or from_t['age']=="K":
        return old
    # consider all possible matings
    weighting = 0
    v = 0
    for other in index_combinations:
        other_d = to_dict(other)
        if other_d['age']=="S":
            continue
        if other_d['age']=="K":
            continue
        if other_d['age']=="O":
            continue
        # young have selection factors
        if from_t["age"]=="Y":
            sym = "".join(from_dict(from_t))+"".join(other)
            sel_fact = symbols(sym)
        else:
            sel_fact = 1
        survival_factor = 1
        s = 1 #get_symbol(other)
        weighting += s
        v += survival_factor*sel_fact*s
#    return v/weighting #TODO: undo this
    return v/3




def sex_propagate2(old,coords,from_t,to_t):
    #offspring must be young
    if to_t['age']!="K" or from_t['age']=='S' or from_t['age']=="K":
        return old
    # consider all possible matings
    weighting = 0
    v = 0
    for other in index_combinations:
        other_d = to_dict(other)
        if other_d['age']=="S":
            continue
        if other_d['age']=="K":
            continue
        if other_d['age']!="O":
            continue
        # young have selection factors
        if from_t["age"]=="Y":
            sym = "".join(from_dict(from_t))+"".join(other)
            sel_fact = symbols(sym)
        else:
            sel_fact = 1
        survival_factor = 1
        s = 1 #get_symbol(other)
        weighting += s
        v += survival_factor*sel_fact*s
#    return v/weighting #TODO: undo this
    return v/3



def age_propagate(old,coords,from_t,to_t):
    if from_t['age']=="S" and to_t['age']=="Y":
        return 1
    elif from_t['age']=="Y" and (to_t['age']=="O" or to_t['age']=="P"):
        # consider all possible matings
        weighting = 0
        v = 0
        for other in index_combinations:
            other_d = to_dict(other)
            if other_d['age']=="S":
                continue
            if other_d['age']=="K":
                continue
                
            # young have selection factors
            sym = "".join(from_dict(from_t))+"".join(other)
            sel_fact = symbols(sym)
            s = 1 #get_symbol(other)
            weighting += s
            v += sel_fact*s
        v = v/weighting
        if to_t['age']=="O":
            return v * 0.1
        else:
            return 1.0-v
    else:
        return old

def total_morph(old,coords,from_t,to_t):
    return old+0.00003



matrix = Matrix([[0 for i in range(N)] for j in range(N)])
apply(matrix,partial(sex_propagate))
apply(matrix,partial(sex_propagate2))
apply(matrix,partial(age_propagate))
apply(matrix,total_morph)
matrix = matrix.transpose()




labels = ["".join(k) for k in index_combinations]


with open('my_matrix.txt',"w") as f:
    sub_dict = {get_symbol(c):symbols("".join(c)) for c in index_combinations}
    transitions_dictionary = defaultdict(list)
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            z = matrix[y,x].subs(sub_dict)
            if z==0:
                continue
            z = str(z)
            label = "{}->{}".format(labels[x],labels[y])
            transitions_dictionary[z].append(label)
    t_keys = list(transitions_dictionary.keys())
    t_values = list(transitions_dictionary.values())
    for i in range(len(t_keys)):
        f.write("{}\n{}\n".format("\n".join(t_values[i]),t_keys[i]))
    #json.dump(transitions_dictionary,f,indent=4)
#raise Exception("early exit")
import pdb
pdb.set_trace()


sim = Simulator(matrix)

try:
#    sim.debug_matrix("hello1.txt",labels)

#    for i in range(8):
#        z = {'YO': (i&4)>>2, 'YP': (i&2)>>1, 'YY': i&1}
#        sim.run_inner(z)
#        print(z,sim.vnorm)

    z = {'YO': 1, 'YP': 1, 'YY': 1}
    sim.load_vg(z)
    
    sim.run(max_inner_iterations=200,
    max_outer_iterations=60000,
    outer_incorporation_factor=0.3,
    outer_iteration_target=0.0,
    inner_iteration_target=1e-12)

#    sim.debug_matrix("hello2.txt",labels)
    
    #print(results)
    #print(outcomes)
except KeyboardInterrupt as e:
    print(e)

#with open("experiment_results1.json","w") as f:
#    json.dump({"outcomes":outcomes,"results":dict(results)},f,indent=3)
