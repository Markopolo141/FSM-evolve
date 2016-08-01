from utils import *
from Simulations import GreatestAscentSimulation, SimpleEnsembleSimulation
from DerivativeSimulations.SubPopulationGrowthSimulation import SubPopulationGrowthSimulation

def sim_number_generator(nums, mutation_shift):
    #print "mutation_shift = {}".format(mutation_shift)
    r = []
    for i in range(matrix_len(nums)):
        r.append(nums.copy())
        r[-1].grid[i][0] = displace(r[-1].grid[i][0], 1, mutation_shift)
        r.append(nums.copy())
        r[-1].grid[i][0] = displace(r[-1].grid[i][0], 0, mutation_shift)
    return r


class MutateSimulation(GreatestAscentSimulation):
    
    def __init__(self, switch, choice, config):
        switch_dist = get_distribution(switch)
        num_dim = sum(switch_dist)
        self.mutation_shift = config['mutation_shift']
        
        def func(nums, pre):
            #print "performing an Ensemble Simulation of {}".format(len(nums))
            ensemble = SimpleEnsembleSimulation([SubPopulationGrowthSimulation(weight_switch(switch, n, switch_dist), pre, config['SubPopulationGrowthSimulation']) for n in nums])
            ensemble.simulate(**config['simulate_params'])
            return ensemble.sims
        
        def pre_func(old, new, old_obj, new_obj):
            #print "iterating genetics from {}".format([a for a in new])
            a = None
            if old_obj and new_obj:
                a = displace(old_obj.population, new_obj.population, config['incorporation_factor'])
            elif new_obj and not old_obj:
                a = new_obj.population
            elif not new_obj and not old_obj:
                a = generate_even_vector(switch.ncols)
            else:
                raise Exception("WTF")
            return weight_choice(choice, a)

        def generator(x):
            return sim_number_generator(x,self.mutation_shift)
        
        GreatestAscentSimulation.__init__(self, 
            start           = generate_constant_vector(num_dim, 0.5),
            generator       = generator,
            pre_function    = pre_func,
            function        = func,
            valuer          = lambda x : x.getTrait(),
            displacer       = lambda x,y : displace(x,y,config['mutation_incorporation_factor']),
            distance        = manhattan_distance
        )
        
