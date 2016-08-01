import os
import json

def super_range(start, end, step):
    a = start
    while a <= end:
        yield a
        a = a + step

Bb_range = list(super_range(-0.05, 0.451, 0.05))
Nb_range = list(super_range(1.0, 2.01, 0.1))
import pdb

try:
    for Bbi, Bb in enumerate(Bb_range):
        for Nbi, Nb in enumerate(Nb_range):
            #pdb.set_trace()
            print "complete: {}".format((1.0*Bbi)/len(Bb_range) + (1.0*Nbi)/(len(Nb_range)*len(Bb_range)))
            j = {"sets":[{"{Bb}":str(Bb),"{Nb}":str(Nb)}]}
            filename = 'data-base-{}-{}.json'.format(Bb,Nb)
            template_filename = 'data-template-{}-{}.json'.format(Bb,Nb)
            data_filename = 'data-{}-{}.json'.format(Bb,Nb)
            with open("./configs/gen_files/{}".format(filename), 'w') as outfile:
                json.dump(j, outfile)
            os.system("python ./configs/replacer.py ./configs/gen_files/{} ./configs/formulas.json ./configs/gen_files/{}".format(filename, template_filename))
            os.system("python ./configs/replacer.py ./configs/gen_files/{} ./configs/template.json ./configs/gen_files/{}".format(template_filename, data_filename))
            os.system("python Sim.py ./configs/gen_files/{}".format(data_filename))
except:
    pass
#os.system("shutdown -h now")
