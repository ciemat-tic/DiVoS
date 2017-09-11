'''
Created on 3 ago. 2017

@author: Administrador
'''
# Use python 3.0 syntax
from  __future__  import  division, print_function
from Chromosome import *

from random import randint
from math import radians, sin, cos
import numpy

#esta es igual que una geometria normal pero los datos se almancenan de manera diferente
# (en formato matriz en lugar de lista) y los cromosomas empleados tienen incorporada
#informacion sobre el triangulo en el que estan


#######################3
#
#
#
#  GEOMETRY:
# X : [0..xSize -1]
# so inner chromosomes go from [1 .. xSize -2]
#an important thing is that all squares have a 1 px border. Then, outside border las length 1, but
#inner ones have length 2. This is, all squares are the same, and we just put one together with the next,
#there is no overlapping. So inner x goes like [1.. xSize,2], [xSize+1 ... 2 * xSize-2], ....




import logging 
from bz2 import compress
logger = logging.getLogger(__name__)


class triangleGeometryMatrix(object):
    def __init__ (self, Size, multiplicity):
        self.inclinacion = numpy.sqrt(3)
        self.Size = Size   
        self.xSize = 2 * Size
        self.ySize = Size * self.inclinacion    #Height of the triangle if Size=1 
        self.multiplicity = multiplicity
        self.sides = self.createSides()
        self.horizontals =  self.createHorizontals()
        self.name= "triangle"
        
            
        
    def clone (self, individual):
        cloned = []
        for chromosome in individual:
            new  = Chromosome(chromosome.x, chromosome.y, chromosome.energy)
            cloned.append(new)
        return cloned
        
    
    #devuelve una lista de anclajes 
    def getAnclajesList(self):
        Lista_x1 = [j * self.Size for j in range(2*self.multiplicity+1)[0:2*self.multiplicity+1:2]]
        Lista_x2 = [j * self.Size for j in range(2*self.multiplicity+1)[1:2*self.multiplicity+1:2]]
        Lista_y1 = [int(numpy.floor(j * self.Size * self.inclinacion)) for j in range(self.multiplicity+1)[0:self.multiplicity+1:2]]
        Lista_y2 = [int(numpy.floor(j * self.Size * self.inclinacion)) for j in range(self.multiplicity+1)[1:self.multiplicity+1:2]]
        compressedList = []
        compressedList += [[Chromosome(j,k,0.25)
                            for j in Lista_x1]
                            for k in Lista_y1]
        compressedList += [[Chromosome(j,k,0.25)
                            for j in Lista_x2]
                            for k in Lista_y2]
        return compressedList
    
     
    #devuelve una lista de anclajes en formato numpy. 
    #es un array de cromosomas, estando estos representados en otro array [x, y, energia)
    def getAnclajesListNumpy(self):

        #generamos lista de cromosomas y vemos su longitud       
        listAux = self.getAnclajesList()
        listLen = 0
        for row in listAux:
            listLen += len(row)
            
        anclajesListNumpy=numpy.zeros([listLen,3], dtype='int32')
        cont=0
        for x in range(len(listAux)):
            for y in range(len(listAux[x])):
                anclajesListNumpy[cont][0] = listAux[x][y].x
                anclajesListNumpy[cont][1] = listAux[x][y].y
                anclajesListNumpy[cont][2] = listAux[x][y].energy
                cont+=1

        return anclajesListNumpy

 
    
    
    
    
    #    Crea un diccionario con todos los puntos pertenecientes a aristas
    #    El diccionario asigna a cada x en [0, 2Size] los puntos en los que corta a las rectas 
    #       de 60 grados que forman los triangulos de la malla
    #    Las ecuaciones de las rectas son:
    #        y = inclinacion*x + k*Size*inclinacion         k es una secuencia de numeros pares
    #        y = -inclinacion*x + k*Size*inclinacion         que depende de la multiplicidad
    #
    #    Para hallar los puntos de corte con otras x mayores utilizamos aritmetica modular 

    
    def createSides(self):
        originalLine = {j : [] for j in range(2*self.Size)}
        yLimit = int(numpy.floor(self.Size *self.inclinacion * self.multiplicity))
        for j in originalLine:
            for k in range(self.multiplicity)[0:self.multiplicity:2]:
                y = int(numpy.floor(k*self.inclinacion*self.Size + self.inclinacion*j))
                if y <= yLimit:
                    originalLine[j] += [y]
            for k in range(self.multiplicity+2)[2:self.multiplicity+2:2]:
                y = int(k*self.inclinacion*self.Size - self.inclinacion*j)
                if y <= yLimit:
                    if y not in originalLine[j]:
                        originalLine[j] += [y]
            originalLine[j].sort() 
        return originalLine    
    
    def createHorizontals(self):
        horizontalLine = [int(numpy.floor(j * self.Size * self.inclinacion)) for j in range(self.multiplicity+1)]
        return horizontalLine
    #    Devuelve True si el cromosoma pisa un lado y False si no pisa
    
    def isSide(self,xPos,yPos):
        if yPos in self.sides[xPos%self.xSize]:
            return True

        
    def isHorizontal(self,yPos):
        if yPos in self.horizontals:
            return True
        
    
       #crea un cromosoma aleatorio en cada triangulo. Es interior, o sea de energia 1.
    #Si no dices nada lo crea donde quiere, o tb se puede especificar un triangulo
    
    def getRandomInnerChromosome(self, xPos=None, yPos=None):
        functionLogger = logger.getChild("getRandomInnerChromosome")
        #---------------------------------------- logger.setLevel(logging.DEBUG)
        
        if xPos == None:
            minX = 1
            maxX = self.multiplicity * self.xSize -2
        else:
            minX = xPos * self.xSize + 1 
            maxX = (xPos + 1) * self.xSize -2
        
        if yPos == None:
            minY = 1
            maxY = int(numpy.floor(self.multiplicity * self.ySize)) 
            newX = 0
            newY = 0
            while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                newX = randint(minX, maxX)
                newY = randint(minY, maxY)
        elif yPos%2 == 0 and xPos%2 == 0:
            minY = int(numpy.floor( yPos * self.ySize)) 
            newX = 0
            newY = 0
            while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                newX = randint(minX, maxX)
                if newX%self.xSize < self.Size:
                    newY = randint(minY, int(numpy.floor( yPos * self.ySize + newX%self.xSize * self.inclinacion))) 
                else: 
                    newY = randint(minY, int(numpy.floor( (yPos +2) * self.ySize - newX%self.xSize * self.inclinacion)))    
        elif yPos%2 == 0 and xPos%2 == 1:
            maxY = int(numpy.floor( (yPos+1) * self.ySize)) 
            newX = 0
            newY = 0
            while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                newX = randint(minX, maxX)
                if newX%self.xSize < self.Size:
                    newY = randint(int(numpy.floor( yPos * self.ySize + newX%self.xSize * self.inclinacion)), maxY)
                else:
                    newY = randint(int(numpy.floor( (yPos +2) * self.ySize - newX%self.xSize * self.inclinacion)), maxY)    
        elif yPos%2 == 1 and xPos%2 == 0:
            maxY =  int(numpy.floor( (yPos+1) * self.ySize)) 
            newX = 0
            newY = 0
            while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                newX = randint(minX, maxX)    
                if newX%self.xSize < self.Size:
                    newY = randint(int(numpy.floor( (yPos +1) * self.ySize - newX%self.xSize * self.inclinacion)), maxY)
                else:
                    newY = randint(int(numpy.floor( (yPos -1) * self.ySize + newX%self.xSize * self.inclinacion)), maxY)
        elif yPos%2 == 1 and xPos%2 == 1:
            minY = int(numpy.floor( yPos * self.ySize)) 
            newX = 0
            newY = 0
            while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                newX = randint(minX, maxX)   
                if newX%self.xSize < self.Size:
                    newY = randint(minY, int(numpy.floor( (yPos +1) * self.ySize - newX%self.xSize * self.inclinacion)))    
                else:
                    newY = randint(minY, int(numpy.floor( (yPos -1) * self.ySize + newX%self.xSize * self.inclinacion)))    
             
        functionLogger.debug("(" + str(newX) + " , " + str(newY) + ")")

        return Chromosome(newX, newY, 1)


    #Crea un cromosoma por triangulo dada una lista de cromosomas existentes

    def getInnerChromosomeForEachTriangle(self, existingChromosomes):
        functionLogger = logger.getChild("getInnerChromosomeForEachTriangle")
        #=======================================================================
        # functionLogger.setLevel(logging.DEBUG)
        #=======================================================================
    
        resultList=[]
        for xPos in range(2*self.multiplicity):
            minX = xPos * self.xSize + 1 
            maxX = (xPos + 1) * self.xSize -2
            for yPos in range(self.multiplicity):      
                validChromosome = False
                while not validChromosome: 
                    validChromosome = True
                    if yPos%2 == 0 and xPos%2 == 0:
                        minY = int(numpy.floor( yPos * self.ySize))
                        newX = 0
                        newY = 0
                        while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                            newX = randint(minX, maxX)
                            if newX%self.xSize < self.Size:
                                newY = randint(minY, int(numpy.floor( yPos * self.ySize + (newX%self.xSize) * self.inclinacion))) 
                            else: 
                                newY = randint(minY, int(numpy.floor( (yPos +2) * self.ySize - (newX%self.xSize) * self.inclinacion)))    
                    elif yPos%2 == 0 and xPos%2 == 1:
                        maxY = int(numpy.floor( (yPos+1) * self.ySize)) 
                        newX = 0
                        newY = 0
                        while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                            newX = randint(minX, maxX)
                            if newX%self.xSize < self.Size:
                                newY = randint(int(numpy.floor( yPos * self.ySize + (newX%self.xSize) * self.inclinacion)), maxY)
                            else:
                                newY = randint(int(numpy.floor( (yPos +2) * self.ySize - (newX%self.xSize) * self.inclinacion)), maxY)    
                    elif yPos%2 == 1 and xPos%2 == 0:
                        maxY =  int(numpy.floor( (yPos+1) * self.ySize)) 
                        newX = 0
                        newY = 0
                        while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                            newX = randint(minX, maxX)    
                            if newX%self.xSize < self.Size:
                                newY = randint(int(numpy.floor( (yPos +1) * self.ySize - (newX%self.xSize) * self.inclinacion)), maxY)
                            else:
                                newY = randint(int(numpy.floor( (yPos -1) * self.ySize + (newX%self.xSize) * self.inclinacion)), maxY)
                    elif yPos%2 == 1 and xPos%2 == 1:
                        minY = int(numpy.floor( yPos * self.ySize)) 
                        newX = 0
                        newY = 0
                        while self.isSide(newX,newY) == True or self.isHorizontal(newY) == True:
                            newX = randint(minX, maxX)   
                            if newX%self.xSize < self.Size:
                                newY = randint(minY, int(numpy.floor( (yPos +1) * self.ySize - (newX%self.xSize) * self.inclinacion)))    
                            else:
                                newY = randint(minY, int(numpy.floor( (yPos -1) * self.ySize + (newX%self.xSize) * self.inclinacion))) 
                    newChromosome = Chromosome(newX, newY, 1)
                    
                    for existingChromosome in  existingChromosomes:
                        if existingChromosome.x == newChromosome.x and \
                            existingChromosome.y == newChromosome.y:
                            validChromosome = False
                print(newX,newY)    
                functionLogger.debug("(" + str(newChromosome.x) + " , " + str(newChromosome.y) + ")")
                resultList.append(newChromosome)
        return resultList

    #### Neighbours
    
    def leftNeighbour(self, myChromosome):
        newX = myChromosome.x -1
        pisa = self.isSide(newX%self.Size,myChromosome.y)
        if newX == 0:
            return None
        elif pisa == True:
            newX -= 2   
        return Chromosome(int(newX), myChromosome.y, myChromosome.energy)

    def rightNeighbour(self, myChromosome):
        newX = myChromosome.x +1
        pisa = self.isSide(newX%self.Size,myChromosome.y)
        if newX == self.xSize * self.multiplicity-2: 
            return None
        elif pisa == True:
            newX += 2  
        return Chromosome(int(newX), myChromosome.y, myChromosome.energy)

    def upNeighbour(self, myChromosome):
        newY = myChromosome.y +1
        pisa = self.isSide(myChromosome.x%self.Size,newY)
        pisa_hor = self.isHorizontal(newY)
        if newY == self.ySize * self.multiplicity -1:
            return None
        elif pisa_hor == True or pisa == True:
            newY += 2   
        return Chromosome(myChromosome.x, int(newY), myChromosome.energy)
    
    def downNeighbour(self, myChromosome):
        newY = myChromosome.y -1
        pisa = self.isSide(myChromosome.x%self.Size,newY)
        pisa_hor = self.isHorizontal(newY)
        if newY == 0:
            return None
        elif pisa_hor == True or pisa == True:
            newY -= 2    
        return Chromosome(myChromosome.x, int(newY), myChromosome.energy)
    
    def leftUpNeighbour(self, myChromosome):
        left = self.leftNeighbour(myChromosome)
        leftUp = None
        if left is not None:
            leftUp = self.upNeighbour(left)
        return leftUp    
    
    def leftDownNeighbour(self, myChromosome):

        left = self.leftNeighbour(myChromosome)
        leftDown = None
        if left is not None:
            leftDown = self.downNeighbour(left)
        return leftDown

    def rightUpNeighbour(self, myChromosome):
        right = self.rightNeighbour(myChromosome)
        rightUp = None
        if right is not None:
            rightUp = self.upNeighbour(right)
        return rightUp


    def rightDownNeighbour(self, myChromosome):
        right = self.rightNeighbour(myChromosome)
        rightDown = None
        if right is not None:
            rightDown = self.downNeighbour(right)
        return rightDown
    
    
    def getNeighbors (self, myChromosome, existingChromosomes):
        neighborList = []
        x = myChromosome.x
        y = myChromosome.y
        
                
        if x > 1:
            elem = self.leftNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
        
        if x < (self.multiplicity - 0.5) * self.Size -2:
            elem = self.rightNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
        
        if y > 1: 
            elem = self.downNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
        
        if y < (self.multiplicity - 1) * self.inclinacion * self.Size - 2:
            elem = self.upNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
        
        if x > 1 and y > 1:
            elem = self.rightUpNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
        
        if x < (self.multiplicity - 0.5) * self.Size -2 and y > 1:
            elem = self.leftUpNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
                
        if  x > 1 and y < (self.multiplicity - 1) * self.inclinacion * self.Size - 2:   
            elem = self.rightDownNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)
                
        if x < (self.multiplicity - 0.5) * self.Size -2 and y < (self.multiplicity - 1) * self.inclinacion * self.Size - 2:
            elem = self.leftDownNeighbour(myChromosome)
            if elem != None:
                neighborList.append(elem)            

        for existingChromosome in existingChromosomes:
            for neighbor in neighborList:
                if existingChromosome.x == neighbor.x and existingChromosome.y == neighbor.y:
                    neighborList.remove(neighbor)
        return neighborList;
    
     
    def mutate(self,individual):
        chosenPosition = randint(0,len(individual)-1)
         
        collide = True
        while (collide):
            collide = False
            randomPoint = self.getRandomInnerChromosome()
            for chromosome in individual:
                collide = collide or (chromosome.x == randomPoint.x and chromosome.y == randomPoint.y)
        individual[chosenPosition] = randomPoint
