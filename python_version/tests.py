import unittest

from utils import *
from sympy import *
from sympy.core.numbers import *
from pymatrix import *
import random
import time

import pdb

def list_almost_equal(A,B):
    if len(A) != len(B):
        return False
    for i in range(len(A)):
        if round(A[i],7) != round(B[i],7):
            return False
    return True
    
def matrix_almost_equal(A,B):
    if A.ncols != B.ncols or A.nrows != B.nrows:
        return False
    for ia,a in enumerate(A):
        for ib,b in enumerate(B):
            if ia==ib and round(a,7)!=round(b,7):
                return False
    return True

class TestUtils(unittest.TestCase):
    def testSuperRange(self):
        self.assertEqual([a for a in super_range(0.0, 1.0, 0.5)], [0.0, 0.5, 1.0])
        self.assertEqual([a for a in super_range(0.0, 1.5, 0.5)], [0.0, 0.5, 1.0, 1.5])
        self.assertEqual([a for a in super_range(0.1, 1.0, 0.5)], [0.1, 0.6])
        self.assertEqual([a for a in super_range(0, 1, 0.5)], [0.0, 0.5, 1.0])
        self.assertEqual([a for a in super_range(1, 1, 0.5)], [1.0])
        self.assertEqual([a for a in super_range(1, 0, 0.5)], [])
    def testAbsSum(self):
        A = [-1,1,1,-1,55]
        self.assertEqual(abs_sum(A), 59)
        A = matrix([[1]]*5)
        self.assertEqual(abs_sum(A), 5)
        self.assertEqual(abs_sum([]), 0)
    def testDelta(self):
        A = [-3,-2,-1,-0.2,0,0.1,1,2,3]
        B = [ 0, 0, 0, 0  ,1,  0,0,0,0]
        for i in range(len(A)):
            self.assertEqual(delta(A[i]), B[i])
    def testProtectedDivision(self):
        b = 'b'
        A = [1,2,3,1,4,5,3,0,1]
        A = A + [-a for a in A]
        B = [0,1,-1]*6
        C = [b,2,-3,b,4,-5,b,0,-1] + [b,-2,3,b,-4,5,b,0,1]
        for i in range(len(A)):
            self.assertEqual(protected_division(A[i],B[i], b),C[i])
    def testDisplace(self):
        A = [1,2,3,4]
        A = A + [-a for a in A]
        B = [4,3,2]
        B = B + [-b for b in B] + B
        C = [float(i)/10.0 for i in range(10)]
        D = [1.0, 2.1, 2.8, 1.6, -1.8, -2.0, 1.2, 0.9]
        for i in range(len(A)):
            self.assertAlmostEqual(displace(A[i], B[i], C[i]), D[i])
        A = matrix([[1]]*5)
        B = matrix([[2]]*5)
        C = matrix([[1.2]]*5)
        self.assertEqual(displace(A,B,0.2), C)
    def testManhattanDistance(self):
        A = [range(5), [-a for a in range(5)]]
        B = [[1+a for a in A[0]], [-(3+a) for a in A[1]]]
        aa = [matrix([a]).trp() for a in A]
        bb = [matrix([b]).trp() for b in B]
        C = [5, 13]
        for i in range(len(A)):
            self.assertEqual(manhattan_distance(A[i], B[i], lambda x,y:[x[i]-y[i] for i in range(min(len(x), len(y)))]), C[i])
            self.assertEqual(manhattan_distance(aa[i], bb[i]), C[i])
    def testManhattanNormalize(self):
        A = [range(5), [-a for a in range(5)]]
        B = [[1+a for a in A[0]], [-(3+a) for a in A[1]]]
        A = A + B
        C = [[0, 0.1, 0.2, 0.3, 0.4], [0, 0.1, 0.2, 0.3, 0.4], [1.0/15, 2.0/15, 3.0/15, 4.0/15, 5.0/15], [0.6, 0.4, 0.2, -0.0, -0.2]]
        for i in range(len(A)):
            self.assertEqual(list_almost_equal(manhattan_normalize(A[i], lambda x,y:[x*a for a in y]), C[i]), True)
            self.assertEqual(matrix_almost_equal(manhattan_normalize(matrix([A[i]]).trp()), matrix([C[i]]).trp()), True)
    def testGenerateEvenVector(self):
        for i in range(3,7):
            v = generate_even_vector(i)
            for a in v:
                self.assertEqual(a, 1.0/i)
    def testGenerateConstantVector(self):
        for i in range(3,7):
            for o in range(3,7):
                v = generate_constant_vector(i,o)
                for z in v:
                    self.assertEqual(z,o)
    def testMatrixSize(self):
        for r in range(2,5):
            for c in range(2,5):
                A = Matrix(r,c)
                self.assertEqual(matrix_size(A), (r,c))
    def testMatrixLen(self):
        for r in range(2,5):
            for c in range(2,5):
                A = Matrix(r,c)
                self.assertEqual(matrix_len(A), r*c)
    def testElvis(self):
        f = lambda x:x
        a = 'ben'
        A = [None,"", "1", f, 3, 2.3, 0]
        B = [a,"","1",f,3,2.3,0]
        for i in range(len(A)):
            self.assertEqual(elvis(A[i], f, a), B[i])
    def testGetMaxIndex(self):
        A = [[0,1,2,3,4,3,2,1,0],
             [4,3,45,76,2,34,2],
             [],
             [99,float("inf"), float("-inf"),0]]
        B = [4,3,None,1]
        for i in range(len(A)):
            self.assertEqual(get_max_index(A[i]), B[i])
    def testGetMaxOf(self):
        A = [[0,1,2,3,4,3,2,1,0],
             [4,3,45,76,2,34,2],
             [],
             [99,float("inf"), float("-inf"),0]]
        B = [4,76,None,float("inf")]
        for i in range(len(A)):
            self.assertEqual(get_max_of(A[i]), B[i])
    def testIsErgodic(self):
        m = matrix([[1,2],[2,3]])
        self.assertEqual(is_ergodic(m), True)
        m = matrix([[1],[2]])
        self.assertEqual(is_ergodic(m), False)
        m = matrix([[1,0],[0,0]])
        self.assertEqual(is_ergodic(m), False)
        m = matrix([[1,0,0],[0,1,1],[0,1,1]])
        self.assertEqual(is_ergodic(m), False)
        m = matrix([[0,1,0],[0,0,1],[1,0,0]])
        self.assertEqual(is_ergodic(m), True)
        m = matrix([[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0]])
        self.assertEqual(is_ergodic(m), True)
        x = symbols('x')
        m = matrix([[x+1,x-x],[x,x*x]])
        self.assertEqual(is_ergodic(m), False)
        m = matrix([[0,x,0,0],[0,0,x,x],[x,0,0,1],[1,0,0,0]])
        self.assertEqual(is_ergodic(m), True)
        m = matrix([[x*x,x-x],[0,0]])
        self.assertEqual(is_ergodic(m), False)
    def testEveryElementIsIn(self):
        m = [1,2,3,4,1,2,3,4,"hello"]
        self.assertEqual(every_element_is_in(m, [1,2,3,4,"hello"]), True)
        self.assertEqual(every_element_is_in(m, [1,4,3,"hello",2,6,7,89]), True)
        self.assertEqual(every_element_is_in(m, [1,2]), False)
        self.assertEqual(every_element_is_in(m, ["1234hello"]), False)
        m = matrix([[1,2,3],[2,3,1],[3,1,2]])
        self.assertEqual(every_element_is_in(m, [1,2,3]), True)
        self.assertEqual(every_element_is_in(m, [1,4,3,"hello",2,6,7,89]), True)
        self.assertEqual(every_element_is_in(m, [1,2]), False)
        self.assertEqual(every_element_is_in(m, ["1234hello"]), False)
    def testIsExpressionWith(self):
        x,y,z = symbols('x y z')
        self.assertEqual(is_expression_with(x+y*y+22, [x,y]), True)
        self.assertEqual(is_expression_with(x+y, [x,y,z]), True)
        self.assertEqual(is_expression_with((x*x+y)*2, [y,z]), False)
    def testMatrixIsExpressionsWith(self):
        x,y,z = symbols('x y z')
        m = matrix([[x*x,y+1],[One(),z-z]])
        self.assertEqual(matrix_is_expressions_with(m, [x,y]), True)
        self.assertEqual(matrix_is_expressions_with(m, [x,y,z]), True)
        self.assertEqual(matrix_is_expressions_with(m, [x]), False)
        self.assertEqual(matrix_is_expressions_with(m, [y,z]), False)
    def testExpressionPositiveSemiDefinite(self):
        x,y,z = symbols('x y z')
        self.assertEqual(check_expression_positive_semi_definite(x), True)
        self.assertEqual(check_expression_positive_semi_definite(x+y), True)
        self.assertEqual(check_expression_positive_semi_definite(x+y-z), False)
        self.assertEqual(check_expression_positive_semi_definite(x-x), True)
        self.assertEqual(check_expression_positive_semi_definite(x-0.5), False)
        self.assertEqual(check_expression_positive_semi_definite(-y/(z-0.4)), False)
    def testCheckMatrixPositiveSemiDefinite(self):
        x,y,z = symbols('x y z')
        m = matrix([[x+y,x],[One(),z-z]])
        self.assertEqual(check_matrix_positive_semi_definite(m), True)
        m = matrix([[x-2*z,z],[z-z,y*55]])
        self.assertEqual(check_matrix_positive_semi_definite(m), False)
        m = matrix([[One(),One()],[Zero(),One()]])
        self.assertEqual(check_matrix_positive_semi_definite(m), True)
        m = matrix([[z,x*-1*x],[z,z]])
        self.assertEqual(check_matrix_positive_semi_definite(m), False)
        m = matrix([[z,x*x],[z/y,z]])
        self.assertEqual(check_matrix_positive_semi_definite(m), True)
        m = matrix([[z,x*x],[y,(z-0.5)*(y-0.5)]])
        self.assertEqual(check_matrix_positive_semi_definite(m), False)
        m = matrix([[z,x*x],[y/(z-0.4),z*y]])
        self.assertEqual(check_matrix_positive_semi_definite(m), False)
        m = matrix([[z,x*x],[-y/(z-0.4),z*y]])
        self.assertEqual(check_matrix_positive_semi_definite(m), False)
    def testVariableTranslate(self):
        def get_rand_seq():
            a = []
            for i in range(random.randint(3,6)):
                a = a + [random.random()]
            return a
        for i in range(7):
            a = get_rand_seq()
            b = variable_translate(a)
            self.assertEqual(len(b), len(a)+1)
            self.assertAlmostEqual(sum(b), 1.0)
            for i in range(len(a)):
                self.assertAlmostEqual(b[i+1]/(b[i]+b[i+1]),a[i])
        for i in range(7):
            a = matrix([get_rand_seq()]).trp()
            b = variable_translate(a)
            self.assertEqual(len(b), matrix_len(a)+1)
            self.assertAlmostEqual(sum(b), 1.0)
            for i in range(matrix_len(a)):
                self.assertAlmostEqual(b[i+1]/(b[i]+b[i+1]),a[i][0])
        self.assertAlmostEqual(variable_translate([0.5,0.5,0.5]), [0.25,0.25,0.25,0.25])
    def testDistributedVariableTranslate(self):
        def get_rand_seq():
            a = []
            for i in range(random.randint(3,6)):
                a = a + [random.randint(0,3)]
            return a
        def get_rand_rand_seq(l):
            a = []
            for i in range(l):
                a = a + [random.random()]
            return a
        for i in range(8):
            a = get_rand_seq()
            b = get_rand_rand_seq(sum(a))
            c = distributed_variable_translate(a,b)
            for z in c:
                if z is not None:
                    self.assertAlmostEqual(sum(z), 1.0)
            d = 0
            for z in c:
                if z is not None:
                    self.assertEqual(variable_translate(b[d:d+len(z)-1]), z)
                    d = d + len(z)-1
        self.assertEqual(distributed_variable_translate([0,1,2,3,1], [0.5]*7), [None,[0.5,0.5],[1.0/3,1.0/3,1.0/3],[0.25,0.25,0.25,0.25],[0.5,0.5]])
    def testGetDistribution(self):
        lower = 2
        upper = 5
        for i in range(5):
            r = random.randint(lower,upper)
            c = random.randint(lower,upper)
            m = Matrix(r,c)
            for z in range(random.randint(2,lower*upper)):
                m.grid[random.randint(0,r-1)][random.randint(0,c-1)] = 1
            d = [sum(a) for a in m.cols()]
            d = [a-1 if a > 1 else 0 for a in d]
            f = get_distribution(m)
            self.assertEqual(f,d)
        self.assertEqual(get_distribution(matrix([[1,0],[1,0],[0,1]])), [1,0])
    def testWeightChoice(self):
        s0,s1,s2,s3 = symbols('s0 s1 s2 s3')
        exprs = [s1+1, s2+1, s1+s2, s1*s2, s2*s3, s2-s2+2, s3-s1, s3+s2*s1, s1*s1+3, s3*s2]
        vals = [matrix([[1,2,3,4]]),matrix([[4,3,2,1]]),matrix([[11,22,33,44]])]
        for aa in range(5):
            t = time.time()
            r = random.randint(2,4)
            c = random.randint(2,4)
            random.seed(t)
            m = Matrix(r,c)
            for ri in range(r):
                for ci in range(c):
                    m.grid[ri][ci] = random.choice(exprs)
            for z in range(len(vals)):
                mm = weight_choice(m, vals[z])
                random.seed(t)
                for ri in range(r):
                    for ci in range(c):
                        self.assertEqual(mm[ri][ci], random.choice(exprs).evalf(subs=dict(zip([s0,s1,s2,s3], vals[z].grid[0]))))
        self.assertEqual(matrix_almost_equal(weight_choice(matrix([[s0+s1,s2+s3],[s2-s1,s3-s2]]), matrix([[1,2,3,4]])), matrix([[3,7],[1,1]])), True )
        self.assertEqual(matrix_almost_equal(weight_choice(matrix([[s0+s1,s2+s3],[s2-s1,s3-s2]]), matrix([[1,4,3,4]])), matrix([[3,7],[1,1]])), False )
        self.assertRaises(Exception, weight_choice, matrix([[s0+s1,s2+s3],[s2-s1,s3-s2]]), matrix([[1,4,3]]) )
        self.assertEqual(matrix_almost_equal(weight_choice(matrix([[s0+s1,s2+s3],[s2-s1,s3-s2]]), matrix([[1,4,3,4,5,6,7]])), matrix([[3,7],[1,1]])), False )
    def testWeightSwitch(self):
        for i in range(30):
            r = random.randint(2,5)
            c = random.randint(2,5)
            m = Matrix(r,c)
            for i in range(0, random.randint(2,5*5)):
                m.grid[random.randint(0,r-1)][random.randint(0,c-1)] = 1
            num_vars = sum(get_distribution(m))
            v = [0.5]*num_vars
            mm = weight_switch(m, v)
            for ci in range(mm.ncols):
                for rr in mm.col(ci):
                    self.assertEqual(rr==0 or rr==1.0/sum(m.col(ci)), True)
        self.assertEqual(weight_switch(matrix([[0, 0],[0, 0]]),[]), matrix([[0, 0],[0, 0]]))
        self.assertEqual(weight_switch(matrix([[0, 0],[0, 0]]),[1,2,3]), matrix([[0, 0],[0, 0]]))
        self.assertEqual(weight_switch(matrix([[1, 0],[0, 1]]),[]), matrix([[1, 0],[0, 1]]))
        self.assertRaises(Exception, weight_switch, matrix([[1, 0],[1, 1]]), [])
        self.assertEqual(matrix_almost_equal(weight_switch(matrix([[1, 0],[1, 1]]),[0.1]), matrix([[0.1, 0],[0.9, 1]])),True)

