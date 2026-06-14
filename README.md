# MIPLIB-meanwidth
The mean width of a polyhedron P is defined as the mean value of the LP max theta^T (x-x') subject to x,x' in P, where the mean is taken over the uniformly random choice of theta from the unit sphere.

In this code we compute the mean width for the LP relaxations of the MIPLIB 2017 benchmark set.

To use the code, make sure you have Gurobi and its python interface installed.
You need to point the code to the directory where you have stored the MIPLIB instances.

The big computation happens in meanwidth.py. It reads the MIPs, takes the LP relaxations, and maximizes and minimizes random objectives. This is a long computation.
The results are written to the output/ directory, with either a status code or a set of minimization and maximization values.
Due to the length of the computation, we have done our best to make it possible to recompute for only a single instance. For that reason, the code will check whether the destination log file already exists and only do the hard computer work if it finds so such existing file.
We have done our best to make everything deterministic, and at least on Huiberts' machine it seems to reproduce.

Assorted post-hoc data analysis is performed in the script means.py, including the numbers reported in the paper.

To see the state of the repository as it was for an earlier paper version, please look at the git tags.


If you want to see the code work, run createtestproblems.py to create some instances, then run meanwidth.py for the actual computations using Gurobi, and finally run analysis.py to get some summaries of the generated outputs.
To run with netlib and miplib instances, you need to acquire those and put the mps files in input/netlib and input/miplib.

Logs from my own run of meanwidth.py are included in the output directory, so you can also directly modify analysis.py if you are interested in making statistics.

Note: meanwidth.py will skip over any instance that already has an associated output file. Therefore to rerun any instance you first manually have to delete the corresponding output log. This should make it easy to verify that the results reproduce on individual instances.

In my own run I downloaded the NETLIB instances from here: https://github.com/SkyLiu0/netlib/tree/d7193c4d5e1d0824d2e33b2ba17191f328582459
We only use the feasible instances.



Changes compared to arxiv-v1:
- Variable counts are included, allowing us to plot mean width versus dimension.
- Code can now use NETLIB as well as MIPLIB instances, since the structure of typical LPs is a bit different from those of MIP LP relaxations. Thanks to Julian Hall for the suggestion.
- Improved error handling
- More pretty printing
- Added unit cubes as a little reference set

Note on running time:
I was confortable letting this experiment run for a really long time. If you are not, then probably you should avoid replicating the computation for the following instances:
- cryptanalysiskb128n5obj14 (32 minutes)
- cryptanalysiskb128n5obj16 (32 minutes)
- ex10 (5 hours)
- ex9 (1,5 hour)
- gfd-schedulen180f7d50m30k18 (40 minutes)
- neos-2075418-temuka (5 hours)
- neos-5049753-cuanza (13 hours)
- neos-5104907-jarama (13 hours)
- ns1116954 (45 minutes)
- rail02 (75 minutes)
- square47 (50 minutes)
- supportcase19 (50 minutes)
- supportcase22 (26 minutes)

On dependencies:
createtestproblems.py depends on having Gurobi and gurobipy installed.
meanwidth.py assumes you have Gurobi 13.0.1 exactly.
analysis.py has no dependencies, or at least nothing that cant be found in pip.

If you have a different Gurobi version I cannot guarantee reproducibility. You can still run the code, but you need to remove the version safeguard in analysis.py.
