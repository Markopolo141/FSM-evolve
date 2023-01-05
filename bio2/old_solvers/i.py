from sympy import symbols, Matrix, diff
from sympy.parsing.sympy_parser import parse_expr
from numpy import matrix
from numpy.linalg import norm
import json
from functools import partial
import click
import logging
import time
import pdb

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

# take v in the vector direction diff, 
# where v is constrained in the unit cube
# auto scales the diff to make the length of the path 
# travelled around the edge of the cube = norm(diff)
def box_accent(v,diff):
    dd = norm(diff)
    while True:
        old_v = v
        v = (v+diff).clip(0,1)
        v_minus_old_v = v-old_v
        norm_v_minus_old_v = norm(v_minus_old_v)
        if norm_v_minus_old_v==0:
            return v
        dd = max(dd-norm_v_minus_old_v-0.0001,0)
        diff = dd*v_minus_old_v/norm_v_minus_old_v


# for a symbolic expression string <element>, consisting of <symbols>
# variables, compile the expression as a executable lambda,
# in global namespace 
def dumb_lambdify(symbols,element):
    s = "lambda {} : {}".format(",".join(symbols),repr(element))
    return eval(s, globals())





class Simulator(object):
    N = None
    A = None
    dA = None
    
    v = None
    s = None
    s_symbols = None

    vg = None
    g = None
    g_symbols = None

    vnorm = None

    def get_dict(self):
        return {self.s[i]:float(vv) for i,vv in enumerate(self.v)}
    def get_g_dict(self):
        return {self.g[i]:float(vvg) for i,vvg in enumerate(self.vg)}

    def __init__(self, input_matrix, initial_vg=None):
         # extract the dimensions of the matrix
        assert isinstance(input_matrix, Matrix)
        assert input_matrix.shape[0] == input_matrix.shape[1]
        self.N = input_matrix.shape[0]

        # setup the initial vectors
        self.v = matrix([[0.5] for i in range(self.N)])
        self.s = ["x{}".format(i) for i in range(self.N)]
        self.s_symbols = [symbols(x) for x in self.s]

        # extract genetic symbols
        self.g_symbols = set()
        for ddd in input_matrix.values():
            for sym in ddd.free_symbols:
                if sym not in self.s_symbols:
                    self.g_symbols.add(sym)
        self.g_symbols = [a[1] for a in sorted([(str(s),s) for s in list(self.g_symbols)])]
        self.g = [str(gg) for gg in self.g_symbols]
        logging.debug("detecting genetic symbols: {}".format(self.g_symbols))
        
        # setup the genetic vectors
        if initial_vg is not None:
            assert len(initial_vg.values())==len(self.g_symbols)
            self.vg = matrix([[initial_vg[gg]] for gg in self.g])
        else:
            self.vg = matrix([[0.5] for gg in self.g])

        # compile away our sympy expressions - for speed
        self.A = dumb_lambdify(self.s+self.g,matrix(input_matrix))
        self.dA = [dumb_lambdify(self.s+self.g,matrix(diff(input_matrix,gg))) for gg in self.g_symbols]
        self.vnorm = None


    def run_inner(self,
    substitions,
    max_inner_iterations=200,
    inner_incorporation_factor=0.5,
    inner_iteration_target=1e-5,
    **extra_arguments
    ):
        # reduce the data to genetic data array
        A_x = partial(self.A,**substitions)
        # do iterations to find a stable point
        old_old_v = self.v.copy()
        self.vnorm = None
        i = 0
        inner_t = time.time()
        inner_difference = float('inf')
        while ((i<max_inner_iterations) and 
        (inner_difference>inner_incorporation_factor*inner_iteration_target)):
            i += 1
            old_v = self.v.copy()
            A_xx = A_x(**self.get_dict())
            if (A_xx<0).any():
                logging.warning("negative matrix encountered")
                A_xx.clip(0)
            self.v[:,:] = ((1.0-inner_incorporation_factor)*self.v + 
                inner_incorporation_factor*A_xx*self.v)
            self.vnorm = self.v.sum()
            self.v[:,:] = self.v / self.vnorm
            inner_difference = norm(self.v - old_v)
        if i==max_inner_iterations:
            logging.warning("Reached max inner iterations")
        ret = [i,time.time()-inner_t, norm(self.v-old_old_v)]
        logging.info("inner took: {0} iters, {1:.4g}s, delta={2:.4g}".format(*ret))
        return ret



    def run(self, 
    max_outer_iterations=200,
    outer_incorporation_factor=0.01,
    outer_iteration_target=1e-3,
    **inner_arguments
    ):
        # begin primary loop
        logging.info("Beginning simulation loop")
        j = 0
        outer_difference = float('inf')
        while ((j<max_outer_iterations) and 
        (outer_difference>outer_incorporation_factor*outer_iteration_target)):
            j += 1
            logging.info("beginning {} inner loop".format(j))
            self.run_inner(self.get_g_dict(),**inner_arguments)

            # calculate the vector of perturbations in eigenvalue
            delta_lambda = []
            arguments = self.get_dict()
            arguments.update(self.get_g_dict())
            for gg in range(len(self.g_symbols)):
                delta_lambda.append([(self.v.transpose()*(self.dA[gg](**arguments)*self.v))[0,0]])
            delta_lambda = matrix(delta_lambda)
            #logging.info("dLambda = {}".format(norm(delta_lambda)))
            delta_lambda = delta_lambda / (0.1+norm(delta_lambda))
            delta_lambda *= outer_incorporation_factor
            old_vg = self.vg.copy()
            self.vg[:,:] = box_accent(self.vg,delta_lambda)
            outer_difference = norm(self.vg-old_vg)
            logging.info("diff_Lambda = {}".format(outer_difference))
        if j==max_outer_iterations:
            logging.warning("Reached max outer iterations, simulation failed to converge")

    def debug_matrix(self,filename, labels):
        self.run_inner(self.get_g_dict(),**inner_arguments)
        arguments = self.get_dict()
        arguments.update(self.get_g_dict())
        A_xx = self.A(**arguments)
        with open(filename,"w") as ff:
            for a in A_xx.tolist():
                for b in a:
                    z = round(float(b*100))
                    if z!=0:
                        ff.write("{:03d} ".format(z) )
                    else:
                        ff.write("    ")
                ff.write("\n")
            ff.write("\n")
            for i in range(self.N):
                ff.write("{} = {}\n".format(labels[i],float(self.v[i])))

    def print_state(self):
        print("Lambda = {}".format(self.vnorm))
        print(self.v)
        for i in range(len(self.v)):
            print("{}:\t{}".format(self.s_symbols[i],self.v[i,0]))
        for i in range(len(self.vg)):
            print("{}:\t{}".format(self.g_symbols[i],self.vg[i,0]))






@click.command()
@click.argument('config_file', type=click.File('r'))
def run(config_file):
    logging.info("Starting simulation on file: {}".format(config_file))
    # load config file as JSON
    config = json.load(config_file)
    config_file.close()
    
    # load parameters
    assert isinstance(config,dict), 'config must be JSON dictionary'
    assert 'matrix' in config.keys(), 'config must have "matrix" specified'
    data = config['matrix']

    assert isinstance(data, list), 'matrix must be specified as array of arrays'
    N = len(data)
    assert False not in [len(d)==N for d in data], 'matrix must be square'
    logging.debug("Matrix size: {}".format(N))

    data = [[parse_expr(ddd) for ddd in dd] for dd in data]
    data = Matrix(data)

    initial_vg = config.get("initial_vg",None)
    sim = Simulator(data, initial_vg)
    
    # begin primary loop
    try:
        sim.run(**config)
    except KeyboardInterrupt as e:
        print(e)
    sim.print_state()        


if __name__ == '__main__':
    run()
