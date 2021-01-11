#!/bin/bash
#SBATCH --time=10:00:00
#SBATCH --ntasks=51
#SBATCH --mem-per-cpu=20G
srun bash sbm_fix_rho0_hpc.sh
