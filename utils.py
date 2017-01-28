def generate_switch_extrema(switch):
    dist = [sum([a[i] for a in switch.grid]) for i in range(len(switch.grid[0]))]
    switches = []
    def iterate(i,indices):
        if i < len(dist):
            for o in range(dist[i]):
                iterate(i+1,indices+[o])
        else:
            new_switch = switch.copy()
            for c in range(switch.ncols):
                for r in range(switch.nrows):
                    if new_switch[r][c]==1:
                        if indices[c] != 0:
                            new_switch[r][c]=0
                        indices[c] -= 1
            switches.append(new_switch)
    iterate(0,[])
    return switches

def addTo(e,l):
    for z in l:
        if e==z:
            return z
    l.append(e)
    return e

def normalise(A,B,s=None):
    if s is None:
        s = sum(B)
    if s > 0:
        for i in range(len(A)):
            A[i].__wrapped__ = B[i]/s
    else:
        for i in range(len(A)):
            A[i].__wrapped__ = 0
    return s

def equate(A,B):
    for i in range(len(A)):
        A[i].__wrapped__ = B[i]

def accumu(lis):
    total = 0
    for x in lis:
        yield total
        total += x

def deviation(l):
    min_v = -float("inf")
    max_v = float("inf")
    for a in l:
        if a > min_v:
            min_v = a
        if a < max_v:
            max_v = a
    return max_v-min_v

'''
given a list defining ranges of iterables in form 
[["count1":{"min":0,"max":5,"step":1}],...} return a list of dicts of all combinations of thoes values (together with the index of their iterations)
note: "step" is optional on each
'''
def multi_iterate(d):
    l = []
    def sub_method(vals,indices,i):
        if i<len(d):
            count = d[i][1]["min"]
            index = 0
            while count < d[i][1]["max"]:
                sub_method(vals + [count],indices + [index],i+1)
                count = d[i][1]["min"]+index*d[i][1].get("step",1)
                index += 1
        else:
            l.append({d[o][0]:(vals[o],indices[o]) for o in range(i)})
    sub_method([],[],0)
    return l
