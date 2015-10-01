from Base.Simulation import Simulation
from utils import *

class EnsembleSimulation(Simulation):
    sims = []
    
    def __init__(self, sims):
        self.sims = sims
        
    def iterate(self):
        raise NotImplementedError
    
    def getTrait(self):
        return max([s.getTrait() for s in self.sims])
    
    def getQuality(self):
        return get_max_of(self.sims, lambda x:x.getTrait()).getQuality()
    
    def getData(self):
        return get_max_of(self.sims, lambda x:x.getTrait()).getData()