from DerivativeSimulations import SubPopulationGrowthSimulation

class TestSubPopulationGrowthSimulation(unittest.TestCase):
    def testSim1(self):
        s = SubPopulationGrowthSimulation(matrix([[1,0],[0,1]]), matrix([[0,1],[1,0]]))
        m = s.population
        s.iterate()
        t = s.getTrait()
        for i in range(15):
            self.assertEqual(matrix_almost_equal(s.population, m), True)
            self.assertEqual(matrix_almost_equal(s.getData(), m), True)
            self.assertEqual(s.getQuality(), 0.0)
            self.assertEqual(s.getTrait(), t)
            s.iterate()
        self.assertEqual(t, 1.0)
    def testSim2(self):
        s = SubPopulationGrowthSimulation(matrix([[0.5,0],[0,0.5]]), matrix([[0,1],[1,0]]))
        m = s.population
        s.iterate()
        t = s.getTrait()
        for i in range(15):
            self.assertEqual(matrix_almost_equal(s.population, m), True)
            self.assertEqual(matrix_almost_equal(s.getData(), m), True)
            self.assertEqual(s.getQuality(), 0.0)
            self.assertEqual(s.getTrait(), t)
            s.iterate()
        self.assertEqual(t, 0.75)
    def testSim3(self):
        s = SubPopulationGrowthSimulation(matrix([[0.5,0,0.5],[0.2,0,0.5],[0.5,0.4,0.3]]), matrix([[0,1,1],[1,0,1],[1,1,0]]))
        s.iterate()
        q = s.getQuality()
        t = s.getTrait()
        for i in range(35):
            #print "{} {}".format(s.getTrait(), s.getQuality())
            self.assertTrue(s.getQuality()<=q)
            q = s.getQuality()
            s.iterate()

