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


def attribute_assortativity_coefficient(G, partition, directed=False):
    num_community = len(set(partition.values()))
    mixing_matrix = np.zeros(shape = (num_community, num_community))              
    for s, t in G.edges():
        mixing_matrix[partition[s], partition[t]] += 1
        # if undirect, the order (s, t) gives by G.edges() is misleading. So we double count every edge.
        if not directed:
            mixing_matrix[partition[t], partition[s]] += 1
    mixing_matrix /= np.sum(mixing_matrix)
    square_sum = np.sum(np.linalg.matrix_power(mixing_matrix, 2))
    tra = np.trace(mixing_matrix)
    r = (tra - square_sum)/(1-square_sum)
    return r


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


def get_cid_cid_edges(Gcc, part):
    cid_cid_edges = defaultdict(set)
    for s, t in Gcc.edges:
        c1 = part[s]
        c2 = part[t]
        if c1 < c2:
            cid_cid_edges[(c1, c2)].add((s, t))
        else:
            cid_cid_edges[(c2, c1)].add((t, s))
    return cid_cid_edges

def get_valid_pairs(cid_cid_edges):
    valid_same_comm_pairs = set()
    valid_cross_comm_pairs = set()

    for (c1, c2), edge_set in cid_cid_edges.items():
        if c1 != c2:
            if len(edge_set) == 1:
                # print('%d-%d has only one edge, not enough to sample two edges'%(c1, c2))
                pass
            else:
                valid_cross_comm_pairs.add((c1, c2))
        else:
            valid_same_comm_pairs.add((c1, c2))
    return valid_same_comm_pairs, valid_cross_comm_pairs

def prepare_data(Gcc, part):
    Gcc_cp = Gcc.copy()
    cid_cid_edges = get_cid_cid_edges(Gcc_cp, part)
    valid_same_comm_pairs, valid_cross_comm_pairs = get_valid_pairs(cid_cid_edges)
    return Gcc_cp, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs


# In[364]:


def rewire_same_comm_edges(Gcc, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs):
    if len(valid_same_comm_pairs) >= 2:
        # random sample two valid communities
        c1_c1, c2_c2 = random.sample(valid_same_comm_pairs, k=2)
        (a, b) = random.sample(cid_cid_edges[c1_c1], k=1)[0]
        (c, d) = random.sample(cid_cid_edges[c2_c2], k=1)[0]
        if Gcc.has_edge(a, c) == 0 and Gcc.has_edge(b, d) == 0:
            Gcc.remove_edges_from([(a, b), (c, d)])
            cid_cid_edges[c1_c1].remove((a, b))
            cid_cid_edges[c2_c2].remove((c, d))
            if len(cid_cid_edges[c1_c1]) == 0:
                valid_same_comm_pairs.remove(c1_c1)
            if len(cid_cid_edges[c2_c2]) == 0:
                valid_same_comm_pairs.remove(c2_c2)
            Gcc.add_edges_from([(a, c), (b, d)])
            key = tuple(sorted((c1_c1[0], c2_c2[0])))
            if c1_c1[0] < c2_c2[0]:
                cid_cid_edges[key].update([(a, c), (b, d)])
            else:
                cid_cid_edges[key].update([(c, a), (d, b)])
            valid_cross_comm_pairs.add(key)
        elif Gcc.has_edge(a, d) == 0 and Gcc.has_edge(b, c) == 0:
            Gcc.remove_edges_from([(a, b), (c, d)])
            cid_cid_edges[c1_c1].remove((a, b))
            cid_cid_edges[c2_c2].remove((c, d))
            if len(cid_cid_edges[c1_c1]) == 0:
                valid_same_comm_pairs.remove(c1_c1)
            if len(cid_cid_edges[c2_c2]) == 0:
                valid_same_comm_pairs.remove(c2_c2)
            Gcc.add_edges_from([(a, d), (b, c)])
            key = tuple(sorted((c1_c1[0], c2_c2[0])))
            if c1_c1[0] < c2_c2[0]:
                cid_cid_edges[key].update([(a, d), (b, c)])
            else:
                cid_cid_edges[key].update([(d, a), (c, b)])
            valid_cross_comm_pairs.add(key)
        else:
            pass
    else:
        pass
        
def rewire_cross_comm_edges(Gcc, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs):
    if len(valid_cross_comm_pairs) >= 1:
        # random sample a valid pair of communities
        (c1, c2) = random.sample(valid_cross_comm_pairs, k=1)[0]
        # we know that a, c are in c1, and b, d are in c2: see how we creat cid_cid_edges.
        (a, b), (c, d) = random.sample(cid_cid_edges[(c1, c2)], k=2)
        if a != c and b != d:    
            if Gcc.has_edge(a, c) == 0 and Gcc.has_edge(b, d) == 0:
                Gcc.remove_edges_from([(a, b), (c, d)])
                cid_cid_edges[(c1, c2)].remove((a, b))
                cid_cid_edges[(c1, c2)].remove((c, d))
                if len(cid_cid_edges[(c1, c2)]) < 2:
                    valid_cross_comm_pairs.remove((c1, c2))
                Gcc.add_edges_from([(a, c), (b, d)])
                cid_cid_edges[(c1, c1)].add((a, c))
                cid_cid_edges[(c2, c2)].add((b, d))
                valid_same_comm_pairs.update([(c1, c1), (c2, c2)])
        # two edges share a common node: don't need to swap ends
        else:
            pass
    else:
        pass
    
def swap_edges(Gcc, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs, num_switches, p):
    for i in range(num_switches):
        if random.random() < p:
            rewire_same_comm_edges(Gcc, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs)
        else:
            rewire_cross_comm_edges(Gcc, cid_cid_edges, valid_same_comm_pairs, valid_cross_comm_pairs)