#             
#     
    def mutateOnRectangle(self,individual):
        chosenPosition = randint(0,len(individual)-1)
        chosenChromosome = individual[chosenPosition]
 
        posX = chosenChromosome.x // self.xSize 
        posY = chosenChromosome.y // self.ySize 
        auxX = chosenChromosome.x % self.xSize 
        auxY = chosenChromosome.y % self.ySize    
        newX = 0
        newY = 0
        collide = True
        while collide:
            collide = False
            while self.isSide(newX, newY) or self.isHorizontal(newY):
                if posY%2 == 0:
                    if auxY > int(auxX*self.inclinacion):
                        newX = randint(0, self.Size)
                        newY = randint(int(self.inclinacion*newX), int(self.ySize)) + int(posY * self.ySize)  
                        newX = newX + posX * self.xSize
                    
                    elif auxY > int(2*self.ySize - auxX*self.inclinacion):
                        newX = randint(self.Size, 2*self.Size)     
                        newY = randint(int(2*self.ySize - newX*self.inclinacion), int(self.ySize)) + int(posY * self.ySize)
                        newX = newX + posX * self.xSize 
                    else: 
                        newX = randint(0, self.xSize)
                        if newX < self.Size:
                            newY = randint(0 ,int(self.inclinacion*newX)) + int(posY * self.ySize)
                        else:
                            newY = randint(0, int(2*self.ySize - newX*self.inclinacion)) + int(posY * self.ySize)
                        newX = newX + posX * self.xSize    
                
                else: 
                    if auxY < int(auxX*self.inclinacion - self.ySize):
                        newX = randint(self.Size, 2*self.Size)
                        newY = randint(0, int(self.inclinacion*newX - self.ySize)) + int(posY * self.ySize)    
                        newX = newX + posX * self.xSize
                    elif auxY < int(self.ySize - auxX*self.inclinacion):
                        newX = randint(0, self.Size)
                        newY = randint(0, int(self.ySize - newX*self.inclinacion)) + int(posY * self.ySize)
                        newX = newX + posX * self.xSize
                    else: 
                        newX = randint(0, self.xSize)
                        if newX < self.Size:
                            newY = randint(int(self.ySize - newX*self.inclinacion), int(self.ySize)) + int(posY * self.ySize)
                        else:
                            newY = randint(0 ,int(self.inclinacion*newX -self.ySize)) + int(posY * self.ySize)
                        newX = newX + posX * self.xSize
            randomPoint = Chromosome(newX, newY, 1)        
            for chromosome in individual:
                collide = collide or (chromosome.x == randomPoint.x and chromosome.y == randomPoint.y)    
        individual[chosenPosition] = randomPoint 
        
