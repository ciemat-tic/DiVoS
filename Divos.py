'''
Created on 07/10/2013

@author: supermanue
'''
from __future__ import division

import random
from Individual import *

from squareGeometryMatrix import squareGeometryMatrix
from triangleGeometryMatrix import triangleGeometryMatrix
import cProfile
import os, sys, itertools
import const
import logging
from math import exp
import datetime
from scipy.optimize import basinhopping
import time

try: 
    import GPUFunctions 
except:
    pass
    
    
def simmulatedAnnealing(population):
    functionLogger = logger.getChild("simmulatedAnnealing")
    functionLogger.setLevel(logging.DEBUG)


    ###########
    ###########
    # ALGORITHM INITIALIZATION
    best_solution = old_solution = population[0]  #TODO IMPLEMENTING IT FOR A SINGLE ELEMENT, THEN PARALELIZE
    T = constants.annealingTemperature

    length=constants.annealingLength

    tempfunc = lambda temp: 0.8*temp
    iterfunc = lambda length: (int)(ceil(1.05*length))
    epochs=constants.annealingEpoch
    populationSize = len(population)

    ###########
    ###########
    #PARALELIZATION

    functionLogger.debug("SIMMULATED ANNEALING ALGORITHM")
    functionLogger.debug("Exporting information to all threads")
    functionLogger.debug("")

    ###########
    ###########
    # ALGORITHM IMPLEMENTATION (adapted to this problem)
    for index in range(epochs):
        functionLogger.debug("Epoch: " + str(index))
        if index > 0:
            T = tempfunc(T)
            length=iterfunc(length)
        for it in range(length):
            for i in range(len(population)):
                new_solution = population[i].clone()

                #change one chromosome
                oldElement = random.choice(new_solution.chromosomes)
                newElement = new_solution.geometry.getRandomInnerChromosome()
                new_solution.changeChromosome(oldElement, newElement)

                # Use a min here as you could get a "probability" > 1
                # Take care of the minus symbol change
                # original function: gamma = min(1, exp((auxIndividuals[i].besselValue - new_solution.besselValue)/T))

                try:
                    diff = (population[i].besselValue - new_solution.besselValue)
                    gamma = min(1, exp(diff/T))
                except: 
                    functionLogger.info("Simulated annealing interrupted")
                    functionLogger.info("Temperature is too small:" + str(T))
                    return 

                if (population[i].besselValue > new_solution.besselValue):
                    # Accept proposed solution
                    population[i] = new_solution
                elif random.uniform(0,1) < gamma:
                    population[i] = new_solution
                if ((population[i].besselValue > new_solution.besselValue) or (random.uniform(0,1) < gamma)):
                    population[i] = new_solution

        cleanAndSort(population)
        functionLogger.info("Best individual is")
        functionLogger.info(population[0].printIndividual())
    functionLogger.info("End of simmulated annealing")


def _randomStep(individual):
    #change one chromosome
    oldElement = random.choice(individual.chromosomes)
    newElement = individual.geometry.getRandomInnerChromosome()
    individual.changeChromosome(oldElement, newElement)
        
        
def basin_hopping(population):
    temperature = constants.basinTemperature
    length = constants.basinLength
    for i in range(len(population)):
        basinhopping(population[i].calculateBesselValue(), population[i], niter=length, T=temperature, take_step=_randomStep)
    return population

def geneticAlgorithm(population):
    functionLogger = logger.getChild("geneticAlgorithm")
    #===========================================================================
    #functionLogger.setLevel(logging.DEBUG)
    #===========================================================================

    functionLogger.debug("GENETIC ALGORITHM")

    auxPopulation=[]
    for child1,child2 in  itertools.product(population,population):
        if child1 == child2:
            continue;

        if random.random() < constants.geneticCROSSOVER_PROBABILITY:
            son = child1.clone()
            son.mytype = const.CROSSOVER_INDIVIDUAL
            randomChromosomeToInsert = random.choice(child2.chromosomes)

            if not randomChromosomeToInsert in son.chromosomes:
                functionLogger.debug("crossover")
                randomChromosomeToRemove = random.choice(son.chromosomes)
                son.changeChromosome(randomChromosomeToRemove,randomChromosomeToInsert)
                auxPopulation.append(son)

                population_stats[const.CROSSOVER_INDIVIDUAL]['creation']+=1

    #Mutate elements
    for element in population:
        if random.random() < constants.geneticMUTATION_PROBABILITY:
            functionLogger.debug("mutation")
            mutant = element.clone()
            mutant.mytype = const.MUTATION_INDIVIDUAL
            mutant.mutate()
            auxPopulation.append(mutant)
            population_stats[const.MUTATION_INDIVIDUAL]['creation']+=1

    #Rotate elements
    for element in population:
        if random.random() < constants.geneticROTATION_PROBABILITY:
            functionLogger.debug("rotation")
            rotant = element.clone()
            rotant.mytype = const.ROTATION_INDIVIDUAL
            rotant.rotate()
            auxPopulation.append(rotant)
            population_stats[const.ROTATION_INDIVIDUAL]['creation']+=1

    population+=auxPopulation

