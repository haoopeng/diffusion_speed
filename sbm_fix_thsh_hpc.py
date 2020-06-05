
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


# In[41]:


CIs = {'90': 1.645, '95': 1.96, '99': 2.576}


# In[42]:


def comb(k):
    '''compute row and column of a k-th element in a lower-triangle'''
    row = int((math.sqrt(1+8*k)+1)/2)
    column = int(k-(row-1)*row/2)
    return [row, column]

def sample_pairs(li, num):
    ''' this func allows one to sample pairs without generating all possible pairs.
    '''
    total = int(len(li) * (len(li) - 1) / 2)
    if total > num:
        index = random.sample(range(total), num)
    else:
        print('This group is small, can not generate # of pairs required, return all pairs!')
        index = range(total)
    pairs = []
    for i in index:
        row, column = comb(i)
        pairs.append((li[row], li[column]))
    return pairs

def sample_cross_group_pairs(list_of_groups, num_pairs):
    '''sample `num_pairs` pairs per group pair
    '''
    num_groups = len(list_of_groups)
    cross_pairs = []
    for i in range(num_groups):
        for j in range(i+1, num_groups):
            len1, len2 = len(list_of_groups[i]), len(list_of_groups[j])
            total =  len1 * len2
            if num_pairs > total:
                index = range(total)
            else:
                index = random.sample(range(total), num_pairs)
            for k in index:
                row = int(k/len2)
                col = k % len2
                cross_pairs.append((list_of_groups[i][row], list_of_groups[j][col]))
    return cross_pairs

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


# In[43]:


def create_mm_network(numberOfNodes, numberOfEdges, numberOfCommunity, u):
    newmanGraph = nx.Graph()
    nlist = list(range(numberOfNodes))
    newmanGraph.add_nodes_from(nlist)
    edge_within_per = int((1-u)*numberOfEdges/numberOfCommunity)
    edge_cross_per = int(u*numberOfEdges/((numberOfCommunity-1)*numberOfCommunity/2))
    elist = []
    communities = list(chunks(nlist, num_nodes//numberOfCommunity))
    for group in communities:
        elist.extend(sample_pairs(group, edge_within_per))
    elist.extend(sample_cross_group_pairs(communities, edge_cross_per))
    newmanGraph.add_edges_from(elist)
    return newmanGraph, communities


# In[44]:


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
    # if len(current) >= 1, but no node is newly activated, then time_step will still add 1.
    # But actually we don't need to minus 1 later when calculating avg speed.
    # e.g, if the seeds infect zero node at step 1, then time_step is 1 since it attempted once.
    return (activation_time, time_step)


# ## MM Modular Graph with LTM

# In[46]:

num_nodes = 100000
avg_degree = 10
num_edges = num_nodes*avg_degree/2
num_community = 2
thsh = 0.35
num_runs = 100
f = 0.01


# In[57]:


rhos = np.arange(0, 0.51, 0.01)
us = np.arange(0, 0.51, 0.01)
sweeping_results = defaultdict(list)

# ntask = 51
# SLURM_PROCID starts from 0 to 50.
SLURM_PROCID = int(argv[1])


rho = rhos[SLURM_PROCID]
num_seeds = int(rho*num_nodes)

for u in us:
    for i in range(num_runs):
        G, communities = create_mm_network(num_nodes, num_edges, num_community, u)
        seeds = random.sample(communities[0], num_seeds) # seeds exist only in A.
        activation_time, step = simulation_ltm(G, thsh, seeds, frac=f)
        activation_per_step = [[0]*step for i in range(len(communities))]
        for i, group in zip(range(len(communities)), communities):
            for node in group:
                if node in activation_time:
                    atime = activation_time[node]
                    activation_per_step[i][atime] += 1
        sweeping_results[u].append((len(activation_time), step, activation_per_step))


Data_Root = '/auto/rcf-proj/ef/hp_273/Diffusion/SBM/per_step_data/'

with open(Data_Root + 'phase_simu_nodes_%sk_z_%s_thsh_%s_f_%s_%s.pickle'%(num_nodes//1000, avg_degree, thsh, f, SLURM_PROCID), 'wb') as file:
    pickle.dump(dict(sweeping_results), file)
