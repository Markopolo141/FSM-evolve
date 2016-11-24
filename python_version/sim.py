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
    
    switch = parse_matrix_of_expressions(config['switch'])
    choice = parse_matrix_of_expressions(config['choice'])
    i_ip = int(config['power_iterations']["super_iterations"])
    i_i = int(config['power_iterations']["iterations"])
    iterations = int(config['iterations'])
    sequence = eval("lambda x:{}".format(config['sequence']))
    output_formatter = config["output_formatter"]
    if "starting_points" in config:
        pops = [manhattan_normalize(matrix([s]).transpose()) for s in config['starting_points']]
    else:
        pops = [generate_even_vector(choice.nrows)]
    if "range_substitutions" in config:
        subs = config["range_substitutions"]
    else:
        subs = {"_":{"min":0,"max":1,"step":1}}
    
    extrema = [weight_switch(switch,e) for e in generate_switch_extrema(switch)]
    
    def evaluate_subs_case(**sub_values):
        print sub_values
        subs_choice = subs_sympy_matrix(choice,sub_values)
        out_file = file(output_formatter.format("".join(["{}{}".format(k,sub_values[k]) for k in sub_values.keys()])),"w")
        for i in tqdm(range(iterations)):
            for p in range(len(pops)):
                extrema_eigen_pairs = [eigen(weight_choice(subs_choice,pops[p])*e,i_ip,i_i) for e in extrema]
                extrema_growths = [e[0] for e in extrema_eigen_pairs]
                max_extrema_index, growth = max(enumerate(extrema_growths), key=operator.itemgetter(1))
                z = sequence(i)
                pops[p] = pops[p]*(1-z) + extrema_eigen_pairs[max_extrema_index][1]*z
            out_file.write(str([str(p.transpose()) for p in pops])+"\n")
        out_file.close()
    multi_iterate(evaluate_subs_case,subs)

if __name__ == '__main__':
    simulate()
