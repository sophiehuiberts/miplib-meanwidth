# MIPLIB-meanwidth
The mean width of a polyhedron P is defined as the mean value of the LP max theta^T (x-x') subject to x,x' in P, where the mean is taken over the uniformly random choice of theta from the unit sphere.

In this code we compute the mean width for the LP relaxations of the MIPLIB 2017 benchmark set.

To use the code, make sure you have Gurobi and its python interface installed.
You need to point the code to the directory where you have stored the MIPLIB instances.

The big computation happens in meanwidth.py. It reads the MIPs, takes the LP relaxations, and maximizes and minimizes random objectives. This is a long computation.
The results are written to the output/ directory, with either a status code or a set of minimization and maximization values.
Due to the length of the computation, we have done our best to make it possible to recompute for only a single instance. For that reason, the code will check whether the destination log file already exists and only do the hard computer work if it finds so such existing file.
We have done our best to make everything deterministic, and at least on Huiberts' machine it seems to reproduce.

The script histograms.py uses the log files in output/ and draw histograms of the individual sample widths for every instance. These histograms are written as png files to histograms/ and may give some intuition for what the distributions look like.

Assorted post-hoc data analysis is performed in the script means.py, including the numbers reported in the paper.

To see the state of the repository as it was for an earlier paper version, please look at the git tags.


If you want to see the code work, run createtestproblems.py to create some instances, then run meanwidth.py for the actual computations using Gurobi, and finally run analysis.py or histograms.py to get some summaries of the generated outputs.
To run with netlib and miplib instances, you need to acquire those and put the mps files in input/netlib and input/miplib.

Logs from my own run of meanwidth.py are included in the output directory, so you can also directly modify analysis.py if you are interested in making statistics.

Note: meanwidth.py will skip over any instance that already has an associated output file. Therefore to rerun any instance you first manually have to delete the corresponding output log. This should make it easy to verify that the results reproduce on individual instances.

In my own run I downloaded the NETLIB instances from here: https://github.com/SkyLiu0/netlib/tree/d7193c4d5e1d0824d2e33b2ba17191f328582459
We only use the feasible instances.
