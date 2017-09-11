#!/bin/sh
##############################################################################
#   .,**ooooo***.       ',***********      ',************          *****.
#  .ooooooooooooo       '*ooooooooooo      .ooooooooooooo         'oooooo.
#  *ooo.''''',ooo       '*o*.''''''''       '''',ooo.''''        '*oo,.*oo.
# '*ooo       '''       '*oo*,,,,,,,,           .ooo'           '*oo,  .oo*'
# '*ooo                 '*oooooooooo*           .ooo'           ,oo,    ooo*'
# '*ooo      ',**'      '*o*.''''''''           .ooo'          .ooo*****oooo*
#  ,ooo*,,,,,*ooo'      '*oo*,,,,,,,,           .ooo'         .oooooooooooooo
#  '*oooooooooooo       '*ooooooooooo'          .ooo'         oooo,''''''.*oo.
#    '.,,,,,,,,.'        .,.........,           '.,,          ,.,.        '...
#
#                          CETA-CIEMAT GPU CLUSTER
#                   ***************************************
#
#                                   Divos
#
##############################################################################

#SBATCH --nodes=2
#SBATCH --partition=gpu
#SBATCH --gres=gpu:kepler:2
#SBATCH --time=04:00:00

module load pythonlibs/3.6.1/pycuda/2017.1 pythonlibs/3.6.1/numpy/1.13.0 pythonlibs/3.6.1/scipy/0.19.1 pythonlibs/3.6.1/matplotlib/2.0.2
python3  Divos.py $1


exit 0
