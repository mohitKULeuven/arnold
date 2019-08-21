# CountOR

An implementation of the ARNOLD algorithm for learning polynomial constraints from positive data.


# Requirements
- [minizinc](https://www.minizinc.org/)
- pymzn
- scipy
- numpy
- math
- pickle
- itertools
- copy
- argparse
- csv
- random


# Installation
Install all the packages mentioned above, unzip the code in any directory with write permissions and you should be able to run the code.


# How to use
Currently the implementation is in the experiment mode. Given any minizinc file as an input, the algorithm samples some examples and learns a model which is then written in a minizinc file.
To run an experiment follow these steps:
1. Make sure there is a folder inside "experiments/" with the name of the problem, for example shipping.
2. Inside shipping folder, there should be 3 files:
	- "shipping.mzn" : this is the model we try to learn
	- "shipping.mzn.vars" : this contains the name of all the variables and constants in the model
	- "shipping.mzn.inputvars" : this contains the name of all the constants in the model
	(Please have a look at some of the folders which has already been put there to run experiments)
3. Now to run experiments for a particual problem simply call "experiment.py" with the following arguments:
	--file <name of the folder in experiment with minizinc files for this particular problem>
	--sum <an array of integers defining the maximum number of terms in a constraint>
	--prod <an array of integers defining the maximum number of tensors in a term>

One example to run an existing problem in the experiment would be to run the following command:

python experiment.py --file shipping --sum 1 --prod 1 2 3

This command will run the experiments for shippping problem be fixing number of terms to 1 and varying the number of variables in each term. It will generate the results of the experiment with values on recall, precision and time inside "experiments/shipping/results/". The resulted minizinc file for each experiment is stored in "experiments/shipping/minizinc/"


# Authors
Mohit Kumar < mohit _dot_ kumar _at_ cs _dot_ kuleuven _dot_ be >
