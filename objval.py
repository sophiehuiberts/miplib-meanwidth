#!/usr/bin/python
# coding: utf-8
import os
import gurobipy
import numpy as np
import math
import sys

env = gurobipy.Env()
env.setParam('OutputFlag',False)

time_limit_per_sample = 60*60 # at most one hour per relaxation

minimum = 10000000000
maximum = -10000000000
minimumnormalized = 10000000000
maximumnormalized = -10000000000

instances = 0
withvals = 0

print(f"    Model Name               |   Value  | Normalized |   Norm")
print(f"----------------------------------------------------------------------------")
for file in os.scandir('/home/sophie/miplibbenchmark'):
    instances = instances + 1
    model = gurobipy.read(os.fsdecode(file),env=env)

    sys.stdout.flush()

    relax = model.relax()
    relax.Params.Crossover = 0
    relax.setParam('TimeLimit',time_limit_per_sample)

    sys.stdout.flush()

    relax.optimize()
    sqnorm = 0
    for var in relax.getVars():
        sample = np.random.normal(0,1)
        var.setAttr('Obj', sample)
        objcoeff = var.getAttr('Obj')
        sqnorm = sqnorm + objcoeff*objcoeff
    norm = math.sqrt(sqnorm)
    if relax.getAttr('Status') == gurobipy.GRB.OPTIMAL:
        if norm > 0.1:
            minimum = min(minimum, relax.ObjVal)
            maximum = max(maximum, relax.ObjVal)
            minimumnormalized = min(minimumnormalized, relax.ObjVal/norm)
            maximumnormalized = max(maximumnormalized, relax.ObjVal/norm)
            print(f"{model.Modelname:<28} | {relax.ObjVal:>8.2} |   {relax.ObjVal/norm:>8.2} | {norm:>8.2} ")
            withvals = withvals + 1
        else:
            print(f"{model.Modelname:<28} |          |            | {norm:>8.2} ")
    else:
        errprint(f"{model.Modelname:<28} | Status code {relax.getAttr('Status')}")
        break

        alloutput.append([model.Modelname,results])
    sys.stdout.flush()
    sys.stderr.flush()
print(minimum, maximum)
print(minimumnormalized, maximumnormalized)
