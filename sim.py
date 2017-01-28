from tqdm import tqdm
from time import time
import click
import json

functions = []
matricies = []
species =   []
config = {"scooped":True}

from validate import run_input_validation
import pdb
pdb.set_trace()
from Species import Species
from utils import normalise, multi_iterate


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
    config = run_input_validation(config)
    
    output_name = config["output"]
    write_delay = config["write_delay"]
    
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
    
    if config["scooped"]:
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
