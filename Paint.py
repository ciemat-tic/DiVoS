'''
Created on 04/11/2013

@author: supermanue
'''

import os, sys
import re
import numpy

from Individual import Individual
from squareGeometryMatrix import squareGeometryMatrix
from Chromosome import Chromosome


if __name__ == '__main__':
    
    if len(sys.argv) == 1: 
        dirToExplore = "/home/mrodriguez/DiVoS_genetic/results"
    else:
        dirToExplore = sys.argv[1]
    
    r1 = re.compile(r"txt$")
    for dirname, dirnames, filenames in os.walk(dirToExplore):
        for filename in filenames:
            
            #if it's a txt, paint it
            
            #if it finishes with a number, it's part of a GIF. Paint every image separately and then join all of them
            if r1.search(filename):
                fullFileName = os.path.join(dirname, filename)
                
                simulationParameters = filename.split("_")
                
                xSize = int(simulationParameters[2])
                ySize = int(simulationParameters[3])
                multiplicity = int(simulationParameters[4])
                
                
                myFile = open(fullFileName, 'r')
                
                elementList = []
                myGeometry = squareGeometryMatrix(xSize, ySize, multiplicity)
                energy=0
                
                for line in myFile.readlines():
                    if line.startswith("besselValue"):
                        besselValue = line.split(":")[1]
                        continue
                    if not line[0].isdigit(): #skip rest of info
                        continue
                    
                    line= re.sub('[(){}<>]', '', line)
                    line = line.strip()
                    xVal,yVal = line.strip().split(" ")
                
                    aux = Chromosome(xVal, yVal, -1)
                
                    elementList.append(aux)
                
                print ("painting " + fullFileName+ ".png")
                auxIndividual = Individual (myGeometry,myGeometry.getAnclajesListNumpy(),True,True, 1)
                auxIndividual.chromosomes = elementList
                auxIndividual.besselValue = besselValue
                
                
                auxIndividual.paint(fullFileName+ ".png")
                

        for myDir in dirnames:
            fullDir = dirToExplore + "/" + myDir + "/"
            gifName = os.path.join(fullDir, "evolution.gif")
            command = "/usr/bin/convert -delay 20 -layers Optimize "+ fullDir + "*png " + gifName
            print ("GENERATE GIF: " )
            print (command)

            command = "python gprof2dot.py -f pstats " + fullDir + "*profile | dot -Tpng -o " + fullDir + "profile1.png"
            print ("GENERATE PROFILE")
            print (command)


