#!/usr/bin/python
# coding: utf-8
import os
import gurobipy
import numpy as np
import math
import sys
from statistics import mean, median

def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

np.random.seed(0)
samples_per_model = 50
time_limit_per_sample = 10*60

env = gurobipy.Env()
env.setParam('OutputFlag',False)

alloutput = ['lmao']

print(f"    Model Name               | Minimum |   Median  |   Mean   | Maximum")
print(f"----------------------------------------------------------------------------")
for file in os.scandir('/home/sophie/miplibbenchmark'):
    model = gurobipy.read(os.fsdecode(file),env=env)

    sys.stdout.flush()

    relax = model.relax()
    relax.Params.Crossover = 0
    relax.setParam('TimeLimit',time_limit_per_sample)

    sys.stdout.flush()

    results = []
    for attempts in range(0,samples_per_model):
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
            errprint(f"{model.Modelname:<28} | Status code {relax.getAttr('Status')}")
            break
    if len(results) == samples_per_model:
        print(f"{model.Modelname:<28} | {min(results):>8.2} | {median(results):>8.2} | {mean(results):>8.2} | {max(results):>8.2}")
        alloutput.append([model.Modelname,results])
    sys.stdout.flush()
    sys.stderr.flush()
print('done. now printing all results so far')
print(alloutput)
