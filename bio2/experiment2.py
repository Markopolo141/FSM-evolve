from solver import *
import numpy as np
from collections import defaultdict
from tqdm import tqdm

logging.getLogger().setLevel(logging.WARNING)

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



genetic_symbols = ['A','B'] # note: must be reversed order under >
invert_key = {genetic_symbols[0]:genetic_symbols[1],genetic_symbols[1]:genetic_symbols[0]}
homozygous_positive = "".join([genetic_symbols[0],genetic_symbols[0]])
hetrozygous = "".join([genetic_symbols[0],genetic_symbols[1]])
homozygous_negative = "".join([genetic_symbols[1],genetic_symbols[1]])
coords = {
"genetics" : [homozygous_positive, hetrozygous, homozygous_negative], # genetic states
"sex" : ["M","F"],
"age" : ["S","Y","O","P"], # super-young, young, old, old-prosperous
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


def apply(matrix,func):
    for i in range(N):
        for j in range(N):
            matrix[i,j] = func(matrix[i,j], (i,j), to_dict(index_combinations[i]), to_dict(index_combinations[j])  )


def invert(A):
    return "".join(sorted([invert_key[a] for a in A]))
def punnet_square_likelihood(parent_A,parent_B,offspring):
    A = sorted([parent_A,parent_B])
    B = sorted([invert(parent_A),invert(parent_B)])
    if A<B:
        parent_A,parent_B=A
    else:
        parent_A,parent_B=B
        offspring = invert(offspring)
    if parent_A == homozygous_positive:
        if parent_B == homozygous_positive:
            if offspring == homozygous_positive:
                return 1
            elif offspring == hetrozygous:
                return 0
            elif offspring == homozygous_negative:
                return 0
            else:
                raise Exception("sos")
        elif parent_B == hetrozygous:
            if offspring == homozygous_positive:
                return 0.5
            elif offspring == hetrozygous:
                return 0.5
            elif offspring == homozygous_negative:
                return 0
            else:
                raise Exception("sos")
        elif parent_B == homozygous_negative:
            if offspring == homozygous_positive:
                return 0
            elif offspring == hetrozygous:
                return 1
            elif offspring == homozygous_negative:
                return 0
            else:
                raise Exception("sos")
        else:
            raise Exception("sos")
    elif parent_A == hetrozygous:
        if parent_B == hetrozygous:
            if offspring == homozygous_positive:
                return 0.25
            elif offspring == hetrozygous:
                return 0.5
            elif offspring == homozygous_negative:
                return 0.25
            else:
                raise Exception("sos")
        else:
            raise Exception("sos")
    else:
        raise Exception("sos")
    


def get_symbol(combination):
    return symbols("x{}".format(index_combinations.index(combination)))

def sex_propagate(old,coords,from_t,to_t):
    #offspring must be young
    if to_t['age']!="S" or from_t['age']=='S':
        return old
    # consider all possible matings
    weighting = 0
    v = 0
    for other in index_combinations:
        other_d = to_dict(other)
        if other_d['age']=="S":
            continue
        if other_d['sex']==from_t['sex']:
            continue
        # young have selection factors
        if from_t["age"]=="Y":
            sym = "".join(from_dict(from_t))+"".join(other)
            #print("consiering: {}".format(sym))
            sel_fact = symbols(sym)
        else:
            sel_fact = 1
        conjoined_state = list(from_t.values())+other
        if "P" in conjoined_state:
            if "O" in conjoined_state or "Y" in conjoined_state:
                survival_factor = hypermodel_symbols['PN']
            else:
                survival_factor = 1.0
        else:
            survival_factor = hypermodel_symbols['NN']
        s = get_symbol(other)
        weighting += s
        v += survival_factor*sel_fact*s*punnet_square_likelihood(from_t['genetics'],other_d['genetics'],to_t['genetics'])
    return v/weighting #TODO: undo this
    #return v



coords_keys_bar_age = [a for a in coords_keys if a!='age']
def age_propagate(old,coords,from_t,to_t):
    if False in [from_t[c] == to_t[c] for c in coords_keys_bar_age]:
        return old
    if from_t['age']=="S" and to_t['age']=="Y":
        if from_t['genetics'] == homozygous_positive:
            genetic_factor = 1
        elif from_t['genetics'] == hetrozygous:
            genetic_factor = hypermodel_symbols['advantage_hetero'] #0.95 #1
        elif from_t['genetics'] == homozygous_negative:
            genetic_factor = hypermodel_symbols['advantage_homo'] #0.1 #1
        return genetic_factor
    elif from_t['age']=="Y" and (to_t['age']=="O" or to_t['age']=="P"):
        # consider all possible matings
        weighting = 0
        v = 0
        for other in index_combinations:
            other_d = to_dict(other)
            if other_d['age']=="S":
                continue
            if other_d['sex']==from_t['sex']:
                continue
            # young have selection factors
            sym = "".join(from_dict(from_t))+"".join(other)
            #print("consiering: {}".format(sym))
            sel_fact = symbols(sym)
            s = get_symbol(other)
            weighting += s
            v += sel_fact*s
        v = v/weighting
        if to_t['age']=="O":
            if from_t['sex']=="F":
                return v * hypermodel_symbols['fertility_factor']
            else:
                return v * 1.0
        else:
            return 1.0-v
    else:
        return old

def total_morph(old,coords,from_t,to_t):
    return old+0.01



matrix = Matrix([[0 for i in range(N)] for j in range(N)])
apply(matrix,partial(sex_propagate))
apply(matrix,partial(age_propagate))
apply(matrix,total_morph)
matrix = matrix.transpose()

'''settings_coords = {
"PN":np.linspace(0.1,0.9,9),
"NN":np.linspace(0.1,0.9,9),
"advantage_hetero":np.linspace(1,1.2,21),
"advantage_homo":np.linspace(0.0,0.9,10),
"fertility_factor":np.linspace(0.0,0.9,10)
}'''

settings_coords = {
"PN":np.linspace(0.0,0.95,20),
"NN":np.linspace(0.0,0.95,20),
"advantage_hetero":np.linspace(1.1,1.1,1),
"advantage_homo":np.linspace(0.1,0.1,1),
"fertility_factor":np.linspace(0.9,0.9,1)
}

assert set(settings_coords.keys())==set(hypermodel_symbols.keys())
settings_coords_keys = sorted(settings_coords.keys())
settings_combinations = dict_combinations([[]],settings_coords,sorted(settings_coords.keys()))
def to_settings_dict(l):
    return {settings_coords_keys[i]:l[i] for i in range(len(l))}

sim = Simulator(matrix, hypermodel_symbols=settings_coords_keys)

outcomes = []
results = defaultdict(list)
#tqdm = list
#import pdb
#pdb.set_trace()
try:
    for settings in tqdm(settings_combinations):
        settings_dict = to_settings_dict(settings)
        #print("Running {}".format(settings_dict))
        
        sim.load_vh(settings)

        max_outer_difference = 0
        max_outer_difference_index = None
        for i in range(len(outcomes)):
            sim.load_vg(outcomes[i])
            outer_difference = sim.outer_run(
            outer_incorporation_factor=0.3,
            max_inner_iterations=200,
            max_outer_iterations=60000,
            inner_iteration_target=1e-6)
            #print("trial {}, outer_difference {}".format(i,outer_difference))
            if outer_difference==0:
                results[i].append(settings)
                break
            else:
                if outer_difference>max_outer_difference:
                    max_outer_difference = outer_difference
                    max_outer_difference_index = i
                continue
        else:
            if max_outer_difference_index == None:
                sim.load_vg(None)
            else:
                sim.load_vg(outcomes[max_outer_difference_index])
            sim.run(max_inner_iterations=200,
            max_outer_iterations=60000,
            outer_incorporation_factor=0.3,
            outer_iteration_target=0.0,
            inner_iteration_target=1e-6)
            outcome = {sim.g[i]:v for i,v in enumerate(sim.vg.transpose().tolist()[0])}
            #print("dum dum dum: {}".format(outcome))
            if outcomes.count(outcome)==0:
                outcome_index = len(outcomes)
                outcomes.append(outcome)
            else:
                outcome_index = outcomes.index(outcome)
            results[outcome_index].append(settings)
        #print(results)
        #print(outcomes)
except KeyboardInterrupt as e:
    print(e)

with open("experiment_results1.json","w") as f:
    json.dump({"outcomes":outcomes,"results":dict(results)},f,indent=3)
