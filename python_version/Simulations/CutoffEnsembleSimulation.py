from Base import EnsembleSimulation

class CutoffEnsembleSimulation(EnsembleSimulation):
    
    def __init__(self, sims, cuttoff):
        self.cutoff = cutoff
        self.ahead_by = 0
        self.old_ahead = None
        self.ahead = None
        EnsembleSimulation.__init__(self, sims)
        
    def iterate(self):
        self.old_ahead = self.ahead
        if self.ahead_by < self.cutoff:
            map(lambda x:x.iterate(), self.sims)
            self.ahead = get_max_of(self.sims, lambda x:x.getTrait())
            self.ahead_by = self.ahead_by + 1 if self.ahead == self.old_ahead else 0
        else:
            self.ahead.iterate()
    
    def getTrait(self):
        return self.ahead.getTrait()
    
    def getQuality(self):
        return self.ahead.getQuality()
    
    def getData(self):
        return self.ahead
