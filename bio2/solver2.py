from sympy import symbols, Matrix, diff, eye
from sympy.parsing.sympy_parser import parse_expr
from numpy import matrix, hstack, multiply
from numpy.linalg import norm, lstsq
from numpy.random import randint
import json
from functools import partial
import click
import logging
import time

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def dot(sA,sB):
    rA = [float(a) for a in sA]
    rB = [float(b) for b in sB]
    N = len(rA)
    assert N==len(rB)
    return sum([rA[i]*rB[i] for i in range(N)])

# takes the vector from A->B, and return the point 
# where the line defined by that vector crosses the plane centered at C with normal dC
def line_plane_constrain(A,B,C,dc):
    Adc = dot(A,dc)
    Bdc = dot(B,dc)
    Cdc = dot(C,dc)
    return (A*(Bdc-Cdc)+B*(Cdc-Adc))/(Bdc-Adc)

# take v in the vector direction diff, 
# where v is constrained in the unit cube
# and within the planes specified by the constraints
# auto scales the sequence diff to make the length of the path 
# travelled around the edges of the constraints = norm(diff)

#TODO: FIX THIS FUNCTION

def box_accent(v,diff, constraints):
    epsilon = 1e-6
    dd = norm(diff)
    constraints = [(c,dc/norm(dc)) for c,dc in constraints]
    while True:
        old_v = v
        print(v,diff)
        v = v+diff
        print(v)
        new_diff = diff
        
        # apply 0-1 bounding box
        '''for i in range(len(v)):
            if v[i,0]>1:
                p = (1-old_v[i,0])/(v[i,0]-old_v[i,0])
                v = p*v+(1-p)*old_v
                v[i,0]=1.0
                new_diff = diff.copy()
                new_diff[i,0]=0.0
                print("ping {}".format(i))
            elif v[i,0]<0:
                p = (0-old_v[i,0])/(v[i,0]-old_v[i,0])
                v = p*v+(1-p)*old_v
                v[i,0]=0.0
                new_diff = diff.copy()
                new_diff[i,0]=0.0
                print("pong {}".format(i))'''

        # apply other constraints
        for c,dc in constraints:
            violation = dot((v-c),dc)
            if violation<-epsilon: #constraint clearly violated
                print("ptwang")
                v = line_plane_constrain(old_v,v,c-epsilon*dc,dc)
                new_diff = diff-(v-old_v)
                new_diff -= dot(dc,new_diff)*dc + epsilon*dc

        # do calculus and scaling
        diff=new_diff
        norm_diff = norm(diff)
        v_minus_old_v = v-old_v
        norm_v_minus_old_v = norm(v_minus_old_v)
        if norm_v_minus_old_v==0 or norm_diff==0:
            violation_exists = True
            while violation_exists:
                violation_exists = False
                for c,dc in constraints:
                    violation = dot((v-c),dc)
                    v = line_plane_constrain(old_v,v,c,dc)
                    violation_exists = True
                for i in range(len(v)):
                    if v[i,0]>1:
                        v[i,0]=1.0
                        violation_exists = True
                    elif v[i,0]<0:
                        v[i,0]=0.0
                        violation_exists = True
            return v
        dd = max(dd-norm_v_minus_old_v-epsilon,0)
        diff = dd*diff/norm(diff)



# for a symbolic expression string <element>, consisting of <symbols>
# variables, compile the expression as a executable lambda,
# in global namespace 
def dumb_lambdify_matrix(symbols,element):
    s = "lambda {} : matrix({},dtype=float)".format(",".join(symbols),repr(element))
    return eval(s, globals())



# thrown when convergenc failed (can be for multiple reasons...)
class ConvergenceException(Exception):
    pass




