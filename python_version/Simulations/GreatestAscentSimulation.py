from utils import *
from Base import Simulation

class GreatestAscentSimulation(Simulation):
    
    def __init__(self, start, generator, pre_function, function, valuer, displacer, distance):
        self.generator = generator
        self.pre_function = pre_function
        self.function = function
        self.valuer = valuer
        self.displacer = displacer
        self.distance = distance
        
        self.new = start
        self.new_pre_function = pre_function(None, start, None, None)
        self.new_obj = function([start], self.new_pre_function)[0]
        self.new_value = valuer(self.new_obj)
        
        self.old = None
        self.old_obj = None
        self.old_pre_function = None
        self.old_value = None
        
    def iterate(self):
        self.old = self.new
        self.old_obj = self.new_obj
        self.old_pre_function = self.new_pre_function
        self.old_value = self.new_value
        
        points = self.generator(self.new)
        objs = self.function(points, self.new_pre_function)
        values = [self.valuer(o) for o in objs]
        index = get_max_index(values)
        
        if values[index] > self.new_value:
            self.new = self.displacer(self.old, points[index])
            self.new_obj = self.function([self.new], self.new_pre_function)[0]
            self.new_pre_function = self.pre_function(self.old, self.new, self.old_obj, self.new_obj)
            self.new_value = self.valuer(self.new_obj)
    
    def getQuality(self):
        return self.distance(self.old, self.new)
        
    def getTrait(self):
        return self.new_value
        
    def getData(self):
        return self.new, self.new_obj
