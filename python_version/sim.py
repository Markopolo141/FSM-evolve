import json
import click
import operator
from utils import *
from core import *
from tqdm import tqdm

@click.command()
@click.argument('config', type=click.File('rb'))
def simulate(config):
    config_data = json.load(config)
    config.close()
    config = config_data
    
    switch = config['switch']
    choice = parse_matrix_of_expressions(config['choice'])
    i_ip = int(config['power_iterations']["super_iterations"])
    i_i = int(config['power_iterations']["iterations"])
    iterations = int(config['iterations'])
    sequence = eval("lambda x:{}".format(config['sequence']))
    output_formatter = config["output_formatter"]
    if "starting_points" in config:
        pops = [numpy.matrix([manhattan_normalize(s)]).transpose() for s in config['starting_points']]
    else:
        pops = [generate_even_vector(len(choice))]
    if "range_substitutions" in config:
        subs = config["range_substitutions"]
    else:
        subs = {"_":{"min":0,"max":1,"step":1}}
    
    extrema = [numpy.matrix(weight_switch(switch,e)) for e in generate_switch_extrema(switch)]
    output_json = []
    for sub_values in tqdm(multi_iterate(subs)):
        subs_choice = lambdify_matrix(subs_sympy_matrix(choice,sub_values),len(choice))
        for i in range(iterations):
            for p in range(len(pops)):
                extrema_eigen_pairs = [eigen(numpy.matrix(weight_choice(subs_choice,pops[p]))*e,i_ip,i_i) for e in extrema]
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
