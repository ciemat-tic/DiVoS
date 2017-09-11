'''
Created on 11 ago. 2017

@author: Administrador
'''
import glob
import sys
from squareGeometryMatrix import squareGeometryMatrix
from triangleGeometryMatrix import triangleGeometryMatrix

from Individual import Individual
from Chromosome import Chromosome


#files = glob.glob( 'results/*.txt' )
files = glob.glob(sys.argv[1])
for myFile in files:
    print ("painting file " + myFile)
    f = open(myFile,'r')
    a = f.readlines()

    multiplicity = int(a[6].split(':')[1])
    geometry = a[7].split(':')[1].strip()
    xSize = int(a[8].split(':')[1])
    ySize = int(a[9].split(':')[1])
    energy = float(a[11].split(':')[1])

    if geometry=="square":
        geometry = squareGeometryMatrix(xSize, ySize, multiplicity)
    else:
        geometry = triangleGeometryMatrix(xSize, multiplicity)

    chromosomeList=[]
    for line in a[14:]:
        try:
            newChromosome = Chromosome(int(line.split()[0]), int(line.split()[1]), 1)
            chromosomeList.append(newChromosome)
        except:
            pass

    numpyAnclajeList = geometry.getAnclajesListNumpy()
    myindividual = Individual(geometry, numpyAnclajeList, False,  False, 1)
    myindividual.chromosomes = chromosomeList
    myindividual.besselValue = energy

    outputFileName = myFile[:-4] + ".png"
    myindividual.paint(outputFileName)
    print ("    OK DONE")
