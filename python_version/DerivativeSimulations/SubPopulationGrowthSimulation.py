from pymatrix import *
from utils import *
from Base import Simulation


class SubPopulationGrowthSimulation(Simulation):
    multiplier_matrix=None
    smoothing_factor=None
    
    old_population=None
    population=None
    
    growth_factor=None
    change_factor=None
    
    def __init__(self, weighted_switch, weighted_choice, config):
        self.smoothing_factor = config['smoothing_factor']
        assert self.smoothing_factor > 0 and self.smoothing_factor < 1
        self.multiplier_matrix = weighted_choice * weighted_switch
        self.population = generate_even_vector(weighted_switch.ncols)
    
    def iterate(self):
        self.old_population = self.population
        self.population = displace(self.old_population, self.multiplier_matrix * self.population, self.smoothing_factor)
        self.growth_factor = sum(self.population)
        self.population = manhattan_normalize(self.population)
        self.change_factor = manhattan_distance(self.population, self.old_population)
        return self.population
    
    def getQuality(self):
        return self.change_factor
        
    def getTrait(self):
        return self.growth_factor
        
    def getData(self):
        return self.population
