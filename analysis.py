#!/usr/bin/python
# coding: utf-8
import os
import os.path
from pathlib import Path
import math
import sys
from statistics import stdev, mean, median
import json
import hashlib
import matplotlib.pyplot as plt

# Ensure any stale intermediate files are caught by hashing current script
with open(__file__,"rb") as f:
    current_script_hash = hashlib.file_digest(f, hashlib.sha256).hexdigest()
    print(f"Analysis script version {current_script_hash}")

def analyze(lib):
    print(f"===============================================================================================")
    print(f"                                    {lib}                                 ")
    print(f"===============================================================================================")
    print(f"  Model Name                 |      Minimum |         Mean |      Maximum |    mean/sqrt(dim)")
    print(f"-----------------------------------------------------------------------------------------------")
    worklimits = []
    unboundeds = []
    othererrors = []
    successes = 0

    samplemeans = []
    samplestdsovermeans = []
    samplemaxes = []
    samplemeansphaseone = []

    samplemeansoversqrtdim = []
    samplemeansoversqrtdof = []
    variablecounts = []
    degreesoffreedomcounts = []

    for direntry in os.scandir(f"output/{lib}"):
        f = open(direntry, 'r')

        scriptversionline = f.readline()
        gurobiversionline = f.readline()
        modelnameline = f.readline()
        variablecountline = f.readline()
        equalitycountline = f.readline()
        statuscodeline = f.readline()
        minimizationline = f.readline()
        maximizationline = f.readline()

        f.close()

        # To be honest I don't know how well these results will reproduce on a different machine.
        # But at least the script version and Gurobi version can be accounted.
        if scriptversionline != "Script version b87b35861c3ed787144dcc247c45807fe781f70546bb3f40c8b798db33a1b7af\n":
            print(f"{os.fsdecode(direntry)} produced by wrong script version")
            exit()
        if gurobiversionline != "Gurobi version (13, 0, 1)\n":
            print(f"{os.fsdecode(direntry)} produced with wrong Gurobi version")
            exit()
        if modelnameline[:11] != "Model name ":
            print(f"{os.fsdecode(direntry)} has no proper model name line")
            exit()
        model = modelnameline[11:-1]
        if statuscodeline != "Full set of 200 results\n":
            statuscode = statuscodeline.split(' ')[2]
            if statuscode == "16":
                worklimits.append(model)
            elif statuscode == "4":
                unboundeds.append(model)
            elif statuscode == "5":
                unboundeds.append(model)
            elif statuscode == "11":
                print("=========================================")
                print(" WARNING")
                print(f" RUN {model} WAS ABANDONED BY USER ")
                print("=========================================")
                othererrors.append(model)
            else:
                print("=========================================")
                print(" WARNING")
                print(f" RUN {model} HAS UNKNOWN STATUS CODE {statuscode}")
                print("=========================================")
                othererrors.append(model)
            continue
        minimums = json.loads(minimizationline)
        maximums = json.loads(maximizationline)

        variablecount = int(variablecountline.split(' ')[2])
        variablecounts.append(variablecount)
        equalitycount = int(equalitycountline.split(' ')[2])
        degreesoffreedomcounts.append(variablecount - equalitycount)

        if len(minimums) != 100:
            print(f"{os.fsdecode(f)} has {len(minimums)} minimization results instead of 100")
            exit()
        if len(maximums) != 100:
            print(f"{os.fsdecode(f)} has {len(maximums)} maximization results instead of 100")
            exit()
        successes = successes + 1

        # computing sample mean width for the LP relaxation is easy
        widths = [maximums[i]-minimums[i] for i in range(100)]
        sample_mean_feasible = mean(widths)
        sample_stdev = stdev(widths)
        samplemeans.append(sample_mean_feasible)
        samplemaxes.append(max(widths))
        samplestdsovermeans.append(sample_stdev/sample_mean_feasible)

        # when we force the origin to be feasible, i.e., we find the mean width of conv({0}, LP feasible set),
        # we can compute the sample mean for this other body quite easily
        convorigin_minimums = [min(0,x) for x in minimums]
        convorigin_maximums = [max(0,x) for x in maximums]
        convorigin_widths = [convorigin_maximums[i]-convorigin_minimums[i] for i in range(100)]

        sample_mean_phaseone = mean(convorigin_widths)
        sample_stdev_phaseone = stdev(convorigin_widths)
        samplemeansphaseone.append(sample_mean_phaseone)

        samplemeansoversqrtdim.append(sample_mean_feasible/math.sqrt(variablecount))
        samplemeansoversqrtdof.append(sample_mean_feasible/math.sqrt(variablecount-equalitycount))

        print(f"{model:<28}   {min(widths):>12.2f}   {sample_mean_feasible:>12.2f}   {max(widths):>12.2f}   {sample_mean_feasible/math.sqrt(variablecount):>12.2f}")



    print(f"{len(unboundeds)} unboundeds")
    print(f"{len(worklimits)} work limits")
    print(f"{len(othererrors)} other errors")
    print(f"{successes} successes")
    print(f"{len(unboundeds) + len(worklimits) + successes + len(othererrors)} instances total.")

    print("===== sample means summary =====")
    print(f"{len([x for x in samplemeans if x < 1e-1])} means below 1e-1")
    print(f"{len([x for x in samplemeans if x > 1e-1 and x < 1e1])} means between 1e-1 and 1e1")
    print(f"{len([x for x in samplemeans if x > 1e1 and x < 1e2])} means between 1e1 and 1e2")
    print(f"{len([x for x in samplemeans if x > 1e2 and x < 1e4])} means between 1e2 and 1e4")
    print(f"{len([x for x in samplemeans if x > 1e4 and x < 1e6])} means between 1e4 and 1e6")
    print(f"{len([x for x in samplemeans if x > 1e6 and x < 1e9])} means between 1e6 and 1e9")
    print(f"{len([x for x in samplemeans if x > 1e9])} means over 1e9")

    print("===== sample means over sqrt(dim) summary =====")
    print(f"{len([x for x in samplemeansoversqrtdim if x < 1e-2])} below 1e-2")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e-2 and x < 1e-1])} between 1e-2 and 1e-1")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e-1 and x < 1e1])} between 1e-1 and 1e1")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e1 and x < 1e2])} between 1e1 and 1e2")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e2 and x < 1e3])} between 1e2 and 1e3")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e3 and x < 1e4])} between 1e3 and 1e4")
    print(f"{len([x for x in samplemeansoversqrtdim if x > 1e4])} over 1e4")

    return samplemeans, variablecounts, degreesoffreedomcounts

fig,ax = plt.subplots()
ax.set_ylabel("Sample mean width (n=100)")
ax.set_xlabel("Variable count")
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid()

if Path('output/tests').is_dir():
    means,varcounts,degreesoffreedom = analyze('tests')
    ax.scatter(varcounts,means,marker='s',alpha=0.3,c='orange',label="Unit cubes")
if Path('output/netlib').is_dir():
    means,varcounts,degreesoffreedom = analyze('netlib')
    ax.scatter(varcounts,means,marker='^',alpha=0.3,c='green',label="NETLIB")
if Path('output/miplib').is_dir():
    means,varcounts,degreesoffreedom = analyze('miplib')
    ax.scatter(varcounts,means,marker='o',c='blue',alpha=0.3,label="MIPLIB")
ax.legend()
plt.savefig('plot-meanwidth-varcount.pdf')
plt.savefig('plot-meanwidth-varcount.svg')
