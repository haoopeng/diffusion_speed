# diffusion_speed

This repository hosts the code to reproduce results of the following paper:
  
H. Peng, A. Nematzadeh, D.M. Romero, E. Ferrara. Network Modularity Controls the Speed of Information Diffusion. Physical Review E 102, 052316 (2020).


## File organization

* To produce Figs. 1-2 in the main paper, run `sbm_simulation.ipynb`, `sbm_analytical.ipynb`, and then `figures_1_2_3.ipynb` (only the first two parts). These two figures are relatively easy (and quick) to make as it fixes both the threshold and the seed_size (no need of a hpc server). They are only a horizontal slice of Fig. 3a.

* To produce the two phase diagrams in Fig. 3, run the last part in `figures_1_2_3.ipynb` (it will point you to first run `sbm_fix_rho0_hpc` (for Fig. 3a) and `sbm_fix_thsh_hpc` (for Fig. 3b) to generate the data). Note that the script in `sbm_fix_thsh_hpc` saves only the final size and time data, whereas the script in `sbm_fix_rho0_hpc` saves per time step data that will be reused in Fig. 5a (therefore the pickle file is too large to be shared). 

* To produce Fig. 4a, run `lfr_simulation.ipynb` (it will point you to run `lfr_hpc` first); to produce Fig. 4b, run `twitter_simulation.ipynb` (it will point you to run `twitter_hpc` first). Both hpc scripts will save the per time step data that will be reused to produce Fig. 5b and Fig. 5c.

* Run scripts in the folder `speed_fix_size` to produce Fig. 5.

* The command I used to run all hpc scirpts is: `sbatch xyz.slurm`. Each phase diagram script (hpc) utilizes 51 computer nodes to simultaneously generate 1/51 slice of the data.

* I didn't share all the pickle files (simulation data) as each of them is about the size of 500 MB.
