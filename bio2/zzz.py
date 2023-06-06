import json

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
for i in range(len(outcomes)):
    for r in results[str(i)]:
        for k in outcome_keys:
            for s1 in r['vector'].keys():
                for s2 in r['vector'].keys():
                    if s1+s2 == k:
#                        print("X", end="")
                        print(ret_char(r['vector'][s1]*outcomes[i][k]*400), end=" ")
            '''if outcomes[i][k]==1.0:
                print("X",end=" ")
            else:
                print(" ",end=" ")'''
            #print(outcomes[i][k],end="\t")

        print(" ",end="")
        for k in r.keys():
            if k!="vector" and k!="stability":
                print("{}{};".format(k,r[k]),end="")
        print("")
