# Use python 3.0 syntax
from  __future__  import  division,  print_function
import numpy
from math import sqrt, pow
from scipy.special import kv as kv
import itertools
import logging
import const

besselValues = {}

def besselFunction(chromosomeA, chromosomeB):
    if numpy.array_equal(chromosomeA,chromosomeB):
        return 0

    distanceSqr = (chromosomeA[0] - chromosomeB[0]) ** 2 + \
            (chromosomeA[1] - chromosomeB[1]) ** 2
    try:
        solution = besselValues[distanceSqr]
    except:
        distance = sqrt(distanceSqr) / const.lammda
        solution = kv(0,distance)
        besselValues[distanceSqr] = solution
    return solution


def pinningForce (chromosome, anclaje):
    distance = sqrt((chromosome[0]-anclaje[0]) ** 2 + (chromosome[1]-anclaje[1]) ** 2)
    auxVal=0
    if distance < const.min_distance:
        auxVal = 1.0/200 * distance;
    return auxVal
        
     

def calculateBesselValue(geometry, elementList, anclajeListNumpy, anclajesInfluence):
    acumtest = 0

    for i in range(len(elementList)-1):
        for j in range(i+1, len(elementList)):
            acumtest +=besselFunction (elementList[i], elementList[j])

    if anclajesInfluence:
        anclajesEnergy = sum(
                    [pinningForce(oneChromosome, oneAnclaje)
                    for oneChromosome in elementList
                    for oneAnclaje in anclajeListNumpy])
        acumtest += anclajesEnergy

    acumtest = acumtest * const.f_0
    return acumtest



 



