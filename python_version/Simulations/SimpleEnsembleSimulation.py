from Base import EnsembleSimulation

class SimpleEnsembleSimulation(EnsembleSimulation):
    def iterate(self):
        for s in self.sims:
            s.iterate()
