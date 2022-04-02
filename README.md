# diffusion_speed

This repository hosts the code to reproduce results of the following paper:
  
H. Peng, A. Nematzadeh, D.M. Romero, E. Ferrara </br>
[Network Modularity Controls the Speed of Information Diffusion](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.102.052316) </br>
*Physical Review E* 102, 052316 (2020)


## File organization

* To produce Fig. 1 and Fig. 2 in the paper, first run `sbm_simulation.ipynb` and `sbm_analytical.ipynb`, and then run the first two parts of `figures_1_2_3.ipynb`. The two figures are relatively easy and quick to produce, therfore you do not need a hpc server for this process.

* To produce the two phase diagrams in Fig. 3, run the last part in `figures_1_2_3.ipynb`; it will point you to first run `sbm_fix_thsh_hpc` (for Fig. 3a) and run `sbm_fix_rho0_hpc` (for Fig. 3b) to generate the data. Note that the script in `sbm_fix_rho0_hpc` creats a file that stores only the final size and time information, whereas the script in `sbm_fix_thsh_hpc` stores per time step data that will be reused in Fig. 5a.

* To produce Fig. 4a, run `lfr_simulation.ipynb` (it will point you to run `lfr_hpc` first); to produce Fig. 4b, run `twitter_simulation.ipynb` (it will point you to run `twitter_hpc` first). Both "hpc" scripts will save the per time step data that will be reused to produce Fig. 5b and Fig. 5c.

* Run scripts in the folder `speed_fix_size` to produce Fig. 5.

* The command I used to run all hpc scirpts is: `sbatch xyz.slurm`. Each phase diagram script (hpc) utilizes 51 computer nodes to simultaneously generate 1/51 slice of the data.

* I didn't share all the simulation data generated in the pickle format because each of them has a file size larger than 500 MB, which exceeds the size limit set by Github.
