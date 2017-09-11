# Use python 3.0 syntax
from  __future__  import  division,  print_function

import numpy

import pycuda.driver as drv
import pycuda.tools
import pycuda.autoinit
from pycuda.compiler import SourceModule
from math import ceil

import sys
import logging
logger = logging.getLogger(__name__)
from besselValues import besselValuesHardCoded
import const


mod = SourceModule("""

#include <stdio.h>
__constant__ double besselValuesHardCoded[500];
__constant__ int lammda=2600;

__device__ double besselFunction (double inputParam)
{
    //int chromosomeNum = threadIdx.x;
    //int numChromosomes = blockDim.x;
    //printf("(%d / %d): input param is %f\\n", chromosomeNum, numChromosomes, inputParam);

    if (inputParam == 0){
        return 0;
        }

    int lowLimit;
    double lowValue, diffValue, diffFactor, returnValue;

    inputParam = inputParam / lammda;

    if (inputParam < 0.0001){
        returnValue = 0;
    }

    else if (inputParam < 0.010){
        lowLimit = __double2int_rz(inputParam * 10000);
        diffFactor = inputParam * 10000 - lowLimit;
        lowValue = besselValuesHardCoded[lowLimit];
        diffValue = (besselValuesHardCoded[lowLimit] - besselValuesHardCoded[lowLimit-1]) * diffFactor;
        returnValue = lowValue - diffValue;
    }

    else if (inputParam < 0.10){
        lowLimit = 100 + __double2int_rz(inputParam * 1000);
        diffFactor = inputParam * 1000 - lowLimit + 100;
        lowValue = besselValuesHardCoded[lowLimit];
        diffValue = (besselValuesHardCoded[lowLimit] - besselValuesHardCoded[lowLimit+1]) * diffFactor;
        returnValue = lowValue - diffValue;
    }

    else if (inputParam < 1){
        lowLimit = 200 + __double2int_rz(inputParam * 100);
        diffFactor = inputParam * 100 - lowLimit + 200;
        lowValue = besselValuesHardCoded[lowLimit];
        diffValue = (besselValuesHardCoded[lowLimit] - besselValuesHardCoded[lowLimit+1]) * diffFactor;
        returnValue = lowValue - diffValue;
    }
    else if (inputParam < 10){
        lowLimit = 300 + __double2int_rz(inputParam * 10);
        diffFactor = inputParam * 10 - lowLimit + 300;
        lowValue = besselValuesHardCoded[lowLimit];
        diffValue = (besselValuesHardCoded[lowLimit] - besselValuesHardCoded[lowLimit+1]) * diffFactor;
        returnValue = lowValue - diffValue;
    }
    else if (inputParam < 100){
        lowLimit = 400 + __double2int_rz(inputParam);
        diffFactor = inputParam - lowLimit + 400;
        lowValue = besselValuesHardCoded[lowLimit];
        diffValue = (besselValuesHardCoded[lowLimit] - besselValuesHardCoded[lowLimit+1]) * diffFactor;
        returnValue = lowValue - diffValue;
    }
    else {
        printf ("ERROR CALCULATING BESSEL\\n");
        printf ("Distance is %f, asking for bessel %f\\n", inputParam * lammda, inputParam);
        returnValue = 0;
    }
    //printf("Bessel value of %f is %f\\n", inputParam, returnValue);
    return returnValue;

}



/*
this is parallelized: each GPU core calculates the value of two vortices.
the idea is:
A intarcts with B,C,D; B interacts with A,C,D and so.
- in a simple approach, each node would calculate one vortice: A-B,A-C,A-D; B-A,B-C,B-D and so; then we add all up
- but we are calculating one A-B, increasing time consumption.
- so we instead calculate 2*A-B, 2*A-C and so.
- In order to make all equal lenght, first node calculates all interactions STARTING with A (3) and all starting with D (0); second node, all starting with B (2) and with C (1) and so

*/
__global__ void oneBesselValueCUDA (int *element, int anclajesList[][3], int numAnclajes, int numChromosomes, bool anclajesInfluence, double *solution){

    int firstChromosome = threadIdx.x;
    int lastChromosome = numChromosomes - firstChromosome -1;

    int firstX, lastX, firstY, lastY, auxX, auxY;
    firstX = element[firstChromosome * 3];
    firstY = element[firstChromosome * 3 + 1];

    lastX = element[lastChromosome * 3];
    lastY = element[lastChromosome * 3 + 1];

    double acum = 0;
    double distance = 0;
    double auxVal = 0;



    for (int otherChromosome= firstChromosome+1; otherChromosome < numChromosomes; otherChromosome +=1 ){
            auxX = element[otherChromosome * 3];
            auxY = element[otherChromosome * 3 + 1];
            distance = sqrt ( pow((double)( firstX-auxX ),2) + pow((double)(firstY - auxY),2));
            auxVal = besselFunction( distance);
            acum += auxVal;
            //printf("(%d / %d): FIRST distance between vortice %d (%d, %d) and vortice %d (%d, %d) is %f, bessel is %f, acum is %f\\n",
            //    firstChromosome, numChromosomes, firstChromosome, firstX,firstY,otherChromosome, auxX,auxY, distance,auxVal, acum);
    }

    if (firstChromosome != lastChromosome){ //avoid error with 3 chromosomes
        for (int otherChromosome= lastChromosome+1; otherChromosome < numChromosomes; otherChromosome +=1 ){
                auxX = element[otherChromosome * 3];
                auxY = element[otherChromosome * 3 + 1];
                distance = sqrt ( pow((double)( lastX-auxX ),2) + pow((double)(lastY - auxY),2));
                auxVal = besselFunction( distance);
                acum += auxVal;
                //printf("(%d / %d): LAST distance between vortice %d (%d, %d) and vortice %d (%d, %d) is %f, bessel is %f, acum is %f\\n",
                //    firstChromosome, numChromosomes, lastChromosome, firstX,firstY,otherChromosome, auxX,auxY, distance,auxVal, acum );
        }
    }



     if (anclajesInfluence) {
        for (int anclajePosition = 0; anclajePosition < numAnclajes; anclajePosition +=1){
            auxX = anclajesList[anclajePosition][0];
            auxY = anclajesList[anclajePosition][1];

            //we calculate interactions with both Chromosomes to avoid accesing the whole list twice
            distance = sqrt ( pow((double)( firstX-auxX ),2) + pow((double)(firstY - auxY),2));
            if (distance < 100) {
                auxVal = 1.0/200 * distance;
                acum += auxVal;
                //printf("(%d / %d): FIRST: distance between vortice %d (%d, %d) and anclaje (%d, %d) is %f, STEP FUNCTION is %f,  acum is %f\\n", firstChromosome, numChromosomes, firstChromosome, firstX,firstY,auxX,auxY, distance, auxVal, acum);
                }

            distance = sqrt ( pow((double)( lastX-auxX ),2) + pow((double)(lastY - auxY),2));
            if ((distance < 100) and (firstChromosome != lastChromosome)){ //avoid error with 3 chromosomes
                auxVal = 1.0/200 * distance;
                acum += auxVal;
                //printf("(%d / %d): LAST: distance between vortice %d (%d, %d) and anclaje (%d, %d) is %f, STEP FUNCTION is %f, acum is %f\\n", firstChromosome, numChromosomes, lastChromosome, lastX,lastY,auxX,auxY, distance, auxVal, acum);
                }



            }
        }
    solution[firstChromosome] = acum;
    }

""")



