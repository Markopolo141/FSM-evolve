import json

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
    for k in outcome_keys:
        if outcomes[i][k]==1.0:
            print("X",end=" ")
        else:
            print(" ",end=" ")
        #print(outcomes[i][k],end="\t")
    for r in results[str(i)]:
        for k in r.keys():
            if k!="vector" and k!="stability":
                print("{}{};".format(k,r[k]),end="")
        print(" ",end="")
    print("")
