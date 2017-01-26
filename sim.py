from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify
from sympy import symbols
from wrapt import ObjectProxy as proxy
from pymatrix import matrix
from tqdm import tqdm
from time import time
import click
import json

def generate_switch_extrema(switch):
    assert False not in [(e==0 or e==1) for r,c,e in switch.elements()], "Switch matrix has entries not zero or one:{}".format(switch)
    dist = [sum([a[i] for a in switch.grid]) for i in range(len(switch.grid[0]))]
    assert False not in [a>0 for a in dist], "Switch matrix has a zero column:{}".format(switch)
    switches = []
    def iterate(i,indices):
        if i < len(dist):
            for o in range(dist[i]):
                iterate(i+1,indices+[o])
        else:
            new_switch = switch.copy()
            for c in range(switch.ncols):
                for r in range(switch.nrows):
                    if new_switch[r][c]==1:
                        if indices[c] != 0:
                            new_switch[r][c]=0
                        indices[c] -= 1
            switches.append(new_switch)
    iterate(0,[])
    return switches

def addTo(e,l):
    for z in l:
        if e==z:
            return z
    l.append(e)
    return e

def normalise(A,B,s=None):
    if s is None:
        s = sum(B)
    if s > 0:
        for i in range(len(A)):
            A[i].__wrapped__ = B[i]/s
    else:
        for i in range(len(A)):
            A[i].__wrapped__ = 0
    return s

def equate(A,B):
    for i in range(len(A)):
        A[i].__wrapped__ = B[i]

def accumu(lis):
    total = 0
    for x in lis:
        yield total
        total += x

def deviation(l):
    min_v = -float("inf")
    max_v = float("inf")
    for a in l:
        if a > min_v:
            min_v = a
        if a < max_v:
            max_v = a
    return max_v-min_v

'''
given a list defining ranges of iterables in form 
[["count1":{"min":0,"max":5,"step":1}],...} return a list of dicts of all combinations of thoes values (together with the index of their iterations)
note: "step" is optional on each
'''
def multi_iterate(d):
    l = []
    def sub_method(vals,indices,i):
        if i<len(d):
            count = d[i][1]["min"]
            index = 0
            while count < d[i][1]["max"]:
                sub_method(vals + [count],indices + [index],i+1)
                count = d[i][1]["min"]+index*d[i][1].get("step",1)
                index += 1
        else:
            l.append({d[o][0]:(vals[o],indices[o]) for o in range(i)})
    sub_method([],[],0)
    return l

functions = []
matricies = []
species =   []
config = {"scooped":True}

class PaddedFunction:
    def __init__(self, expr):
        self.strE = str(expr)
        self.atoms = [a for a in list(expr.atoms()) if not a.is_constant()]
        self.values = {str(a):None for a in self.atoms}
        self.value = None
        self.f = lambdify(self.atoms,expr,dummify=False)
    def update(self):
        self.value = self.f(**self.values)
    def connect(self,dictionary):
        for k in self.values.keys():
            try:
                d = dictionary[k]
            except KeyError:
                print "Error: cannot connect function {} with atoms {}, to dictionary with keys {}".format(self.strE,self.values.keys(),dictionary.keys())
                raise
            self.values[k] = d
    def __eq__(self,other):
        return self.strE == other.strE

class PaddedMatrix:
    def __init__(self, M):
        M = M.map(lambda x:x.simplify())
        self.strM = str(M)
        self.replacements = []
        for r,c,e in M.elements():
            if e.is_constant():
                M[r][c] = float(e)
            else:
                self.replacements.append((r,c,addTo(PaddedFunction(e),functions)))
                M[r][c] = None
        self.M = M
    def update(self):
        for r,c,f in self.replacements:
            self.M[r][c]=f.value
    def __eq__(self, other):
        return self.strM == other.strM

class SubSpecies:
    def __init__(self,M,number=1,numbers=None,col_pruning=False,row_pruning=True):
        row_absence = [(False not in [r.is_zero is True for r in row]) and not(row_pruning) for row in M.rows()]
        column_absence = [(False not in [r.is_zero is True for r in col]) and not(col_pruning) for col in M.cols()]
        self.absence = [row_absence[i] or column_absence[i] for i in range(M.nrows)]
        self.map = B = list(accumu([1 if not(a) else 0 for a in self.absence]))
        rows_present = sum([1 for a in self.absence if not(a)])
        self.oldvalues = [proxy(number/rows_present) for i in range(M.nrows) if not self.absence[i]]
        self.newvalues = [proxy(number/rows_present) for i in range(M.nrows) if not self.absence[i]]
        self._temp = [0]*M.nrows
        removed_states = 0
        for index,a in enumerate(self.absence):
            if a:
                removed_states += 1
                M = M.del_row_col(index-removed_states+1,index-removed_states+1)
        self.M = addTo(PaddedMatrix(M),matricies)
    def update(self,smoothing):
        mm = self.M.M.grid
        ov = self.oldvalues
        inverse_smoothing = 1-smoothing
        temp = self._temp
        for r in range(len(self.oldvalues)):
            s = 0
            for c in range(self.M.M.ncols):
                s += mm[r][c]*ov[c]*inverse_smoothing
            s += smoothing*ov[r]
            temp[r] = s
        equate(self.newvalues,temp)
    def turnOver(self):
        for i in range(len(self.oldvalues)):
            nv = self.newvalues[i]
            ov = self.oldvalues[i]
            t = nv.__wrapped__
            nv.__wrapped__ = ov.__wrapped__
            ov.__wrapped__ = t
    def __getitem__(self, key):
        if self.absence[key] is True:
            return 0
        else:
            return self.newvalues[self.map[key]]

