from solver4 import *
import numpy as np
from collections import defaultdict
from tqdm import tqdm
from random import shuffle

logging.getLogger().setLevel(logging.WARNING)
#logging.getLogger().setLevel(logging.INFO)

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

# given genotype of the parents, return the likelihood that they return the genotype of the offspring.
def punnet_square_likelihood(parent_A,parent_B,offspring):
    # symmetry swapping
    A = sorted([parent_A,parent_B])
    B = sorted([invert(parent_A),invert(parent_B)])
    if A<B:
        parent_A,parent_B=A
    else:
        parent_A,parent_B=B
        offspring = invert(offspring)
    # the punnet square logic of genotype of offspring liklihood (with mutation factor)
    #EXPRESSION GENERATING CODE:
    '''from sympy import symbols, expand, simplify
    m = symbols('m')
    ex = lambda x: simplify(x)#expand(x)
    def mate(a,b):
        return (ex((a[0]+a[1])*(b[0]+b[1])/4),
                ex((a[0]+a[1])*(2-b[0]-b[1])/4 + (2-a[0]-a[1])*(b[0]+b[1])/4),
                ex((2-a[0]-a[1])*(2-b[0]-b[1])/4) )
    array = {"hop":[1-m,1-m],"he":[1-m,m],"hon":[m,m]}
    array_keys = array.keys()
    for a in array_keys:
        for b in array_keys:
            m = mate(array[a],array[b])
            print(a,b,m,simplify(sum(m)))'''
    
    if parent_A == homozygous_positive:
        if parent_B == homozygous_positive:
            if offspring == homozygous_positive:
                return (1 - hypermodel_symbols['mut'])**2
            elif offspring == hetrozygous:
                return 2*hypermodel_symbols['mut']*(1-hypermodel_symbols['mut'])
            elif offspring == homozygous_negative:
                return hypermodel_symbols['mut']**2
        elif parent_B == hetrozygous:
            if offspring == homozygous_positive:
                return 0.5*(1-hypermodel_symbols['mut'])
            elif offspring == hetrozygous:
                return 0.5
            elif offspring == homozygous_negative:
                return 0.5*hypermodel_symbols['mut']
        elif parent_B == homozygous_negative:
            if offspring == homozygous_positive:
                return hypermodel_symbols['mut']*(1-hypermodel_symbols['mut'])
            elif offspring == hetrozygous:
                return (1 - hypermodel_symbols['mut'])**2 + hypermodel_symbols['mut']**2
            elif offspring == homozygous_negative:
                return hypermodel_symbols['mut']*(1-hypermodel_symbols['mut'])
    elif parent_A == hetrozygous:
        if parent_B == hetrozygous:
            if offspring == homozygous_positive:
                return 0.25
            elif offspring == hetrozygous:
                return 0.5
            elif offspring == homozygous_negative:
                return 0.25
    raise Exception("Punnet Square Senseless Exception")
    


def get_symbol(combination):
    return symbols("x{}".format(index_combinations.index(combination)))

def get_selection_symbol(from_t,other):
    if from_t["age"]=="Y":
        sym = "".join(from_dict(from_t))+"".join(other)
        #print("consiering: {}".format(sym))
        sel_fact = symbols(sym)
    else:
        sel_fact = 1
    return sel_fact

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
        sel_fact = get_selection_symbol(from_t,other)
        sel_fact *= get_selection_symbol(other_d,from_dict(from_t)) #optional mutuality of choice
        
        conjoined_state = list(from_t.values())+other
        if "P" in conjoined_state:
            if "O" in conjoined_state or "Y" in conjoined_state:
                survival_factor = hypermodel_symbols['PN']
            else:
                survival_factor = 1.0
        else:
            survival_factor = 0.5*hypermodel_symbols['PN']**2 #hypermodel_symbols['NN']
        s = get_symbol(other)
        weighting += s
        v += survival_factor*sel_fact*s*punnet_square_likelihood(from_t['genetics'],other_d['genetics'],to_t['genetics'])
    return v/weighting #optional weighting factor
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
            sel_fact = symbols(sym)
            s = get_symbol(other)
            weighting += s
            v += sel_fact*s
        v = v/weighting #optional weighting factor
        if to_t['age']=="O":
            if from_t['sex']=="F":
                return v * hypermodel_symbols['fertility_factor']
            else:
                return v * 1.0
        else:
            return 1.0-v
    else:
        return old

# populate the matrix with some small factor to keep everyting well behaved
def total_morph(old,coords,from_t,to_t):
    return old+0.00003



matrix = Matrix([[0 for i in range(N)] for j in range(N)])
apply(matrix,partial(sex_propagate))
apply(matrix,partial(age_propagate))
apply(matrix,total_morph)
matrix = matrix.transpose()



