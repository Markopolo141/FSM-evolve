from sympy import symbols
import xarray as xr

coords = {
"genetics" : ["++", "+-", "--"], # genetic states
"sex" : ["M","F"],
"age" : ["Y","O"],
"strategy" : ["Poly","Mono"]
}

from_coords = {"from_{}".format(a):b for a,b in coords.items()}
to_coords = {"to_{}".format(a):b for a,b in coords.items()}

frame = xr.DataArray(0.0,dims = sorted(from_coords.keys()) + sorted(to_coords.keys()), coords = [from_coords[k] for k in sorted(from_coords.keys())] + [to_coords[k] for k in sorted(to_coords.keys())])


# survival

frame = xr.where( (frame.from_age=="Y") & (frame.to_age=="O") & (frame.from_sex==frame.to_sex) & (frame.from_strategy==frame.to_strategy) & (frame.from_genetics==frame.to_genetics) , 1.0, frame)

import pdb
pdb.set_trace()


#the_market = sum(frame[np.logical_or(frame.age!="Y",frame.strategy!="Mono")].symbol)


# offspring

