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
