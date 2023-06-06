import json
from termcolor import colored, cprint


chars = [' ','.',',',';','!','|','1','I','P','R','Q','N','W','#','@']

def ret_char(f):
    if f>1.0:
        f=0.999999
    if f<0:
        f=0
    return chars[int(f*len(chars))]

with open("experiment_results1.json",'r') as f:
    data = json.load(f)
outcomes = data['outcomes']
results = data['results']
outcome_keys = sorted(outcomes[0].keys())
for j in range(len(outcome_keys[0])):
    for k in outcome_keys:
        print(k[j],end=" ")
    print("")

r_results = []
for i,k in results.items():
    for j,kk in enumerate(k):
        for key in kk.keys():
            try:
                kk[key] = float(kk[key])
            except:
                pass
        kk["index"] = int(i)
        r_results.append(kk)
#results = sorted(r_results, key = lambda x : frozenset([a for a in x.values() if isinstance(a,int) or isinstance(a,float)]))
#results = sorted(r_results, key = lambda x : [x[a] for a in sorted(x.keys()) if isinstance(x[a],float)])
#results = sorted(r_results, key = lambda x : x["NN"])
#results = sorted(r_results, key = lambda x : (x["NN"], x["advantage_hetero"]))
results = sorted(r_results, key = lambda x : (x["advantage_hetero"],x["NN"]))
for r in results:
    i = r["index"]
    for k in outcome_keys:
        for s1 in r['vector'].keys():
            for s2 in r['vector'].keys():
                if s1+s2 == k:
#                        print("X", end="")
                    #print(ret_char(r['vector'][s1]*outcomes[i][k]*400), end=" ")
                    cprint(ret_char(r['vector'][s1]*outcomes[i][k]*200), "red" if k[3]=='M' else "blue", end=" ")
        '''if outcomes[i][k]==1.0:
            print("X",end=" ")
        else:
            print(" ",end=" ")'''
        #print(outcomes[i][k],end="\t")

    print(" ",end="")
    for k in r.keys():
        if k!="vector" and k!="stability":
            print("{}{:.2f};".format(k,r[k]),end="")
    print("")