#######  NOT IMPLEMENTED YET
        
    def rotateRectangle(self,individual):
        return 0
#         xRectangle = randint(0, self.multiplicity-1)
#         yRectangle = randint(0, self.multiplicity-1)
# 
#         #-------------------------------------------------------- xRectangle = 1
#         #-------------------------------------------------------- yRectangle = 1
#     
#         #Crear arrays
#         elementsInRectangle = []
#         for myChromosome in individual:
#             if myChromosome.x >= self.xSize * xRectangle \
#                 and myChromosome.x < self.xSize * (xRectangle + 1) \
#                 and myChromosome.y >= self.ySize * yRectangle \
#                 and myChromosome.y < self.ySize * (yRectangle + 1): 
# 
#                 elementsInRectangle.append(myChromosome)
# 
#         if len(elementsInRectangle) == 0:
#             return
#         
#         rotationAngle = 180 / len(elementsInRectangle)
#         #---------------------------------------------------- rotationAngle = 90
# 
#         for element in elementsInRectangle:
#             self.rotatePoint (element, xRectangle, yRectangle, rotationAngle)
#             
#         
#         
#         #The problem here is that we are rotating particles inside a rectangle, so they tend to fall off the surface.
#         #In that case, they are pushed back to the edge of the rectangle    






# tablero = triangleGeometryMatrix(4,1)
# ejercito = tablero.getInnerChromosomeForEachTriangle([])
# def main():
#     print(tablero.getAnclajesList())
#     print(tablero.getRandomInnerChromosome())
#           
# if __name__ == "__main__":
#     main()          
