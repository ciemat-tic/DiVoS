'''
Created on 24/02/2015

@author: supermanue
'''

# Use python 3.0 syntax
from  __future__  import  division,  print_function

import pylab
import matplotlib.pyplot as plt
import numpy
from Chromosome import Chromosome
from timeit import itertools
try:
    from GPUFunctions import calculateBesselValue as calculateBesselValueFromLib
except:
    from CPUFunctions import calculateBesselValue as calculateBesselValueFromLib


from math import ceil, sqrt
import sys

import const
import logging
logger = logging.getLogger(__name__)



class Individual(object):
    '''
    classdocs
    '''



    def __initNoRandom__(self, geometry, numpyAnclajeList, anclajesInfluence, totallyRandomInicialization, numChromosomes, mytype=const.RANDOM_INDIVIDUAL):
        '''
        Constructor
        '''
        self.besselValue = -1
        self.lifetime = 0
        self.geometry = geometry
        self.numpyAnclajeList = numpyAnclajeList
        self.anclajesInfluence = anclajesInfluence
        self.chromosomes = []
        self.totallyRandomInicialization = totallyRandomInicialization
        self.numChromosomes = numChromosomes
        self.mytype = mytype

        #we put all the chromosomes in the center of the square
        centerX = int(self.geometry.xSize / 2)
        centerY = int(self.geometry.ySize / 2)

        #particles will be in a (particleOffset, particuleOffset) square.
        #so half of them are on the left, half on the right, and so
        particlesOffset = int ( sqrt(self.numChromosomes) / 2)

        for xPos, yPos in  itertools.product(range (self.geometry.multiplicity),range (self.geometry.multiplicity)):

            xOffset = xPos * self.geometry.xSize
            yOffset = yPos * self.geometry.ySize

            counter = 0 #this is for situations where the number of chromosomes is not a power of 2
            for x, y  in itertools.product((centerX - particlesOffset, centerX + particlesOffset), (centerY - particlesOffset, centerY + particlesOffset)):
                newChromosome = Chromosome(x + xOffset, y + yOffset,1)
                self.chromosomes.append(newChromosome)
                counter+=1
                if counter >= numChromosomes:
                    break;

        self.besselValue = self.calculateBesselValue()




    def __init__(self, geometry, numpyAnclajeList, anclajesInfluence, totallyRandomInicialization, numChromosomes, mytype=const.RANDOM_INDIVIDUAL):
        '''
        Constructor
        '''

        self.besselValue = -1
        self.lifetime = 0
        self.geometry = geometry
        self.numpyAnclajeList = numpyAnclajeList
        self.anclajesInfluence = anclajesInfluence
        self.chromosomes = []
        self.totallyRandomInicialization = totallyRandomInicialization
        self.numChromosomes = numChromosomes
        self.mytype = mytype

        for xPos in range (self.geometry.multiplicity):
            for yPos in range (self.geometry.multiplicity):
                for counter in range (numChromosomes):
                    if self.totallyRandomInicialization:
                        self.__addOptimizedRandomChromosome()
                    else:
                        self.__addOptimizedRandomChromosome(xPos, yPos)


    def __eq__(self, other):
        for x,y in zip(self.chromosomes, other.chromosomes):
            if x!=y:
                return False
        return True



    #this  function crates a random chromosome, supposed to be better than a snadard random generation
    #to do so, it creates three random ones, and then picks the one uits better to the problem solution
    def __addOptimizedRandomChromosome(self, xPos=None, yPos=None):

        #egt three chromosomes that do not collide with the existing ones
        auxChromosomes = []
        while len(auxChromosomes) < 3:
            collision = True
            while collision:
                collision = False
                auxChromosome = self.geometry.getRandomInnerChromosome(xPos, yPos)
                for choromosome in self.chromosomes:
                    if auxChromosome.x == choromosome.x and auxChromosome.y == choromosome.y:
                        collision = True
                        break
                for choromosome in auxChromosomes:
                    if auxChromosome.x == choromosome.x and auxChromosome.y == choromosome.y:
                        collision = True
                        break
            auxChromosomes.append(auxChromosome)

        #now choose the best one

        bestValue = sys.maxsize
        bestChromosome=None

        #ponemos un cromosoma, miramos el valor y lo quitamos. Almacenamos el mejor
        for ind in auxChromosomes:
            self.chromosomes.append(ind)
            currentValue = self.calculateBesselValue()
            if currentValue < bestValue:
                bestChromosome=ind
                bestValue = currentValue
            self.chromosomes.pop()
        self.chromosomes.append(bestChromosome)
        self.besselValue = bestValue



    def clone(self):
        #number of chromosomes is set to Zero to avoid creating a new chromosome list, initializing it and calculating its bessel value
        newIndividual = Individual(self.geometry, self.numpyAnclajeList, self.anclajesInfluence, self.totallyRandomInicialization, 0)
        newIndividual.numChromosomes = self.numChromosomes
        newIndividual.besselValue = self.besselValue
        newIndividual.mytype = self.mytype
        newChromosomeList = []

        for chromosome in self.chromosomes:
            newChromosomeList.append(Chromosome(chromosome.x, chromosome.y, chromosome.energy))
        newIndividual.chromosomes = newChromosomeList

        return newIndividual


    def printIndividual(self):

        #------------------------------------------------------------- auxStr=""
        #----------------------------------- for chromosome in self.chromosomes:
            # auxStr+= str(int(chromosome.x)) + " " + str(int(chromosome.y)) + " , "
        #--------------------------------------------------------- return auxStr

        auxStr = ""

        auxStr += "multiplicity: " + str(self.geometry.multiplicity)+ "\n"
        auxStr += "geometry: " + str(self.geometry.name)+ "\n"
        auxStr += "geometry.xSize: " + str(self.geometry.xSize)+ "\n"
        auxStr += "geometry.ySize: " + str(int(self.geometry.ySize))+ "\n"
        auxStr+="size: "+str(len(self.chromosomes)) + "\n"
        auxStr+="besselValue: "+str(self.besselValue) + "\n"
        auxStr+="type: " + str(self.mytype) + "\n"
        auxStr+="lifetime: " + str(self.lifetime) + "\n"

        for chromosome in self.chromosomes:
            auxStr+= str(int(chromosome.x)) + " " + str(int(chromosome.y)) + "\n"


        return auxStr


    def calculateBesselValue(self):
        #NOTE THAY ELEMENT_LIST HAS TO BE A NUMPY ARRAY HERE
        numpyChromosomes = self.chromosomesToNumpyArray()
        self.besselValue = calculateBesselValueFromLib(self.geometry, numpyChromosomes, self.numpyAnclajeList, self.anclajesInfluence)
        return self.besselValue


    #Return True is there has been any improvement, False if not
    def improve(self):
        functionLogger = logger.getChild("improve")
        #functionLogger.setLevel(logging.DEBUG)
        functionLogger.debug ("START IMPROVE METHOD")
        isLocalMin=True

        for chromosomeToMutate in self.chromosomes:
            neighbors = self.geometry.getNeighbors(chromosomeToMutate, self.chromosomes)
            for newchromosome in neighbors:
                newIndividual = self.clone()
                newIndividual.changeChromosome(chromosomeToMutate, newchromosome)
                if newIndividual.besselValue < self.besselValue:
                    functionLogger.debug("there was improvement")
                    self.chromosomes = newIndividual.chromosomes
                    self.besselValue = newIndividual.besselValue
                    isLocalMin = False

        return not(isLocalMin)


    #replace and old chromosomoe by a existing one.

    #TODO test comparison
    def changeChromosome(self, oldElement, newElement):
        functionLogger = logger.getChild("changeChromosome")
        functionLogger.debug("cambio el (" + str(oldElement.x) + "," + str(oldElement.y) + ") por (" + str(newElement.x) + "," + str(newElement.y) + ")")

        newChromosomeList = []
        for element in self.chromosomes:
            if element == oldElement:
                newChromosomeList.append(newElement)
            else:
                newChromosomeList.append(element)

        self.chromosomes = newChromosomeList
        self.calculateBesselValue()



    def rotate(self):
        #return geometry.mutateOnRectangle(individual)
        self.geometry.rotateRectangle(self.chromosomes)
        self.calculateBesselValue()


    def mutate(self):
        functionLogger = logger.getChild("mutate")
        #=======================================================================
        # functionLogger.setLevel(logging.DEBUG)
        #=======================================================================


        #REMOVE 30% OF THE CHROMOSOMES AND REPLACE THEM WITH OTHERS
        chromosomesToMutate = int(ceil(len(self.chromosomes) / 3))

        functionLogger.debug("I am going to mutate " + str (chromosomesToMutate) + " elements")
        functionLogger.debug(self.printIndividual())

        self.chromosomes[:] = self.chromosomes[:-chromosomesToMutate]

        for i in range(chromosomesToMutate):
            self.__addOptimizedRandomChromosome()
            self.calculateBesselValue() #this already adds bessel value, so there is no need of doing it again (as in the rotation)

        functionLogger.debug("After mutation")
        functionLogger.debug(self.printIndividual())
        functionLogger.debug("Ok, done")


    def paint(self, outputFile=None):
        strechFactor = self.geometry.xSize  / self.geometry.ySize
        #this ugly hack breaks polymorphism and should be avoided at any cost. But yet again...
        if self.geometry.name=="triangle":
            strechFactor = strechFactor/2
        figSizeX=  self.geometry.multiplicity
        figSizeY = (int)(figSizeX / strechFactor)

        fig = pylab.figure(1,figsize=(figSizeX, figSizeY), dpi=80)
        ax = fig.add_subplot(111)
        ax.grid(True)
        ax.set_title("my Taylor is Rich")
        ax.set_xlabel("My Taylor")
        ax.set_ylabel("is Rich")
        ax.axis([0, self.geometry.xSize * self.geometry.multiplicity, 0, self.geometry.ySize * self.geometry.multiplicity])

        manager = pylab.get_current_fig_manager()

        anclajesXArray = []
        anclajesYArray = []

        plt.clf()

        for anclajeRow in self.geometry.getAnclajesList():
            for anclaje in anclajeRow:
                anclajesXArray.append(anclaje.x)
                anclajesYArray.append(anclaje.y)

        plt.plot(anclajesXArray, anclajesYArray, 'bo', markersize=15)

        elementsXArray=[]
        elementsYArray=[]


        for element in self.chromosomes:
            elementsXArray.append(element.x)
            elementsYArray.append(element.y)

        plt.title("Energy: " + str (self.besselValue))
        plt.xlabel("X position")
        plt.ylabel("Y position")

        plt.plot(elementsXArray, elementsYArray, 'ro', markersize=5)


        plt.draw()
        if outputFile != None:
            plt.savefig(outputFile)




    def make_hash(self):
        return self.__make_hash(self)


    def __make_hash(self, element):
        if isinstance(element, list):
            return tuple([self.__make_hash(e) for e in element])
        else:
            return hash(element)