'''
the number of computational units to execute is the number of elements * max number of neighbors. Every thread computes a neighbor.

the max possible number of threads is 512

thus, if a lot of particles are being simulated,  every thread must compute more than 1 neighbor. This is done by the so-called "groups"
'''



def calculateBesselValue(geometry, elementList, anclajeListNumpy, anclajesInfluence):
    
    auxList = elementList[0:ceil(len(elementList)/2)]
    numberOfCores=len(auxList)

    oneBesselValueGPU=numpy.zeros(numberOfCores, dtype='double')
    oneBesselValueCUDA = mod.get_function("oneBesselValueCUDA")

    oneBesselValueCUDA(drv.In(elementList),
                                drv.In(anclajeListNumpy),
                                numpy.int32(len(anclajeListNumpy)),
                                numpy.int32(len(elementList)),
                                numpy.int32(anclajesInfluence), #esto es en realidad boolean, pero pasandolo como int funciona mejor el CUDA (no casca)
                                drv.Out(oneBesselValueGPU),
                                block=(numberOfCores,1,1))

    besselValue = sum( item for item in oneBesselValueGPU)
    
    besselValue = besselValue * const.f_0
    
    return besselValue

def loadBesselValues():
    besselValuesHardCodedD,_ = mod.get_global("besselValuesHardCoded")
    drv.memcpy_htod(besselValuesHardCodedD, besselValuesHardCoded)
