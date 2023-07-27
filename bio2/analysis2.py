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
    pixel_data = defaultdict(list)
    for s1 in result_keys:
        v = 0
        for k in outcome_keys:
            if k[:len(s1)]==s1:
            #if k[len(s1):]==s1:
                #s2 = k[len(s1):]
                v += r['vector'][s1]*outcomes[i][k]
        pixel_data[s1[0]].append(v)
    for k in pixel_data.keys():
        v = sum(pixel_data[k])/len(pixel_data[k])
        image_data[k].append((r['PN'],r['advantage_hetero'],v,r['stability']))

xs = sorted(list(set(a[0] for a in image_data['S'])))
ys = sorted(list(set(a[1] for a in image_data['S'])))

xs_dict = {b:a for a,b in enumerate(xs)}
ys_dict = {b:a for a,b in enumerate(ys)}

s_func = lambda x: min(max(np.power(pixel[2],1.0/2)*200,0),255)
im = np.ndarray((len(xs),len(ys)),dtype="uint8")
for pixel in image_data['Y']:
    if abs(pixel[3])>1e-5:
        im[xs_dict[pixel[0]],ys_dict[pixel[1]]] = 0.0
    else:
        im[xs_dict[pixel[0]],ys_dict[pixel[1]]] = s_func(pixel[2])
cv2.imwrite("output_Y.png", im)


d = []
for pixel in image_data['Y']:
    x_coord = xs_dict[pixel[0]]
    y_coord = ys_dict[pixel[1]]
    if x_coord%2==0 and y_coord%2==0:
        if abs(pixel[3])>1e-5:
            d.append((x_coord,y_coord,0.0))
        else:
            d.append((x_coord,y_coord,pixel[2]))
d = sorted(d)
with open("output_Y.dat",'w') as f:
    for i,dd in enumerate(d):
        if i>0 and d[i-1][0]!=dd[0]:
            f.write("\n")
        f.write("{}\t{}\t{}\n".format(*dd))