class Simulator(object):
    N = None
    A = None
    dA = None

    w = None
    v = None
    s = None
    s_symbols = None

    vg = None
    g = None
    g_symbols = None

    vnorm = None
    wnorm = None

    hypermodel_symbols = None
    hypermodel = None
    v_hypermodel = None

    def get_dict(self):
        if self.v.shape[1]!=0:
            return {self.s[i]:float(vv) for i,vv in enumerate(self.v)}
        return {}
                
    def get_g_dict(self):
        if self.vg.shape[1]!=0:
            return {self.g[i]:float(vvg) for i,vvg in enumerate(self.vg)}
        return {}
    def get_h_dict(self):
        if self.v_hypermodel.shape[1]!=0:
            return {self.hypermodel[i]:float(vvh) for i,vvh in enumerate(self.v_hypermodel)}
        return {}

    def load_vg(self,initial_vg=None):
        if initial_vg is not None:
            assert len(initial_vg.values())==len(self.g_symbols)
            self.vg = matrix([[float(initial_vg[gg])] for gg in self.g])
        else:
            self.vg = matrix([[0.5] for gg in self.g])
    
    def load_vh(self,v_hypermodel=None):
        if v_hypermodel is not None:
            assert len(v_hypermodel)==len(self.hypermodel)
            self.v_hypermodel = matrix([[float(v_hypermodel[gg])] for gg in self.hypermodel])
        else:
            self.v_hypermodel = matrix([[0.0] for i in range(len(self.hypermodel))])


    def __init__(self, input_matrix, initial_vg=None, hypermodel_symbols=None, initial_vh=None):
         # extract the dimensions of the matrix
        assert isinstance(input_matrix, Matrix)
        assert input_matrix.shape[0] == input_matrix.shape[1]
        self.N = input_matrix.shape[0]
        self.lambda_symbol = symbols('l')

        # setup the initial vectors
        self.v = matrix([[0.5] for i in range(self.N)])
        self.w = matrix([[0.5] for i in range(self.N)])
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
        
        # exclude hypermodel symbols
        self.hypermodel_symbols = []
        self.hypermodel = []
        if hypermodel_symbols is not None:
            for gg in hypermodel_symbols:
                if gg in self.g:
                    sym = self.g_symbols[self.g.index(gg)]
                    self.hypermodel.append(gg)
                    self.hypermodel_symbols.append(sym)
                    self.g.remove(gg)
                    self.g_symbols.remove(sym)
            if len(self.hypermodel_symbols)!=len(hypermodel_symbols):
                logging.warn("hypermodel symbols specified by not present")
        self.load_vh(initial_vh)
        
        # setup the genetic vectors
        self.load_vg(initial_vg)

        # compile away our sympy expressions - for speed, the matrix, and its derivatives in all genetic symbols
        self.A = dumb_lambdify_matrix(self.s+self.g+self.hypermodel,input_matrix.tolist())
        self.dA = [dumb_lambdify_matrix(self.s+self.g+self.hypermodel,diff(input_matrix,gg).tolist()) for gg in self.g_symbols]

        # calculate the augmented matrix for gamma reasoning
        s_symbols_vector = Matrix(self.s_symbols)
        self.dV = eye(self.N)*self.lambda_symbol
        self.dV -= input_matrix
        for i,ss in enumerate(self.s_symbols):
            self.dV[:,i] -= diff(input_matrix,ss)*s_symbols_vector
        self.dV = self.dV.row_join(s_symbols_vector)
        self.dV = self.dV.col_join(Matrix([[1 for i in range(self.N)] + [0]]))
        self.dV = dumb_lambdify_matrix(self.s+self.g+self.hypermodel+[str(self.lambda_symbol)],self.dV.tolist())
        # calculate derivates, with appended zero row
        self.dAv = [dumb_lambdify_matrix(self.s+self.g+self.hypermodel+[str(self.lambda_symbol)],
            (diff(input_matrix,gg).col_join(Matrix([[0 for i in range(self.N)]]))).tolist()
            ) for gg in self.g_symbols]