class Species:
    def __init__(self, switch, choice, distribution=None,sub_distributions=None,col_pruning=False,row_pruning=True,preliminary_subs={}):
        self.num_states = len(choice)
        self.sub_species = []
        self.values = [proxy(0) for i in range(self.num_states)]
        self.svalues = [proxy(0) for i in range(self.num_states)]
        self.value = proxy(0)
        extrema = generate_switch_extrema(matrix(switch))
        preliminary_subs = {symbols(a):b[0] for a,b in preliminary_subs.iteritems()}
        choice = matrix(choice).map(lambda x:parse_expr(str(x)).subs(preliminary_subs))
        for i,e in enumerate(extrema):
            if sub_distribution is not None:
                self.sub_species.append(SubSpecies(choice*e,numbers=sub_distribution[i]))
            elif distribution is not None
                self.sub_species.append(SubSpecies(choice*e,distribution[i]))
            else:
                self.sub_species.append(SubSpecies(choice*e,1.0))
    def updateValues(self):
        for i in range(self.num_states):
            counter = 0
            for s in self.sub_species:
                counter += s[i]
            self.values[i].__wrapped__ = counter
        self.value.__wrapped__ = sum(self.values)
        normalise(self.svalues,self.values)
    def update(self,smoothing):
        for s in self.sub_species:
            s.update(smoothing)
        self.updateValues()
    def turnOver(self):
        for s in self.sub_species:
            s.turnOver()

def process(sub_parameters):
    global config
    if config.get("scooped",False):
        from scoop import shared
        config = shared.getConst("config")
    dictionary = {}
    values = []
    cvalues = []
    svalues = []
    recent_values = []

    for i,p in enumerate(config['species']):
        p.update({"preliminary_subs":sub_parameters,"col_pruning":config.get("col_pruning",None),"row_pruning":config.get("row_pruning",None)})
        s = Species(**p)
        species.append(s)
        for o,ss in enumerate(s.sub_species):
            for n in range(s.num_states):
                dictionary["S{}P{}T{}".format(i,o,n)] = ss[n]
            for nv in ss.newvalues:
                values.append(nv)
        for n in range(s.num_states):
            dictionary["S{}T{}".format(i,n)] = s.values[n]
            cvalues.append(s.values[n])
            dictionary["V{}T{}".format(i,n)] = s.svalues[n]
        dictionary["S{}".format(i)] = s.value
        svalues.append(s.value)
    [f.connect(dictionary) for f in functions]
    recent_values = [[] for v in values]
    
    [s.updateValues() for s in species]
    normalise(values,values,normalise(cvalues,cvalues))
    for i in range(config['max_iterations']):
        [f.update() for f in functions]
        [m.update() for m in matricies]
        [s.update(config['smoothing']) for s in species]
        normalise(values,values,normalise(cvalues,cvalues,normalise(svalues,svalues)))
        for o,v in enumerate(values):
            recent_values[o].append(v.__wrapped__)
        if (i>=config['convergence_sample_size']):
            max_d = 0
            for v in recent_values:
                v.pop(0)
                max_d = max(max_d,deviation(v))
            if max_d < config['convergence_sd']:
                dictionary = {a:float(b) for a,b in dictionary.iteritems()}
                dictionary.update({"Converged":True})
                return [sub_parameters,dictionary]
        [s.turnOver() for s in species]
    return [sub_parameters,{"Converged":False}]

@click.command()
@click.argument('conf', type=click.File('rb'))
def simulate(conf):
    global config
    config = json.load(conf)
    conf.close()
    output_name = config.get("output","out.txt")
    write_delay = config.get("write_delay",10)
    
    if "range_substitutions" in config:
        subs = config["range_substitutions"]
        subs_keys = [s[0] for s in subs]
        range_constraints = []
        for con in config.get("range_constraints",[]):
            range_constraints.append(eval("lambda {}:{}".format(",".join(subs_keys),con)))
        substitutions = [a for a in multi_iterate(subs) if False not in [con(**a) for con in range_constraints]]
    else:
        substitutions = [{}]
    progress = tqdm(total=len(substitutions))
    last_write_time = time()
    
    def output_file(output_data):
        output = file(output_name, "w")
        output.write(json.dumps({"output":output_data},sort_keys=True).replace('], [','],\n['))
        output.flush()
        output.close()

    if config.get("scooped",False):
        from scoop import futures, shared
        shared.setConst(config=config)
        generator = futures.map_as_completed(process, substitutions)
    else:
        def tmp(A):
            for a in A:
                yield process(a)
        generator = tmp(substitutions)
    
    output_data = []
    for result in generator:
        output_data.append(result)
        progress.update()
        if time()-last_write_time > write_delay:
            output_file(output_data)
            last_write_time = time()
    output_file(output_data)
    progress.close()

if __name__ == '__main__':
    simulate()
