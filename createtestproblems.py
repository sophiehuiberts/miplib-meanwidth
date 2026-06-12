#!/usr/bin/python
# coding: utf-8
import gurobipy
from pathlib import Path

Path("input").mkdir(exist_ok=True)
Path("input/tests").mkdir(exist_ok=True)

env = gurobipy.Env()
env.setParam('OutputFlag',False)

for i in range(1,21):
    m = gurobipy.Model()
    m.addVars(range(2**i), lb=0, ub=1)
    m.update()
    m.write(f"input/tests/unit-cube-{2**i}.mps")
