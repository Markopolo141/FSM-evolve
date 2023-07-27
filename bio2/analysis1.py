import json
from termcolor import colored, cprint
from random import choice
import cv2
from collections import defaultdict
import numpy as np


with open("Experiment_results1.json",'r') as f:
    data = json.load(f)
outcomes = data['outcomes']
results = data['results']
outcome_keys = sorted(outcomes[0].keys()) #YAAMYAAF etc
result_keys = list(choice(choice(list(results.values())))['vector'].keys()) #YAAM etc

# append the index to the records, and create r_records all together
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

image_data = defaultdict(list)
for r in results:
    i = r["index"]
    for s1 in result_keys:
        v = 0
        for k in outcome_keys:
            if k[:len(s1)]==s1:
            #if k[len(s1):]==s1:
                #s2 = k[len(s1):]
                v += r['vector'][s1]*outcomes[i][k]
        image_data[s1].append((r['PN'],r['advantage_hetero'],v))

xs = sorted(list(set(a[0] for a in image_data[result_keys[0]])))
ys = sorted(list(set(a[1] for a in image_data[result_keys[0]])))

xs_dict = {b:a for a,b in enumerate(xs)}
ys_dict = {b:a for a,b in enumerate(ys)}

s_func = lambda x: min(max(np.power(pixel[2],1.0/4)*200,0),255)

for s in result_keys:
    im = np.ndarray((len(xs),len(ys)),dtype="uint8")
    for pixel in image_data[s]:
        im[xs_dict[pixel[0]],ys_dict[pixel[1]]] = s_func(pixel[2])
    cv2.imwrite("output_{}.png".format(s), im)
