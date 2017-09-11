#!/bin/sh

for file in $(ls inputFiles)
do
	sbatch -o results/slurm-%j.out ./fermi.sh inputFiles/$file
done




