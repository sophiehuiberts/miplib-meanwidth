#!/usr/bin/python
# coding: utf-8
import os
import os.path
import math
import sys
from statistics import stdev, mean, median
import json
import hashlib
import matplotlib.pyplot as plt
from matplotlib import colors

# Ensure any stale intermediate files are caught by hashing current script
with open(__file__,"rb") as f:
    current_script_hash = hashlib.file_digest(f, hashlib.sha256).hexdigest()
    print(f"Script version {current_script_hash}")

print(f"    Model Name               | Minimum |   Median  |   Mean   | Maximum")
print(f"----------------------------------------------------------------------------")

worklimitcount = 0
unboundedcount = 0
successes = 0


# For every instance (they are stored as .mps.gz)
for direntry in os.scandir('output'):
    f = open(direntry, 'r')

    scriptversionline = f.readline()
    gurobiversionline = f.readline()
    modelnameline = f.readline()
    statuscodeline = f.readline()
    minimizationline = f.readline()
    maximizationline = f.readline()

    f.close()

    if scriptversionline != "Script version 7673f1835e243e653da39473886fded06752d8ec19fa9b1aa2d9eb97f22a4ad1\n":
        print(f"{os.fsdecode(file)} produced by wrong script version")
        exit()
    if gurobiversionline != "Gurobi version (13, 0, 1)\n":
        print(f"{os.fsdecode(file)} produced with wrong Gurobi version")
        exit()
    if modelnameline[:11] != "Model name ":
        print(f"{os.fsdecode(file)} has no proper model name line")
        exit()
    model = modelnameline[11:-1]
    if statuscodeline != "Full set of 200 results\n":
        statuscode = statuscodeline.split(' ')[2]
        if statuscode == "16":
            worklimitcount = worklimitcount + 1
        if statuscode == "4":
            unboundedcount = unboundedcount + 1
        if statuscode == "5":
            unboundedcount = unboundedcount + 1
        continue
    minimums = json.loads(minimizationline)
    maximums = json.loads(maximizationline)

    if len(minimums) != 100:
        print(f"{os.fsdecode(file)} has {len(minimums)} minimization results instead of 100")
        exit()
    if len(maximums) != 100:
        print(f"{os.fsdecode(file)} has {len(maximums)} maximization results instead of 100")
        exit()
    successes = successes + 1

    # computing sample mean width for the LP relaxation is easy
    widths = [maximums[i]-minimums[i] for i in range(100)]
    sample_mean_feasible = mean(widths)
    sample_stdev = stdev(widths)

    # when we force the origin to be feasible, i.e., we find the mean width of conv({0}, LP feasible set),
    # we can compute the sample mean for this other body quite easily
    convorigin_minimums = [min(0,x) for x in minimums]
    convorigin_maximums = [max(0,x) for x in maximums]
    convorigin_widths = [convorigin_maximums[i]-convorigin_minimums[i] for i in range(100)]

    sample_mean_phaseone = mean(convorigin_widths)
    sample_stdev_phaseone = stdev(convorigin_widths)

    print(f"{model:<28}     {min(widths)}       {sample_mean_feasible}      {sample_stdev}")

    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
    axs[0].hist(widths, bins='fd')
    axs[0].set_title("LP feasible")
    axs[1].hist(convorigin_widths, bins='fd')
    axs[1].set_title("conv(LP feasible,0)")
    fig.suptitle(f"Sampled widths for {model}")
    plt.savefig(f"histograms/{model}.png")
    plt.close()

print(f"{unboundedcount} unboundeds")
print(f"{worklimitcount} work limits")
print(f"{successes} successes")
print(f"{unboundedcount + worklimitcount + successes} total. For MIPLIB 2017 benchmark this should be 240")
