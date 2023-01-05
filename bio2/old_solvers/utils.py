
import numpy as np
from numpy.linalg import norm


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
        
v = np.matrix([0.5,0.5,0.5])
diff = np.matrix([0.6,0.01,0.0001])

#import pdb
#pdb.set_trace()
print(box_accent(v,diff))