#        self.dAv = dumb_lambdify_matrix(self.s+self.g+self.hypermodel+[str(self.lambda_symbol)],
#        [(diff(input_matrix,gg).col_join(Matrix([[0 for i in range(self.N)]]))).tolist() for gg in self.g_symbols])
        
        self.vnorm = None
        self.wnorm = None


    def run_inner(self,
    substitions,
    max_inner_iterations=200,
    inner_incorporation_factor=0.5,
    inner_iteration_target=1e-5,
    **extra_arguments
    ):
        # reduce the data to genetic data array
        A_x = partial(self.A,**substitions)
        old_old_v = self.v.copy()
        self.vnorm = None
        self.wnorm = None
        i = 0
        inner_t = time.time()
        inner_difference = float('inf')
        # do iterations to find a stable point
        while ((i<max_inner_iterations) and 
        (inner_difference>inner_incorporation_factor*inner_iteration_target)):
            i += 1
            old_v = self.v.copy()
            A_xx = A_x(**self.get_dict())
            if (A_xx<0).any():
                logging.warning("negative matrix encountered")
                A_xx = A_xx.clip(0)
            # power iteration to find right maximal eigenvector
            self.v[:,:] = ((1.0-inner_incorporation_factor)*self.v + 
                inner_incorporation_factor*A_xx*self.v)
            self.vnorm = self.v.sum()
            self.v[:,:] = self.v / self.vnorm
            inner_difference = norm(self.v - old_v)

            old_w = self.w.copy()
            A_xxt = A_xx.transpose()
            # power iteration to find left maximal eigenvector
            self.w[:,:] = ((1.0-inner_incorporation_factor)*self.w + 
                inner_incorporation_factor*A_xxt*self.w)
            self.wnorm = self.w.sum()
            self.w[:,:] = self.w / self.wnorm
            inner_difference = max(inner_difference,norm(self.w - old_w))
            
        if i==max_inner_iterations:
            logging.warning("Reached max inner iterations")
            raise ConvergenceException("inner loop iteration limit reached")
        ret = [i,time.time()-inner_t, norm(self.v-old_old_v)]
        logging.info("inner took: {0} iters, {1:.4g}s, delta={2:.4g}".format(*ret))
        return ret


    def outer_run(self, 
        outer_incorporation_factor, 
        max_delta_magnitude=1.0,
        inner_delta_multiplier=10.0,
        randomising_step=True,
        **inner_arguments
    ):
        arguments = self.get_g_dict()
        arguments.update(self.get_h_dict())
        self.run_inner(arguments,**inner_arguments)

        # calculate the vector of perturbations in the eigenvalue for static superpopulation
        delta_lambda = []
        arguments.update(self.get_dict())
        for i in range(len(self.g_symbols)):
            delta_lambda.append([(self.w.transpose()*(self.dA[i](**arguments)*self.v))[0,0]])
        delta_lambda = matrix(delta_lambda)
        logging.info("dLambda = {}".format(norm(delta_lambda)))

        import pdb
        pdb.set_trace()

        # calculate the vector of purturbations in the eigenvalue for non-static superpopulation
        arguments.update({str(self.lambda_symbol):self.vnorm})
        dAv = hstack([self.dAv[i](**arguments)*self.v for i in range(len(self.g_symbols))])
        v = lstsq(self.dV(**arguments),dAv,rcond=None)
        if v[2]!=self.N+1:
            logging.warning("matrix dAv has not got full rank.")
            
#        delta_gamma = [v[0][-1,:].transpose()


        
        productive_step_size = norm((self.vg+delta_lambda).clip(0,1) - self.vg)
#        with open("vector_debug.txt","a") as f:
#            Z = (self.vg+delta_lambda).clip(0,1) - self.vg
#            ZZ = Z.transpose().tolist()[0]
#            ZZ = ["#" if z>0 else "." if z<0 else " " for z in ZZ]
#            f.write("".join(ZZ))
#            f.write(" {}\n".format(productive_step_size))
        if randomising_step:
            delta_lambda = multiply(matrix(randint(2,size=delta_lambda.size)).transpose(),delta_lambda) # add some randomisation
        if inner_delta_multiplier==float("inf"):
            if norm(delta_lambda)!=0:
                delta_lambda = max_delta_magnitude * delta_lambda / norm(delta_lambda)
        else:
            delta_lambda = max_delta_magnitude * inner_delta_multiplier * delta_lambda / (1.0+inner_delta_multiplier*norm(delta_lambda))
        delta_lambda *= outer_incorporation_factor
        old_vg = self.vg.copy()
        self.vg[:,:] = box_accent(self.vg,delta_lambda)
        return productive_step_size,norm(self.vg-old_vg)



    def run(self, 
    max_outer_iterations=200,
    outer_incorporation_factor=0.01,
    outer_iteration_target=1e-3,
    v_hypermodel = None,
    **inner_arguments
    ):
        if v_hypermodel is not None:
            self.load_vh(v_hypermodel)
            
        # begin primary loop
        logging.info("Beginning simulation loop")
        j = 0
        outer_difference = float('inf')
        while ((j<max_outer_iterations) and 
        (outer_difference>outer_incorporation_factor*outer_iteration_target)):
            j += 1
#            if j==700:
#                import pdb
#                pdb.set_trace()
            logging.info("beginning {} loop".format(j))
            outer_difference,_ = self.outer_run(outer_incorporation_factor,**inner_arguments)
            logging.info("diff_Lambda = {}".format(outer_difference))
        if j==max_outer_iterations:
            logging.warning("Reached max outer iterations, simulation failed to converge")
            raise ConvergenceException("outer loop iteration limit reached")
            return False
        return True

    def debug_matrix(self,filename, labels):
        arguments = self.get_g_dict()
        arguments.update(self.get_h_dict())
        self.run_inner(arguments)
        arguments.update(self.get_dict())
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
            ff.write(json.dumps(self.get_g_dict(),indent=4))
            ff.write(json.dumps(self.get_h_dict(),indent=4))

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
