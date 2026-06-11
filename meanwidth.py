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
import hashlib
from pathlib import Path

# Ensure any stale intermediate files are caught by hashing current script
with open(__file__,"rb") as f:
    current_script_hash = hashlib.file_digest(f, hashlib.sha256).hexdigest()
    print(f"Script version {current_script_hash}")

# How many random unit-length objective vectors will we optimize per instance?
samples_per_model = 100

# Work limit is like time limit but deterministic.
# Chose 60 seconds
work_limit_per_sample = 5*60

env = gurobipy.Env()
env.setParam('OutputFlag',False)

print(f"    Model Name               | Minimum |   Median  |   Mean   | Maximum")
print(f"----------------------------------------------------------------------------")


def find_meanwidth(file, testset):
    model = gurobipy.read(os.fsdecode(file),env=env)

    modelname = model.ModelName
    if modelname == "":
        modelname = file.name

    # We will just be doing the measurements themselves in computation
    # Analysis will be performed later
    if os.path.isfile(f"output/{testset}/{modelname}-meanwidthlog.txt"):
        print(f"output/{testset}/{modelname}-meanwidthlog.txt already exists")
        sys.stdout.flush()
        return

    equalityconstraintcount = 0
    for constr in model.getConstrs():
        if constr.getAttr("Sense") == '=':
            equalityconstraintcount = equalityconstraintcount + 1
    for var in model.getVars():
        if var.getAttr("UB") < var.getAttr("LB") + 1e-6:
            equalityconstraintcount = equalityconstraintcount + 1

    # Since the amount of previously processed MIPs isn't fixed, we reset seed
    np.random.seed(0)

    # We solve the relaxation with different objectives
    relax = model.relax()

    # No crossover to get a basic solution. Tiny loss of accuracy but it saves time
    relax.Params.Crossover = 0

    # LP solving method to deterministic concurrent
    relax.setParam('Method', 4)

    # Work limit is like time limit but deterministic
    relax.setParam('WorkLimit',work_limit_per_sample)

    minimizationresults = []
    maximizationresults = []
    # tqdm makes a little progress bar
    statuscode = 0
    for attempts in tqdm(range(0,samples_per_model)):
        # Instead of sampling objective as a random unit vector,
        # we will sample its entries standard normal independent.
        # After optimizing we can divide by the 2-norm of the objective
        # Hence we track our squared norm
        sqnorm = 0
        for var in relax.getVars():
            sample = np.random.normal(0,1)
            var.setAttr('Obj', sample)
            sqnorm = sqnorm + sample*sample

        # we will both minimize and maximize the objective
        # otherwise it may complicate Milman concentration of measure
        relax.setAttr('ModelSense', 1) # minimize
        relax.optimize()
        if relax.getAttr('Status') == gurobipy.GRB.OPTIMAL:
            # See here the division by the objective norm
            minimizationresults.append(relax.ObjVal / math.sqrt(sqnorm))
        else:
            # No optimal solution found: abort this instance
            print(f"{modelname:<28} | Status code {relax.getAttr('Status')} on minimization attempt {attempts}")
            statuscode = relax.getAttr('Status')
            sys.stdout.flush()
            break

        relax.setAttr('ModelSense', -1) # maximize
        relax.optimize()
        if relax.getAttr('Status') == gurobipy.GRB.OPTIMAL:
            # See here the division by the objective norm
            maximizationresults.append(relax.ObjVal / math.sqrt(sqnorm))
        else:
            # No optimal solution found: abort this instance
            print(f"{modelname:<28} | Status code {relax.getAttr('Status')} on maximization attempt {attempts}")
            statuscode = relax.getAttr('Status')
            sys.stdout.flush()
            break
    sys.stdout.flush()
    # Now write to file what we found
    # Will write the analysis script later
    with open(f"output/{testset}/{modelname}-meanwidthlog.txt",'w',encoding="utf-8") as outputfile:
        outputfile.write(f"Script version {current_script_hash}\n")
        outputfile.write(f"Gurobi version {gurobipy.gurobi.version()}\n")
        outputfile.write(f"Model name {modelname}\n")
        outputfile.write(f"Variable count {len(relax.getVars())}\n")
        outputfile.write(f"Equality count {equalityconstraintcount}\n")
        if len(maximizationresults) == samples_per_model:
            # aggregate min and max results to keep old stdout format
            results = [-x for x in minimizationresults] + maximizationresults
            outputfile.write(f"Full set of {len(results)} results\n")
            json.dump(minimizationresults, outputfile)
            outputfile.write(f"\n")
            json.dump(maximizationresults, outputfile)
            outputfile.write(f"\n")
            print(f"{modelname:<28} | {min(results):>8.2} | {median(results):>8.2} | {mean(results):>8.2} | {max(results):>8.2}")
            sys.stdout.flush()
        else:
            outputfile.write(f"Status code {statuscode} on attempt {attempts}\n")
            json.dump(minimizationresults, outputfile)
            outputfile.write(f"\n")
            json.dump(maximizationresults, outputfile)
            outputfile.write(f"\n")
    sys.stdout.flush()

Path("output").mkdir(exist_ok=True)
Path("output/netlib").mkdir(exist_ok=True)
Path("output/miplib").mkdir(exist_ok=True)

if Path('input/tests').is_dir():
    Path("output/tests").mkdir(exist_ok=True)
    for file in os.scandir('./input/tests'):
        find_meanwidth(file, 'tests')

if Path('input/netlib').is_dir():
    for file in os.scandir('./input/netlib'):
        find_meanwidth(file, 'netlib')

if Path('input/miplib').is_dir():
    for file in os.scandir('./input/miplib'):
        find_meanwidth(file, 'miplib')