from Base import Simulation

class dummySimulation(Simulation):
    a = None
    b = None
    index = None
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.index = 1
    def iterate(self):
        self.index = self.index + 1
    def getQuality(self):
        return float(self.a) / self.index
    def getTrait(self):
        return float(self.b) / self.index
    def getData(self):
        return self.index
        
class dummyCountSimulation(Simulation):
    a = None
    b = None
    index = None
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.index = 1
    def iterate(self):
        self.index = self.index + 1
    def getQuality(self):
        return self.c if self.index < self.a else 0
    def getTrait(self):
        return self.d if self.index < self.b else 0
    def getData(self):
        return self.index

class TestSimulate(unittest.TestCase):
    def testSimulate(self):
        params = [(50,20),(10,140),(40,20),(10,12),(2,340),(3,1239)]
        its = [5,13,5,4,19,36]
        its2 = [50,10,40,10,3,3]
        for i,p in enumerate(params):
            s = dummySimulation(*p)
            s.simulate(1000.0,1.0)
            self.assertEqual(s.index, its[i])
        for i,p in enumerate(params):
            s = dummySimulation(*p)
            s.simulate(1.0,10000.0)
            self.assertEqual(s.index, its2[i])

from Simulations import SimpleEnsembleSimulation

class TestSimpleEnsembleSimulation(unittest.TestCase):
    def testSimpleEnsembleSimulation(self):
        for z in range(random.randint(10,35)):
            aes = []
            bes = []
            des = []
            for i in range(random.randint(5,15)):
                aes.append(random.randint(20,50))
                bes.append(random.randint(20,50))
                des.append(random.random()*10.0)
            total_sims = [dummyCountSimulation(aes[i],bes[i],10.0,des[i]) for i in range(len(aes))]
            sims = SimpleEnsembleSimulation(total_sims)
            sims.simulate(1.0)
            for i in range(max(max(aes),max(bes))):
                indexo = get_max_index([des[o] if i < bes[o] else 0.0 for o in range(len(aes))])
                if i>= aes[indexo]:
                    self.assertEqual(sims.sims[0].index, i)
                    break

