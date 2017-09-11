DiVoS (Dinamica de Vortices Superconductores)
=====
Tool for the simulation of superconducting vortex.


Autores: Manuel Rodríguez-Pascual, Juan Rodríguez-García, Rafael Mayo-García

CITATION: M. Rodríguez-Pascual et al, "Superconducting Vortex Lattice Configurations on Periodic Potentials: Simulation and Experiment". Journal of Superconductivity and Novel Magnetism, Volume 25, Issue 7, pp 2127–2130 (2012).


Running DiVoS
---------
format: python3 Divos.py <input_file>

to submit all experiments from inputFiles folder to Slurm Batch queue: sh submitEverything.sh

results are stored in /results as .txt (Divos output) .out (slurm output, including debugging info) and .png (graphical representation of best found solution).

Depending on your configuration, .png files may not be generated when running DiVoS in batch mode. If so, running "python3 paintResults.py <txt_file>" with a slurm output file will create the .png for that file. The process is automatizes, and "sh paintResults.sh" create the .png of every .txt file present in /results folder. 


(now, some scratch info for internal organization. This will be deleted when current experiment is finished)

Clean
-----
remove aux scripts (kepler.sh and so) when project is finished


Inputs
------
Los experimentos están en la carpeta InputFiles en forma de archivos de texto con sus especificaciones, organizados de la siguiente manera:

Experimentos: Annealing, Genetic, Combined

Vórtices: 1,2,3

Multiplicidad: 20     (aunque pone 50 en el nombre)

Annealing epoch: 10, 20, 40, 80, 100

Genetic generations: 100, 150, 200, 250, 300

Combined: Epoch=20, generations= 100, 150, 200, 250, 300

Si se importa Divos de mi ordenador también se puede implementar Divos con malla triangular.


Excel y organizacion
--------------------
Los archivos de la carpeta results se meten en las carpetas Divos/Organizacion según los algoritmos que se estén utilizando.
Desde Divos/Organizacion se ejecuta exceling_algoritmo para crear un archivo de texto que puede implementarse directamente en excel.
