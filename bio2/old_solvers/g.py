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

# for a symbolic expression string <element>, consisting of <symbols>
# variables, compile the expression as a executable lambda,
# in global namespace 
def dumb_lambdify(symbols,element):
    s = "lambda {} : {}".format(",".join(symbols),repr(element))
    return eval(s, globals())


default_parameters = {
"inner_incorporation_factor":0.5,
"outer_incorporation_factor":0.01,
"max_inner_iterations":200,
"inner_iteration_target":1e-5,
"max_outer_iterations":200,
"outer_iteration_target":1e-3
}

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
    logging.debug("loaded_parameters:")
    for k,default in default_parameters.items():
        config[k] = config.get(k,default)
        logging.debug("\t{}:\t{}".format(k,config[k]))

    # extract the dimensions of the matrix
    assert isinstance(data, list), 'matrix must be specified as array of arrays'
    N = len(data)
    assert False not in [len(d)==N for d in data], 'matrix must be square'
    logging.debug("Matrix size: {}".format(N))

    # setup the initial vectors
    v = matrix([[0.5] for i in range(N)])
    s = ["x{}".format(i) for i in range(N)]
    s_symbols = [symbols(x) for x in s]
    def get_dict():
        return {s[i]:float(v[i]) for i in range(N)}

    # load data as symbolic matrix, and extract genetic symbols
    g_symbols = set()
    data = [[parse_expr(ddd) for ddd in dd] for dd in data]
    for dd in data:
        for ddd in dd:
            for sym in ddd.free_symbols:
                if sym not in s_symbols:
                    g_symbols.add(sym)
    data = Matrix(data)
    logging.debug("detecting genetic symbols: {}".format(g_symbols))
    
    # setup the genetic vectors
    G = len(g_symbols)
    g_symbols = [a[0] for a in sorted([(s,str(s)) for s in list(g_symbols)], key = lambda x:x[1])]
    if "initial_vg" in config.keys():
        assert len(config['initial_vg'].values())==G
        vg = matrix([[config['initial_vg'][str(g_symbols[i])]] for i in range(G)])
    else:
        vg = matrix([[0.5] for i in range(G)]) #TODO: 0.5
    g = [str(gg) for gg in g_symbols]
    def get_g_dict():
        return {g[i]:float(vg[i]) for i in range(G)}

    # compile away our sympy expressions - for speed
    A = dumb_lambdify(s+g,matrix(data.tolist()))
    dA = [dumb_lambdify(s+g,matrix(diff(data,g[gg]).tolist())) for gg in range(G)]

    # begin primary loop
    logging.info("Beginning simulation loop")
    j = 0
    outer_difference = float('inf')
    try:
        while ((j<config['max_outer_iterations']) and 
        (outer_difference>config['outer_incorporation_factor']*config['outer_iteration_target'])):
            j += 1
            # reduce the data to genetic data array
            A_x = partial(A,**get_g_dict())

            # do iterations to find a stable point
            old_old_v = v.copy()
            vnorm = None
            i = 0
            inner_t = time.time()
            inner_difference = float('inf')
            while ((i<config['max_inner_iterations']) and 
            (inner_difference>config['inner_incorporation_factor']*config['inner_iteration_target'])):
                i += 1
                old_v = v.copy()
                A_xx = A_x(**get_dict())
                if (A_xx<0).any():
                    logging.warning("negative matrix encountered")
                    A_xx.clip(0)
                v[:,:] = ((1.0-config['inner_incorporation_factor'])*v + 
                    config['inner_incorporation_factor']*A_xx*v)
                vnorm = v.sum()
                v[:,:] = v / vnorm
                inner_difference = norm(v - old_v)
            if i==config['max_inner_iterations']:
                logging.warning("Reached max inner iterations")
            logging.info("{0} took: {1} iters, {2:.4g}s, delta={3:.4g}".format(j,i,time.time()-inner_t, norm(v-old_old_v)))

            '''
            if 'labels' in config.keys():
                #for i in range(N):
                #    print("{} = {}".format(config['labels'][i],float(v[i])))
                with open("debug_output.txt","w") as ff:
                    for a in A_xx.tolist():
                        for b in a:
                            z = round(float(b*100))
                            if z!=0:
                                ff.write("{:03d} ".format(round(float(b*100))) )
                            else:
                                ff.write("    ")
                        ff.write("\n")
                    ff.write("\n")
                    for i in range(N):
                        ff.write("{} = {}\n".format(config['labels'][i],float(v[i])))
                
            import pdb
            pdb.set_trace()'''

            # calculate the vector of perturbations in eigenvalue
            delta_lambda = []
            arguments = get_dict()
            arguments.update(get_g_dict())
            for gg in range(G):
                delta_lambda.append([(v.transpose()*(dA[gg](**arguments)*v))[0,0]])
            delta_lambda = matrix(delta_lambda)
            #logging.info("dLambda = {}".format(norm(delta_lambda)))
            delta_lambda = delta_lambda / (0.001+norm(delta_lambda))

            old_vg = vg.copy()
            vg[:,:] = (vg + config['outer_incorporation_factor']*delta_lambda).clip(0,1)
            outer_difference = norm(vg-old_vg)
            logging.info("diff_Lambda = {}".format(outer_difference))
        if j==config['max_outer_iterations']:
            logging.warning("Reached max outer iterations, simulation failed to converge")
    except KeyboardInterrupt as e:
        print(e)
    print("Lambda = {}".format(vnorm))
    print(v)
    for i in range(len(v)):
        print("{}:\t{}".format(s_symbols[i],v[i,0]))
    for i in range(len(vg)):
        print("{}:\t{}".format(g_symbols[i],vg[i,0]))
        


if __name__ == '__main__':
    run()