settings_coords = {
"PN":np.linspace(0.01,1.0,100),
"advantage_hetero":np.linspace(0.01,1.50,150),
"advantage_homo":np.linspace(0.0,0.0,1),
"fertility_factor":np.linspace(0.9,0.9,1),
"mut":np.linspace(0.01,0.01,1)
}



#settings_coords = {
#"PN":np.linspace(0.67,0.67,1),
#"advantage_hetero":np.linspace(0.04,0.04,1),
#"advantage_homo":np.linspace(0.0,0.0,1),
#"fertility_factor":np.linspace(0.9,0.9,1),
#"mut":np.linspace(0.01,0.01,1)
#}



# test the hypothesis that more resource abundance will shift
# emphasis to good genes.
#
# ie. when PN>NN and fertility factor will mediate between selection
# of genetic type

assert set(settings_coords.keys())==set(hypermodel_symbols.keys())
settings_coords_keys = sorted(settings_coords.keys())
settings_combinations = dict_combinations([[]],settings_coords,sorted(settings_coords.keys()))
#shuffle(settings_combinations)
def to_settings_dict(l):
    return {settings_coords_keys[i]:l[i] for i in range(len(l))}

labels = ["".join(k) for k in index_combinations]
sim = Simulator(matrix, hypermodel_symbols=settings_coords_keys)

outcomes = []
results = defaultdict(list)
#tqdm = list


max_outer_iterations=500
outer_incorporation_factor=0.5
outer_iteration_target= 1e-6 #0
max_inner_iterations=2000
inner_iteration_target=1e-8

rehash_max_outer_iterations=10

max_delta_magnitude= 1.0
inner_delta_multiplier=float('inf')#10000.0


with open("vector_debug.txt","w") as f:
    f.write("header\n")

try:
    for settings in tqdm(settings_combinations):
        settings_dict = to_settings_dict(settings)
        #print("Running {}".format(settings_dict))

        sim.load_vh(settings_dict)

        max_outer_difference = float('inf')
        max_outer_difference_index = None
        for i in range(len(outcomes)):
            sim.load_vg(outcomes[i])
            try:
                outer_difference, stability = sim.outer_run(
                outer_incorporation_factor=outer_incorporation_factor,
                max_inner_iterations=max_inner_iterations,
                max_outer_iterations=rehash_max_outer_iterations,
                inner_iteration_target=inner_iteration_target,
                max_delta_magnitude=max_delta_magnitude,
                inner_delta_multiplier=inner_delta_multiplier,
                randomising_step = False)
            except ConvergenceException as e:
                continue
            #print("trial {}, outer_difference {}".format(i,outer_difference))
            if outer_difference==0:
                settings_dict['vector'] = dict(zip(labels,sim.v.transpose().tolist()[0]))
                settings_dict['stability']=stability
                results[i].append(settings_dict)
                break
            else:
                #if outer_difference<max_outer_difference: #TODO < or >?
                #    max_outer_difference = outer_difference
                #    max_outer_difference_index = i
                continue
        else:
            if max_outer_difference_index == None:
                sim.load_vg(None)
            else:
                sim.load_vg(outcomes[max_outer_difference_index])

            try:
                print(settings_dict)
                converged,stability = sim.run(max_inner_iterations=max_inner_iterations,
                max_outer_iterations=max_outer_iterations,
                outer_incorporation_factor=outer_incorporation_factor,
                outer_iteration_target=outer_iteration_target,
                inner_iteration_target=inner_iteration_target,
                max_delta_magnitude=max_delta_magnitude,
                inner_delta_multiplier=inner_delta_multiplier
                )
            except ConvergenceException as e:
                # using the averaged vg and v as data
                outcome = {sim.g[i]:v for i,v in enumerate(sim.vg_averaged.transpose().tolist()[0])}
                outcome_index = len(outcomes)
                outcomes.append(outcome)
                settings_dict['vector'] = dict(zip(labels,sim.v_averaged.transpose().tolist()[0]))
                settings_dict['stability']=999
                results[outcome_index].append(settings_dict)
                
                #pass # formerly pass
                continue

            outcome = {sim.g[i]:v for i,v in enumerate(sim.vg.transpose().tolist()[0])}
            if outcomes.count(outcome)==0:
                outcome_index = len(outcomes)
                outcomes.append(outcome)
            else:
                outcome_index = outcomes.index(outcome)
            settings_dict['vector'] = dict(zip(labels,sim.v.transpose().tolist()[0]))
            settings_dict['stability']=stability
            results[outcome_index].append(settings_dict)
        #print(results)
        #print(outcomes)
except KeyboardInterrupt as e:
    print(e)

with open("experiment_results1.json","w") as f:
    json.dump({"outcomes":outcomes,"results":dict(results)},f,indent=3)
