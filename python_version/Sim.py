from pymatrix import *
from sympy.parsing.sympy_parser import parse_expr
from utils import *

import click
import json
import logging

from DerivativeSimulations import EvolveSimulation

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

import pdb

@click.command()
@click.argument('config', type=click.File('r'))
def loadSim(config):
    #pdb.set_trace()
    logger.info("Reading lines from files")
    config_text = config.read()
    config.close()
    logger.info("Translating file text to matricies")
    config_json = {}
    try:
        config_json = json.loads(config_text)
    except:
        logger.error("Failed to parse config file as valid JSON")
        raise
    try:
        switch = Matrix.FromString(config_json['switch'], parser=int)
        choice = Matrix.FromString(config_json['choice'], parser=parse_expr)
    except:
        logger.error("Failed to parse text to matricies")
        raise
    #print "SWITCH-TABLE:\n{}".format(switch)
    #print "CHOICE-TABLE:\n{}".format(choice)
    logger.info("Booting Simulation Instance")
    sim = EvolveSimulation(switch, choice, config_json)
    logger.info("Running Simulation Instance")
    sim.simulate(**config_json['simulate_params'])
    #print "__SIMULATION_END__"
    #print "SWITCH-TABLE:\n{}".format(switch)
    #print "CHOICE-TABLE:\n{}".format(choice)
    #print "FINAL POPULATION\n{}".format(sim.simulation.new_obj.population)
    #print "WEIGHTED-SWITCH-TABLE\n{}".format(weight_switch(switch, sim.simulation.new))
    logger.info("Outputting data")
    out_file = open("{}_output.txt".format(".".join(config.name.split(".")[0:-1])),"w")
    out_file.write("FINAL POPULATION\n{}".format(sim.simulation.new_obj.population))
    out_file.write("WEIGHTED-SWITCH-TABLE\n{}".format(weight_switch(switch, sim.simulation.new)))
    out_file.close()
    
    

if __name__ == '__main__':
    loadSim()
