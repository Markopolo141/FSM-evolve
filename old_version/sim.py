from core import *
import math
from tqdm import tqdm
import json
import click
import operator
import numpy
import sympy
from sympy import symbols
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify
from scoop import futures, shared
import random
import scoop
from time import time

def process(sub_parameters):
    V = shared.getConst("V")
    sequence = eval("lambda x:{}".format(V['sequence']))
    weight_function = eval(V['weight_function'])
    extrema = V['extrema']
    
    sub_values = {V['subs_symbols'][a]:b[0] for a,b in sub_parameters.iteritems()}
    subs_choice = matrix_map(V['choice'],lambda x,i,j:lambdify(V['pop_symbols'],x.subs(sub_values)))
    pops = [a.copy() for a in V['origional_pops']]
    for i in range(V['iterations']):
        for p in range(len(pops)):
            flattened_pop = [a[0,0] for a in pops[p]]
            weighted_choice = numpy.matrix(matrix_map(subs_choice,lambda x,i,j:x(*flattened_pop)))
            extrema_eigen_pairs = [eigen(weighted_choice*e) for e in extrema]
            random.shuffle(extrema_eigen_pairs)
            extrema_eigen_pairs = sorted(extrema_eigen_pairs, key=operator.itemgetter(0), reverse=True)
            growths = [a[0] for a in extrema_eigen_pairs]
            weights = [weight_function(index,growths) for index in range(len(growths))]
            weights = [a/sum(weights) for a in weights]
            z = sequence(i)
            pops[p] = pops[p]*(1-z) + sum([weights[index]*extrema_eigen_pairs[index][1] for index in range(len(growths))])*z
    return {"parameters":sub_parameters,"pops":[[ppp.sum() for ppp in p] for p in pops]}

@click.command()
@click.argument('config', type=click.File('rb'))
def simulate(config):
    config_data = json.load(config)
    config.close()
    config = config_data
    
    output_formatter = config["output_formatter"]
    subs = {a:b for a,b in config.get("range_substitutions", [["Z",{"min":0,"max":0.5,"step":1}]])}
    if "range_constraints" in config:
        range_constraints = [eval("lambda {}:{}".format(",".join(subs.keys()),con)) for con in config["range_constraints"]]
    else:
        range_constraints = []
    def switch_weighter(vector):
        return lambda x,i,j: x if vector[j] is None else vector[j].pop() if x else 0
    switch = config['switch']
    write_delay = config.get("write_delay",10)
    
    V = {}
    V['choice'] = matrix_map(config['choice'],lambda x,i,j:parse_expr(str(x)))
    V['iterations'] = int(config['iterations'])
    if "starting_points" in config:
        origional_pops = [[a/sum(s) if sum(s)>0 else 1.0/len(s) for a in s] for s in config['starting_points']]
        V['origional_pops'] = [numpy.matrix([a]).transpose() for a in origional_pops]
    else:
        V['origional_pops'] = [numpy.matrix([[1.0/len(V['choice'])] for s in range(len(V['choice']))])]
    V['extrema'] = [numpy.matrix(matrix_map(switch,switch_weighter(e))) for e in generate_switch_extrema(switch)]
    V['pop_symbols'] = [sympy.symbols("s{}".format(i)) for i in range(len(V['choice']))]
    V['subs_symbols'] = {a:symbols(a) for a,b in subs.iteritems()}
    V['sequence'] = config.get('sequence',"1.0/(x+2)")
    V['weight_function'] = config['weight_function']
    shared.setConst(V=V)
    
    output_json = []
    
    big_list = [a for a in multi_iterate(subs) if False not in [con(**a) for con in range_constraints]]
    progress = tqdm(total=len(big_list))
    last_write_time = time()
    def output_file(output_json):
        out_file = file(output_formatter, "w")
        out_file.write(json.dumps({"output":output_json},sort_keys=True).replace('{"parameters":','\n{"parameters":'))
        out_file.flush()
        out_file.close()
    for result in futures.map_as_completed(process, big_list):
        output_json.append(result)
        progress.update()
        if time()-last_write_time > write_delay:
            output_file(output_json)
            last_write_time = time()
    output_file(output_json)
    progress.close()

if __name__ == '__main__':
    simulate()