def greedyAlgorithm(population):
    functionLogger = logger.getChild("greedyAlgorithm")
    #functionLogger.setLevel(logging.DEBUG)
    functionLogger.debug("GREEDY ALGORITHM")

    for individual in population:
        functionLogger.debug ("before improvement")
        functionLogger.debug(individual.printIndividual())
        individual.improve()
        individual.lifetime +=1
        functionLogger.debug("AFTER improvement")
        functionLogger.debug(individual.printIndividual())

def cleanAndSort(population):
    functionLogger = logger.getChild("cleanAndSort")
    #===========================================================================
    # functionLogger.setLevel(logging.DEBUG)
    #===========================================================================

    functionLogger.debug("sort and remove duplicates ")


    #===========================================================================
    # Remove duplicates, keeping the one with higher lifetime
    #===========================================================================

    auxPopulation =[]

    for individual in population:
        auxIndividual=individual
        alreadyExists=False
        for individual2 in auxPopulation:
            if individual == individual2:
                alreadyExists = True
                if individual.lifetime >= individual2.lifetime:
                    individual2.lifetime = individual.lifetime
                    individual2.mytype = individual.mytype
                break
        if not alreadyExists:
            auxPopulation.append(auxIndividual)
    population[:] = auxPopulation

    population.sort(key=lambda individual: individual.besselValue)

    functionLogger.debug("after sorting and removing duplicates, population size is " + str(len(population)))
    for individual in population:
        functionLogger.debug(individual.printIndividual())


def removeWorstElements(population):
    functionLogger = logger.getChild("removeWorstElements")
    #===========================================================================
    # functionLogger.setLevel(logging.DEBUG)
    #===========================================================================

    functionLogger.debug("REMOVING WORST ELEMENTS")
    functionLogger.debug("Population length at the begginging of removal: " + str(len(population)))

    cleanAndSort(population)


#===============================================================================
#     for elem in population[constants.population:]:
#
#         population_stats[elem.mytype]['destruction']+=1
#         if population_stats[elem.mytype]['destruction'] == 1:
#             population_stats[elem.mytype]['avg_lifetime'] =elem.lifetime
#         else:
#             population_stats[elem.mytype]['avg_lifetime'] = (population_stats[elem.mytype]['avg_lifetime'] * (population_stats[elem.mytype]['destruction']-1) + elem.lifetime) / population_stats[elem.mytype]['destruction']
#         population.remove(elem)
#===============================================================================


    if len(population) == constants.population:
        return

    functionLogger.debug("Replacing worst elements with the new ones")

    #get the old ones
    oldPopulation = [elem for elem in population if elem.lifetime  > constants.geneticMinIndividualLife]
    newPopulation = [elem for elem in population if elem.lifetime  <= constants.geneticMinIndividualLife]
    if len (newPopulation) < constants.population * constants.geneticFractionOfOldElementsKept:
        elemsToReplace = len (newPopulation)
    else:
        elemsToReplace = int(constants.population * constants.geneticFractionOfOldElementsKept)
    oldElemsToKeep = constants.population - elemsToReplace

    functionLogger.debug("    Old population: " + str(len(oldPopulation)))
    functionLogger.debug("    New population: " + str(len(newPopulation)))
    functionLogger.debug ("Elements to keep from old population: " + str(oldElemsToKeep))
    functionLogger.debug ("Elements to replace from population: " + str(elemsToReplace))



    population[:] = oldPopulation[:oldElemsToKeep]
    population+=newPopulation[:elemsToReplace]


    #===========================================================================
    # STATS ABOUT DELETED ELEMENTS
    #===========================================================================
    for elem in oldPopulation[oldElemsToKeep:]:
        functionLogger.debug("Stats from element " + str(elem.printIndividual()))

        population_stats[elem.mytype]['destruction']+=1
        if population_stats[elem.mytype]['destruction'] == 1:
            population_stats[elem.mytype]['avg_lifetime'] =elem.lifetime
        else:
            population_stats[elem.mytype]['avg_lifetime'] = (population_stats[elem.mytype]['avg_lifetime'] * (population_stats[elem.mytype]['destruction']-1) + elem.lifetime) / population_stats[elem.mytype]['destruction']


    cleanAndSort(population)
    functionLogger.debug("Population length at the end of removal: " + str(len(population)))




