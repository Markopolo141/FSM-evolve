import json
import click
import operator
from utils import *
from core import *
from tqdm import tqdm
from sympy import symbols
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify
import cgitb
cgitb.enable(format="text")

@click.command()
@click.argument('config', type=click.File('rb'))
def simulate(config):
    config_data = json.load(config)
    config.close()
    config = config_data
    
    switch = config['switch']
    choice = matrix_map(config['choice'],lambda x,i,j:parse_expr(str(x)))
    i_ip = int(config['power_iterations']["super_iterations"])
    i_i = int(config['power_iterations']["iterations"])
    iterations = int(config['iterations'])
    sequence = eval("lambda x:{}".format(config['sequence']))
    output_formatter = config["output_formatter"]
    if "starting_points" in config:
        origional_pops = [[a/sum(s) if sum(s)>0 else 1.0/len(s) for a in s] for s in config['starting_points']]
        origional_pops = [numpy.matrix([a]).transpose() for a in original_pops]
    else:
        origional_pops = [numpy.matrix([[1.0/len(choice)] for s in range(len(choice))])]
    if "range_substitutions" in config:
        subs = config["range_substitutions"]
    else:
        subs = {"Z":{"min":0,"max":1,"step":1}}
    subs = {symbols(a):b for a,b in subs.iteritems()}
    def switch_weighter(vector):
        return lambda x,i,j: vector[j].pop() if x and vector[j] is not None else 0
    extrema = [numpy.matrix(matrix_map(switch,switch_weighter(e))) for e in generate_switch_extrema(switch)]
    pop_symbols = [sympy.symbols("s{}".format(i)) for i in range(len(choice))]
    
    output_json = []
    for sub_values in tqdm(multi_iterate(subs)):
        
        pops = [a.copy() for a in origional_pops]
        subs_choice = matrix_map(choice,lambda x,i,j:lambdify(pop_symbols,x.subs(sub_values)))
        import pdb
        pdb.set_trace()
        for i in range(iterations):
            for p in range(len(pops)):
                flattened_pop = [a[0,0] for a in pops[p]]
                weighted_choice = numpy.matrix(matrix_map(subs_choice,lambda x,i,j:x(*flattened_pop)))
                extrema_eigen_pairs = [eigen(weighted_choice*e,i_ip,i_i) for e in extrema]
                extrema_growths = [e[0] for e in extrema_eigen_pairs]
                max_extrema_index, growth = max(enumerate(extrema_growths), key=operator.itemgetter(1))
                z = sequence(i)
                pops[p] = pops[p]*(1-z) + extrema_eigen_pairs[max_extrema_index][1]*z
        output_json.append({"parameters":dict([("{}".format(str(iii[0])),"{0:.3f}".format(iii[1])) for iii in sub_values.iteritems()]),"pops":[[[1 if pp.sum()>0.05 else 0 for pp in p],[ppp.sum() for ppp in p]] for p in pops]})
        out_file = file(output_formatter, "w")
        out_file.write(json.dumps({"output":output_json},sort_keys=True).replace('{"parameters":','\n{"parameters":'))
        out_file.flush()
        out_file.close()

if __name__ == '__main__':
    simulate()