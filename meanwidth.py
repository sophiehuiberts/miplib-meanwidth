#!/usr/bin/python
# coding: utf-8
import os
import os.path
import gurobipy
import numpy as np
import math
import sys
from tqdm import tqdm
from statistics import mean, median
import json

def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

np.random.seed(0)
samples_per_model = 500
time_limit_per_sample = 60

env = gurobipy.Env()
env.setParam('OutputFlag',False)

print(f"    Model Name               | Minimum |   Median  |   Mean   | Maximum")
print(f"----------------------------------------------------------------------------")
for file in os.scandir('/home/sophie/miplibbenchmark'):
    model = gurobipy.read(os.fsdecode(file),env=env)
    if os.path.isfile(f"output/{model.ModelName}-meanwidthlog.txt"):
        print(f"output/{model.ModelName}-meanwidthlog.txt already exists")
        sys.stdout.flush()
        continue

    relax = model.relax()
    relax.Params.Crossover = 0
    relax.Params.DualReductions = 0
    relax.setParam('TimeLimit',time_limit_per_sample)

    results = []
    for attempts in tqdm(range(0,samples_per_model)):
        sqnorm = 0
        varcount = 0
        for var in relax.getVars():
            varcount = varcount + 1
            sample = np.random.normal(0,1)
            var.setAttr('Obj', sample)
            sqnorm = sqnorm + sample*sample
        relax.optimize()
        if relax.getAttr('Status') == gurobipy.GRB.OPTIMAL:
            results.append(-1 * relax.ObjVal / math.sqrt(sqnorm))
        else:
            print(f"{model.Modelname:<28} | Status code {relax.getAttr('Status')} on attempt {attempts}")
            sys.stdout.flush()
            break
    with open(f"output/{model.ModelName}-meanwidthlog.txt",'w',encoding="utf-8") as outputfile:
        if len(results) == samples_per_model:
            json.dump(results, outputfile)
            print(f"{model.Modelname:<28} | {min(results):>8.2} | {median(results):>8.2} | {mean(results):>8.2} | {max(results):>8.2}")
            sys.stdout.flush()
        else:
            outputfile.write(f"Status code {relax.getAttr('Status')} on attempt {attempts}")
