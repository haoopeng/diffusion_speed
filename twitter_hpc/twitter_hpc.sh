#!/bin/bash
cd /home/rcf-40/hp_273/diffusion/RealNet/run_on_hpc
source /usr/usc/python/3.7.4/setup.sh
python3 twitter_hpc.py $SLURM_PROCID

