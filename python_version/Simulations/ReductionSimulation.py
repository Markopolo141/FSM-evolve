from Base import Simulation
import pdb

class ReductionSimulation(Simulation):

    def __init__(self, simulation, alter_func, initial_reduction, reduction_compaction, simulate_params):
        self.simulation = simulation
        self.reduction = initial_reduction
        self.reduction_compaction = reduction_compaction
        self.alter_func = alter_func
        self.simulate_params = simulate_params
        
        self.old_trait = float("-inf")
        self.new_trait = self.old_trait

    def iterate(self):
        self.old_trait = self.new_trait
        self.alter_func(self.simulation, self.reduction)
        self.simulation.simulate(**self.simulate_params)
        self.new_trait = self.simulation.getTrait()
        self.reduction = self.reduction * self.reduction_compaction
        
    def getQuality(self):
        return abs(self.new_trait - self.old_trait)
        
    def getTrait(self):
        return self.new_trait
        
    def getData(self):
        return self.simulation
