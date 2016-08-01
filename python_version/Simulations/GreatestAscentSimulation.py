from utils import *
from Base import Simulation

'''
Greatesst Ascent Simulator:

A general simulation that crawls coordinates to the principal point of the function 'function'

inputs:
* start:        a coordinate space point to start from
* generator:    a function when given a coordinate space point generates an array of new coordinate space points to test (not including the origional point)
* pre_function: calculates a thing from the old&new points&objects to be used in the new call of the function
* function:     returns an array of objects from which the valuer can extract the numerical value/priority of. inputs are an array of coordinate points, and the pre-function value
* valuer:       given an object returned by the function itself, return the value of it (in some sense)
* displacer:    a function that computes the resulting coordinate space point of the origional central point displaced somewhat towards the new (and better) point.
* distance:     a function to compute the distance between two coordinate space points
'''
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
        self.old_value = None
        
    def iterate(self):
        self.old = self.new
        self.old_obj = self.new_obj
        self.old_value = self.new_value
        
        points = self.generator(self.new)
        objs = self.function(points, self.new_pre_function)
        values = [self.valuer(o) for o in objs]
        index = get_max_index(values)
        
        #print "GreatestAscentSim: new increase from {} to {}: {}".format(self.new_value, values[index], values[index]-self.new_value)
        if values[index] > self.new_value:
            self.new = self.displacer(self.old, points[index])
            self.new_obj = self.function([self.new], self.new_pre_function)[0]
            self.new_pre_function = self.pre_function(self.old, self.new, self.old_obj, self.new_obj)
            self.new_obj = self.function([self.new], self.new_pre_function)[0]
            self.new_value = self.valuer(self.new_obj)
    
    def getQuality(self):
        return self.distance(self.old, self.new)
        
    def getTrait(self):
        return self.new_value
        
    def getData(self):
        return self.new, self.new_obj
