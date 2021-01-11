#!/bin/bash
cd /home/rcf-40/hp_273/diffusion/run_on_hpc/fix_thsh/
source /usr/usc/python/3.7.4/setup.sh
python3 sbm_fix_thsh_hpc.py $SLURM_PROCID