#########################################
#########################################
# FROM HERE, AUX FUNCTIONS FOR GPU-RELATED OPPERATIONS


    def chromosomesToNumpyArray(self):
        numpyElements=numpy.zeros([len(self.chromosomes),3], dtype='int32')
        cont = 0
        for elem in self.chromosomes:
            numpyElements[cont,0] = elem.x
            numpyElements[cont,1] = elem.y
            numpyElements[cont,2] = elem.energy

            cont +=1
        return numpyElements


        numpyAnclajeList=numpy.zeros([cont,3], dtype='int32')
        cont = 0
        for anclajeRow in self.anclajeList:
            for anclaje in anclajeRow:
                numpyAnclajeList[cont][0] = anclaje[0]
                numpyAnclajeList[cont][1] = anclaje[1]
                numpyAnclajeList[cont][2] = anclaje[2]
                cont+=1

        return numpyAnclajeList





#we convert the existing data structures into an one-dimensional array
#to feed the GPU

#allElements contains all the possible mutations for every element.
#thus, in the first postiton we find the possible mutations to the first chromosome, and so
def allCombinationsToNumpyArray(allElements, elementList):

    maxNeighbors = 0
    for neighborList in allElements:
        maxNeighbors = max (maxNeighbors, len(neighborList))


    numpyElements=numpy.zeros([len(elementList), maxNeighbors, len(elementList),3], dtype='int32')


    positionBeingMutated = 0
    for neighborGroup in allElements:
        mutationNumber = 0
        for neighborBeingMutated in neighborGroup:
            #copy everything, then replace the element to mutate
            for elemPosition in range(len(elementList)):
                numpyElements[positionBeingMutated,mutationNumber,elemPosition,0]= elementList[elemPosition].x
                numpyElements[positionBeingMutated,mutationNumber,elemPosition,1] = elementList[elemPosition].y
                numpyElements[positionBeingMutated,mutationNumber,elemPosition,2] = elementList[elemPosition].energy

                if elemPosition==positionBeingMutated:
                    numpyElements[positionBeingMutated,mutationNumber,elemPosition, 0] = neighborBeingMutated.x
                    numpyElements[positionBeingMutated,mutationNumber,elemPosition,1] = neighborBeingMutated.y
                    numpyElements[positionBeingMutated,mutationNumber,elemPosition,2] = neighborBeingMutated.energy

            mutationNumber +=1
        positionBeingMutated +=1

    return numpyElements

def __make_hash(myobject):
    if isinstance(myobject, list):
        return tuple([e.make_hash() for e in myobject])
    else:
        return hash(myobject)
