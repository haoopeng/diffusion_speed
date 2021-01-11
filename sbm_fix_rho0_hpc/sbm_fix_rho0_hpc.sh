#!/bin/bash
cd /home/rcf-40/hp_273/diffusion/run_on_hpc/fix_rho/
source /usr/usc/python/3.7.4/setup.sh
python3 sbm_fix_rho0_hpc.py $SLURM_PROCID
