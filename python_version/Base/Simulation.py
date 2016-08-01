class Simulation:
    def iterate(self):
        raise NotImplementedError
    def getQuality(self):
        raise NotImplementedError
    def getTrait(self):
        raise NotImplementedError
    def getData(self):
        raise NotImplementedError
        
    def simulate(self, target_quality=float("inf"), target_trait_change=float("inf"), repeated=0, min_iterations=1, max_iterations=1000):
        iteration = 0
        old_trait = float("-inf")
        repeats = 0
        while iteration < max_iterations:
            self.iterate()
            iteration = iteration + 1
            new_trait = self.getTrait()
            if self.getQuality() <= target_quality and abs(new_trait-old_trait) <= target_trait_change:
                if iteration >= min_iterations:
                    repeats = repeats + 1
                    if repeats > repeated:
                        return iteration
            else:
                repeats = 0
            old_trait = new_trait
        print "WARNING, SIMULATE REACHED MAX ITERATIONS"
        return iteration
