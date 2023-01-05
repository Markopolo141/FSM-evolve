from sympy import symbols, Matrix
import json

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
matrix = Matrix([[0 for i in range(N)] for j in range(N)])

def apply(A,func):
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
        if "P" in list(from_t.values())+other:
            if "P" not in list(from_t.values())+other:
                survival_factor = 0.3
            else:
                survival_factor = 1.0
        else:
            survival_factor = 0.1
        s = get_symbol(other)
        weighting += s
        v += survival_factor*sel_fact*s*punnet_square_likelihood(from_t['genetics'],other_d['genetics'],to_t['genetics'])
    return v/weighting #TODO: undo this
    #return v

apply(matrix,sex_propagate)


coords_keys_bar_age = [a for a in coords_keys if a!='age']
def age_propagate(old,coords,from_t,to_t):
    if False in [from_t[c] == to_t[c] for c in coords_keys_bar_age]:
        return old
    if from_t['age']=="S" and to_t['age']=="Y":
        if from_t['genetics'] == homozygous_positive:
            genetic_factor = 0.9 #1
        elif from_t['genetics'] == hetrozygous:
            genetic_factor = 0.95 #1
        elif from_t['genetics'] == homozygous_negative:
            genetic_factor = 0.1 #1
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
            return v * 0.143546
        else:
            return 1.0-v
    else:
        return old

apply(matrix,age_propagate)


def total_morph(old,coords,from_t,to_t):
    return old+0.01

apply(matrix,total_morph)

output_dictionary = {"matrix":[[str(b) for b in a] for a in matrix.transpose().tolist()],
"max_inner_iterations":200,
"max_outer_iterations":60000,
"outer_incorporation_factor":0.1,
'outer_iteration_target':0.0,
"labels":["".join(l) for l in index_combinations]}
#output_dictionary['initial_vg'] = {}
with open('my_output.json','w') as f:
    json.dump(output_dictionary,f)



