
from utils import *
from Simulations import ReductionSimulation
from DerivativeSimulations.MutateSimulation import MutateSimulation




class EvolveSimulation(ReductionSimulation):
    switch=None
    choice=None
    config=None
    
    def __init__(self, switch, choice, config):
        assert check_input(switch, choice)
        self.switch = switch
        self.choice = choice
        self.config = config
        
        def alter_func(sim,r):
            sim.muation_shift = r
        
        ReductionSimulation.__init__(
            self,
            MutateSimulation(switch, choice, config['MutateSimulation']),
            alter_func,
            config['initial_reduction'],
            config['reduction_compaction'],
            config['simulate_params']
        )
