
# coding: utf-8

# In[2]:

import os
from sys import argv
import csv
import math
import random
import pickle
import datetime
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.interpolate import griddata
from networkx.algorithms.community import LFR_benchmark_graph


def simulation_ltm(G, thsh, seeds, frac=0.01):
    time_step = 0
    current = seeds
    activation_time = {s_node: time_step for s_node in current}
    activated_neighbors = defaultdict(int)
    need_to_be_active = set()
    while len(current) >= 1:
        time_step += 1
        candidate = set()
        for u in current:
            for w in G.neighbors(u):
                if w not in activation_time and w not in need_to_be_active:
                    candidate.add(w)
                    activated_neighbors[w] += 1
        for node in candidate:
            if activated_neighbors[node]/len(G[node]) >= thsh:
                need_to_be_active.add(node)
        newly_activated = random.sample(need_to_be_active, int(frac*len(need_to_be_active)))
        for node in newly_activated:
            activation_time[node] = time_step
            need_to_be_active.remove(node)
        current = newly_activated
    return (activation_time, time_step)


num_nodes = 25000
avg_degree = 10
thsh = 0.3
num_runs = 100
f = 0.01

tau1 = 2.5
tau2 = 1.5
max_degree = 30


rhos = np.arange(0, 0.51, 0.01)
us = np.arange(0.1, 1.00, 0.02)

sweeping_results = defaultdict(list)

# ntask = 51
# SLURM_PROCID starts from 0 to 50.
SLURM_PROCID = int(argv[1])


rho = rhos[SLURM_PROCID]
num_seeds = int(rho*num_nodes)

for u in us:
    for i in range(num_runs):
        G = LFR_benchmark_graph(num_nodes, tau1, tau2, u, average_degree=avg_degree, max_degree=max_degree, seed=10)
        seeds = random.sample(G.nodes(), num_seeds)
        activation_time, step = simulation_ltm(G, thsh, seeds, frac=f)
        activation_per_step = [0] * step
        for node in activation_time:
            atime = activation_time[node]
            activation_per_step[atime] += 1
        sweeping_results[u].append((len(activation_time), step, activation_per_step))


Data_Root = '/auto/rcf-proj/ef/hp_273/Diffusion/LFR/per_step_data/'

with open(Data_Root + 'phase_simu_nodes_%sk_z_%s_thsh_%s_f_%s_%s.pickle'%(num_nodes//1000, avg_degree, thsh, f, SLURM_PROCID), 'wb') as file:
    pickle.dump(dict(sweeping_results), file)
