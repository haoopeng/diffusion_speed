#!/bin/bash
cd /home/rcf-40/hp_273/diffusion/LFR/run_on_hpc
source /usr/usc/python/3.7.4/setup.sh
python3 lfr_hpc.py $SLURM_PROCID