from Simulations import GreatestAscentSimulation

class TestGreatestAscentSimulation(unittest.TestCase):
    def testGreatestAscentSimulation(self):
        sim = GreatestAscentSimulation(
            0.0,
            lambda x: [x-1,x+1],
            lambda a,b,c,d: None,
            lambda x,y: [-(5-a)**2 for a in x],
            lambda x:x,
            lambda x,y: y,
            lambda x,y: abs(x-y)
        )
        sim.simulate(0.0)
        self.assertEqual(sim.new, 5.0)
    def testGreatestAscentSimulatable(self):
        sim = GreatestAscentSimulation(
            0.0,
            lambda x: [x-1,x+1],
            lambda a,b,c,d: None,
            lambda x,y: [-(5-a)**2 for a in x],
            lambda x:x,
            lambda x,y: 0.5*x+0.5*y,
            lambda x,y: abs(x-y)
        )
        sim.simulate(0.0)
        self.assertEqual(sim.new, 4.5)   #not deliberate and known badness...

from Simulations import ReductionSimulation

class TestReductionSimulation(unittest.TestCase):
    def testReductionSimulation(self):
        sim = GreatestAscentSimulation(
            0.0,
            lambda x: [x-1,x+1],
            lambda a,b,c,d: None,
            lambda x,y: [-(5-a)**2 for a in x],
            lambda x:x,
            lambda x,y: 0.5*x+0.5*y,
            lambda x,y: abs(x-y)
        )
        def alter_func(sim,r):
            sim.generator = (lambda x: [x-r,x+r])
        red_sim = ReductionSimulation(
            sim,
            alter_func,
            5,
            0.1,
            {"target_quality":0.001}
        )
        #pdb.set_trace()
        red_sim.simulate(0.0001, repeated=0)
        print red_sim.simulation.new

unittest.main()
