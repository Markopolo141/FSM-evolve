import json
from termcolor import colored, cprint
from random import choice


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
result_keys = list(choice(choice(list(results.values())))['vector'].keys())

for j in range(len(result_keys[0])):
    for k in result_keys:
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

results = sorted(r_results, key = lambda x : (x["advantage_hetero"],x["PN"]))
for r in results:
    i = r["index"]
    for s1 in result_keys:
        v = 0
        for k in outcome_keys:
            if k[:len(s1)]==s1:
                #s2 = k[len(s1):]
                v += r['vector'][s1]*outcomes[i][k]
        cprint(ret_char(v*200), "red" if s1[3]=='M' else "blue", end=" ")

    print(" ",end="")
    for k in r.keys():
        if k!="vector" and k!="stability":
            print("{}{:.2f};".format(k,r[k]),end="")
    print("")
