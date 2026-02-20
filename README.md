# MIPLIB-meanwidth
Half the mean width of a polyhedron P equals the mean value of the LP max theta^T x subject to x in P, where the mean is taken over the uniformly random choice of theta from the unit sphere.

In this code we compute half the mean width for the LP relaxations of the MIPLIB 2017 benchmark set.

To use the code, make sure you have Gurobi and its python interface installed. You need to point the code to the directory where you have stored the MIPLIB instances. Output is to stdout.

To see the state of the repository as it was for a particular paper version, please look at the git tags.