def evolution(generation = 1):
    global population
    functionLogger = logger.getChild("evolution")
    #===========================================================================
    # functionLogger.setLevel(logging.DEBUG)
    #===========================================================================
    
    genetico = constants.chooseGenetico
    voraz = constants.chooseVoraz

    if voraz == True:
        greedyAlgorithm(population)
    
    if genetico == True:
        geneticAlgorithm(population)
    removeWorstElements(population)

    functionLogger.info("Best individual is")
    functionLogger.info(population[0].printIndividual())


    functionLogger.debug ("COMPLETE INDIVIDUAL LIST")
    for individual in population:
        functionLogger.debug(individual.printIndividual())
        functionLogger.debug ("---")


def evolutionManager():
    functionLogger = logger.getChild("evolutionManager")
    global population
    
    recocido = constants.chooseRecocido
    basin = constants.chooseBasin
    genetico = constants.chooseGenetico

    if recocido == True:
        simmulatedAnnealing(population)
    if basin == True:
        basin_hopping(population)
    	    
    if genetico == True:
        for generation in range(constants.geneticGenerations):
            functionLogger.info ("------------------------------")
            functionLogger.info ("------------------------------")
            functionLogger.info ("    ITERATION: " + str(generation))
            functionLogger.info ("------------------------------")

            evolution(generation)
            #=======================================================================
            # printStats()
            #=======================================================================







def paintDynamic():

    fig = pylab.figure(1)
    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title("my Taylor is Rich")
    ax.set_xlabel("My Taylor")
    ax.set_ylabel("is Rich")
    ax.axis([0, geometry.xSize * geometry.constants.multiplicity, 0, geometry.ySize * geometry.constants.multiplicity])

    manager = pylab.get_current_fig_manager()

    timer = fig.canvas.new_timer(interval=1)
    #timer.add_callback(self.avanza, self.squareFunction)
    timer.add_callback(evolution)
    timer.start()

    timer2 = fig.canvas.new_timer(interval=1)
    timer2.add_callback(paint)
    timer2.start()

    pylab.show()

def paint():
    global population
    bestIndividual = population[0]
    bestIndividual.paint()

def printStats():
    logger.info ("EVOLUTION STATS")
    logger.info ("    Random individuals created / discarded / lifetime: " + str (population_stats[const.RANDOM_INDIVIDUAL]['creation']) + " / " + str (population_stats[const.RANDOM_INDIVIDUAL]['destruction'])+ " / " + str (population_stats[const.RANDOM_INDIVIDUAL]['avg_lifetime']))
    logger.info ("    Mutation individuals created / discarded / lifetime: " + str (population_stats[const.MUTATION_INDIVIDUAL]['creation']) + " / " + str (population_stats[const.MUTATION_INDIVIDUAL]['destruction'])+ " / " + str (population_stats[const.MUTATION_INDIVIDUAL]['avg_lifetime']))
    logger.info ("    Crossover individuals created / discarded / lifetime: " + str (population_stats[const.CROSSOVER_INDIVIDUAL]['creation']) + " / " + str (population_stats[const.CROSSOVER_INDIVIDUAL]['destruction'])+ " / " + str (population_stats[const.CROSSOVER_INDIVIDUAL]['avg_lifetime']))
    logger.info ("    Rotation individuals created / discarded / lifetime: " + str (population_stats[const.ROTATION_INDIVIDUAL]['creation']) + " / " + str (population_stats[const.ROTATION_INDIVIDUAL]['destruction'])+ " / " + str (population_stats[const.ROTATION_INDIVIDUAL]['avg_lifetime']))

    logger.info ("WINNER STATS")
    cont = 0
    for elem in population:
        logger.info("    " + str(cont) + ": creation / lifetime: " + constants.get_typename(elem.mytype ) + " / " + str(elem.lifetime))


