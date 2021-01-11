#!/bin/bash
#SBATCH --time=23:00:00
#SBATCH --ntasks=51
#SBATCH --mem-per-cpu=20G
srun bash twitter_hpc.sh
