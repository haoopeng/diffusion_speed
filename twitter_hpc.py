
# coding: utf-8

# In[71]:

import json
import time
import csv
import math
import pickle
import random
import datetime
import numpy as np
import pandas as pd
from sys import argv
# import community
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

from util import *
# In[50]:

Data_Root = '/auto/rcf-proj/ef/hp_273/Diffusion/RealNet/'
Data_Root = '/staging/ef/hp_273/Diffusion/RealNet/'
net_name = 'twitter'


G = nx.read_edgelist(Data_Root+'networks/twitter_combined.txt', delimiter=' ', create_using=nx.DiGraph(), nodetype=str)
G = G.to_undirected(reciprocal=False)

Gcc = max(nx.connected_components(G), key=len)
Gcc = G.subgraph(Gcc).copy()
# part = community.best_partition(Gcc, randomize=False)

with open(Data_Root+'networks/partition_%s.pickle'%net_name, 'rb') as file:
    part = pickle.load(file)

num_nodes = len(Gcc.nodes())
num_edges = len(Gcc.edges())
num_switches = num_edges//2

rhos = np.arange(0, 0.51, 0.01)
ps = np.arange(0, 1.02, 0.02)
# ntask = 51
# SLURM_PROCID starts from 0 to 50.
SLURM_PROCID = int(argv[1])
p = ps[SLURM_PROCID]

thsh = 0.3
num_runs = 100
f = 0.01

Gcc_cp, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs = prepare_data(Gcc, part)
swap_edges(Gcc_cp, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs, num_switches, p)

# In[382]:

sweeping_results = defaultdict(list)

for rho in rhos:
    num_seeds = int(rho*num_nodes)
    for i in range(num_runs):
        seeds = random.sample(Gcc_cp.nodes(), num_seeds)
        activation_time, step = simulation_ltm(Gcc_cp, thsh, seeds, frac=f)
        activation_per_step = [0] * step
        for node in activation_time:
            atime = activation_time[node]
            activation_per_step[atime] += 1
        sweeping_results[rho].append((len(activation_time), step, activation_per_step))

with open(Data_Root + 'per_step_data/phase_simu_%s_thsh_%s_f_%s_%s.pickle'%(net_name, thsh, f, SLURM_PROCID), 'wb') as file:
    pickle.dump(dict(sweeping_results), file)
