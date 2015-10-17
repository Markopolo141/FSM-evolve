from pymatrix import *
from sympy.parsing.sympy_parser import parse_expr
from utils import *

import click
import json
import logging

from DerivativeSimulations import EvolveSimulation

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)



@click.command()
@click.argument('config', type=click.File('r'))
def loadSim(config):
    logger.info("Reading lines from files")
    config_text = config.read()
    config.close()
    logger.info("Translating file text to matricies")
    try:
        config = json.loads(config_text)
    except:
        logger.error("Failed to parse config file as valid JSON")
        raise
    try:
        switch = Matrix.FromString(config['switch'], parser=int)
        choice = Matrix.FromString(config['choice'], parser=parse_expr)
    except:
        logger.error("Failed to parse text to matricies")
        raise
    print "SWITCH-TABLE:\n{}".format(switch)
    print "CHOICE-TABLE:\n{}".format(choice)
    logger.info("Booting Simulation Instance")
    sim = EvolveSimulation(switch, choice, config)
    logger.info("Running Simulation Instance")
    sim.simulate(**config['simulate_params'])
    print "__SIMULATION_END__"
    print "SWITCH-TABLE:\n{}".format(switch)
    print "CHOICE-TABLE:\n{}".format(choice)
    print "FINAL POPULATION\n{}".format(sim.simulation.new_obj.population)
    print "WEIGHTED-SWITCH-TABLE\n{}".format(weight_switch(switch, sim.simulation.new))
    
    

if __name__ == '__main__':
    loadSim()