if __name__ == '__main__':
    
    t_initial = int(round(time.time() * 1000))
    #IndividualFunctions.paintDynamic(pop,geometry, evolutionOneStep)

    #===========================================================================
    # mainHandler = logging.StreamHandler()
    # FORMAT=str(rank) + " / " + str(size) + ': %(message)s'
    # formatter = logging.Formatter(FORMAT)
    # mainHandler.setFormatter(formatter)
    # logging.basicConfig(handler=mainHandler)
    #===========================================================================
    logging.basicConfig(level=logging.INFO)
    #asgasg
    #one logger per thread

    logger = logging.getLogger(__name__ + ".0")


    #variables entrada
    #TODO: Leer variables entrada
    constants = const.Const(sys.argv[1])

    if constants.geometry=="square":    
    	geometry = squareGeometryMatrix(constants.maxX, constants.maxY, constants.multiplicity)
    elif constants.geometry=="triangle":
        geometry = triangleGeometryMatrix(constants.maxX, constants.multiplicity)
    else:
        printf("GEOMETRY NOT RECOGNIZED, EXITING")
        sys.exit()
    numpyAnclajeList = geometry.getAnclajesListNumpy()


    #some file naming
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I:%M")
    outputNameRoot = constants.outputFolder + "/" + str(int(round(time.time() * 1000))) 
    #outputNameRoot = constants.outputFolder + "/result" #TODO cambiar para linux
    
    outputTxt   = outputNameRoot + ".txt"
    outputImage = outputNameRoot + ".png"
    
    if not os.path.exists(constants.outputFolder):
        os.makedirs(constants.outputFolder)

    #INIT POPULATION
    population_stats=[]
    for i in range(4):
        auxDict={"creation":0, "destruction": 0, "avg_lifetime":0}
        population_stats.append(auxDict)
    population_stats[const.RANDOM_INDIVIDUAL]['creation']= constants.population


    try: 
        GPUFunctions.loadBesselValues()
    except:
        print ("no need to load bessel values")
    
    #population is initialized in a node, then distributed among all the rest
    population = [Individual(geometry, numpyAnclajeList, constants.anclajesInfluence, constants.totallyRandomInicialization, constants.vortices) for i in range(constants.population)]

    #EJECUCION
    if constants.executionMode=="graphics": #THIS DOES NOT WORK
        #cProfile.runctx('paintDynamic(population, geometry,evolution)', globals(), locals())
        paintDynamic()

    elif constants.executionMode=="profile":
        cProfile.runctx('evolutionManager()', globals(), locals(),outputNameRoot+ "_profile" )
        logger.warn ("Command to print profile: ")
        logger.warn ("python3 gprof2dot.py -f pstats "+  outputNameRoot+ "_profile" + "|  dot -Tjpg -o output.jpg | display output.jpg ")

    elif constants.executionMode=="batch":
        evolutionManager()

    t_final = int(round(time.time() * 1000)) 
    #END OF EXECUTION

    #PRINT BEST INDIVIDUAL
    logger.info("Best individual is")
    logger.info(population[0].printIndividual())
    f = open(outputTxt, 'w')
    f.write("Total execution time is: " + str(t_final-t_initial) + "\n")
    f.write("Simmulated Annealing: " + str(constants.chooseRecocido) + "\n")
    #f.write("Basin Hopping: " + str(constans.chooseBasin) + "\n")
    f.write("Greedy Algorithm: " + str(constants.chooseVoraz) + "\n")
    f.write("Genetic Algorithm: " + str(constants.chooseGenetico) + "\n")
    f.write("Vortices: " + str(constants.vortices) + "\n")
    if constants.chooseGenetico == True: 
        f.write("Generations: " + str(constants.geneticGenerations) + "\n")
    else: 
        f.write("Epoch: " + str(constants.annealingEpoch))
    f.write( population[0].printIndividual() + "\n")
    f.close()

    logger.info ("Stored in " +outputTxt)


    try:
        population[0].paint(outputFile=outputImage)
        logger.info ("paint is disabled")
        logger.info ("Painted in " + outputImage)
    except:
        logger.warn ("Ops!")
        logger.warn ("Could not paint output. To do so, you need a machine with $DISPLAY configured")
        
   
    logger.info ("Total execution time is:" + str(t_final - t_initial) + " ms")
 
