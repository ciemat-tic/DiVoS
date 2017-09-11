# Use python 3.0 syntax
from  __future__  import  division, print_function
from Chromosome import *

from random import randint
from math import radians, sin, cos
import numpy

#esta es igual que una geometria normal pero los datos se almancenan de manera diferente
# (en formato matriz en lugar de lista) y los cromosomas empleados tienen incorporada
#informacion sobre el rectangulo en el que estan


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
logger = logging.getLogger(__name__)


class squareGeometryMatrix(object):
	def __init__ (self, xSize, ySize, multiplicity):
		self.xSize = xSize
		self.ySize = ySize
		self.multiplicity = multiplicity
		self.name="square"
		
			
		
	def clone (self, individual):
		cloned = []
		for chromosome in individual:
			new  = Chromosome(chromosome.x, chromosome.y, chromosome.energy)
			cloned.append(new)
		return cloned
		
	
	#devuelve una lista de anclajes 
	def getAnclajesList(self):
		
		compressedList = [[Chromosome(self.xSize * x, self.ySize * y, 0.25)
						for y in range(self.multiplicity + 1)] 
						for x in range(self.multiplicity + 1)]
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
			
	
	#crea un cromosoma aleatorio en cada rectangulo. Es interior, o sea de energia 1.
	#Si no dices nada lo crea donde quiere, o tb se puede especificar un rectangulo
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
			maxY = self.multiplicity * self.ySize -2
		else:
			minY = yPos * self.ySize + 1 
			maxY = (yPos + 1) * self.ySize -2 		
		
		newX = 0
		#for example, if it is 0, 19, 20 or 39
		while (newX % self.xSize) == 0 or ((newX + 1) % self.xSize) == 0:
			newX = randint(minX, maxX)

		newY = 0
		while (newY % self.ySize) == 0 or ((newY + 1) % self.ySize) == 0:
			newY = randint(minY, maxY)
			
		functionLogger.debug("(" + str(newX) + " , " + str(newY) + ")")

		return Chromosome(newX, newY, 1)


		
	def getInnerChromosomeForEachRectangle(self, existingChromosomes):
		functionLogger = logger.getChild("getInnerChromosomeForEachRectangle")
		#=======================================================================
		# functionLogger.setLevel(logging.DEBUG)
		#=======================================================================

		resultList=[]
		for xPos in range(self.multiplicity):
			for yPos in range(self.multiplicity):		
				validChromosome = False
				while not validChromosome: 
					validChromosome = True
					newX = randint(1, self.xSize -2)
					newY = randint(1, self.ySize -2)
					newChromosome = Chromosome(newX + xPos * self.xSize, newY + yPos * self.ySize, 1)
				
					for existingChromosome in  existingChromosomes:
						if existingChromosome.x == newChromosome.x and \
							existingChromosome.y == newChromosome.y:
							validChromosome = False
				
				functionLogger.debug("(" + str(newChromosome.x) + " , " + str(newChromosome.y) + ")")
				resultList.append(newChromosome)

		return resultList
	

	def getNeighbors (self, myChromosome, existingChromosomes):
		neighborList = []
		x = myChromosome.x
		y = myChromosome.y


		#si su x no esta en una arista se puede mover a izquierda y derecha
		if x % self.xSize != 0:
			elem = self.leftNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
			
			elem = self.rightNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
		#si su y no esta en una arista se puede mover arriba y abajo
		if y % self.ySize != 0:
			elem = self.upNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
				
			elem = self.downNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)

		#si ni la x ni la y estan en una arista, se pueden mover en diagonal
		if (x % self.xSize != 0) and (y % self.ySize != 0):
			elem = self.leftUpNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
			elem = self.rightUpNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
			elem = self.leftDownNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)
			elem = self.rightDownNeighbour(myChromosome)
			if elem != None:
				neighborList.append(elem)


		for existingChromosome in existingChromosomes:
			for neighbor in neighborList:
				if existingChromosome.x == neighbor.x and existingChromosome.y == neighbor.y:
					neighborList.remove(neighbor)
		return neighborList;


	#if there are neighbors on the left, OK.
	#if not, two options:
	#a) it is in the first rectangle, so no neighbors
	#b) it is not in the first, there is a neightbor in the adjacet square
	#Note that every square has its own border, so the frontier between them is of width 2

	def leftNeighbour(self, myChromosome):
		newX = myChromosome.x -1
		if newX ==0:
			return None
		
		elif newX % self.xSize == 0:
			newX -= 2
			
		return Chromosome(int(newX), myChromosome.y, myChromosome.energy)


	def rightNeighbour(self, myChromosome):
		newX = myChromosome.x +1
		if newX == self.xSize * self.multiplicity -1:
			return None
		elif (newX +1)  % self.xSize == 0:
			newX += 2
		return Chromosome(int(newX), myChromosome.y, myChromosome.energy)


	def upNeighbour(self, myChromosome):
		newY = myChromosome.y +1
		if newY == self.ySize * self.multiplicity -1:
			return None
		elif (newY +1)  % self.ySize == 0:
			newY += 2
		return Chromosome(myChromosome.x, int(newY), myChromosome.energy)

	def downNeighbour(self, myChromosome):
		newY = myChromosome.y -1
		if newY ==0:
			return None
		elif newY % self.ySize == 0:
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







	
	def mutate(self,individual):
		chosenPosition = randint(0,len(individual)-1)
		
		collide = True
		while (collide):
			collide = False
			randomPoint = self.getRandomInnerChromosome()
			for chromosome in individual:
				collide = collide or (chromosome.x == randomPoint.x and chromosome.y == randomPoint.y)
		individual[chosenPosition] = randomPoint
			
	
	def mutateOnRectangle(self,individual):
		chosenPosition = randint(0,len(individual)-1)
		chosenChromosome = individual[chosenPosition]

		myXRectangle = int((chosenChromosome.x) / self.xSize) * self.xSize
		myYRectangle = int((chosenChromosome.y) / self.ySize) * self.ySize
		
		collide = True
		while (collide):
			collide = False
			newX = 0
			while (newX % self.xSize) == 0:
				newX = randint(1, self.xSize-2 ) + myXRectangle
			newY = 0
			while (newY % self.xSize) == 0:
				newY = randint(1, self.ySize-2) + myYRectangle
			randomPoint = Chromosome(newX, newY, 1)

			for chromosome in individual:
				collide = collide or (chromosome.x == randomPoint.x and chromosome.y == randomPoint.y)
		
		individual[chosenPosition] = randomPoint
		
		
		
	def rotateRectangle(self,individual):
		xRectangle = randint(0, self.multiplicity-1)
		yRectangle = randint(0, self.multiplicity-1)

		#-------------------------------------------------------- xRectangle = 1
		#-------------------------------------------------------- yRectangle = 1
	
		#Crear arrays
		elementsInRectangle = []
		for myChromosome in individual:
			if myChromosome.x >= self.xSize * xRectangle \
				and myChromosome.x < self.xSize * (xRectangle + 1) \
				and myChromosome.y >= self.ySize * yRectangle \
				and myChromosome.y < self.ySize * (yRectangle + 1): 

				elementsInRectangle.append(myChromosome)

		if len(elementsInRectangle) == 0:
			return
		
		rotationAngle = 180 / len(elementsInRectangle)
		#---------------------------------------------------- rotationAngle = 90

		for element in elementsInRectangle:
			self.rotatePoint (element, xRectangle, yRectangle, rotationAngle)
			
		
		
		#The problem here is that we are rotating particles inside a rectangle, so they tend to fall off the surface.
		#In that case, they are pushed back to the edge of the rectangle
		
		#also, note that to simplify opperations the point is moved to rectangle (0,0) and 
		#then back to its original position
		
	def rotatePoint (self, element, xRectangle, yRectangle, rotationAngle):
		functionLogger = logger.getChild("rotatePoint")
		#=======================================================================
		# functionLogger.setLevel(logging.DEBUG)
		#=======================================================================
		
		radian = radians (rotationAngle)
		
		rotationCenterX = self.xSize / 2
		rotationCenterY = self.ySize / 2
		
		xRectangleOffset = self.xSize * xRectangle
		yRectangleOffset = self.ySize * yRectangle
		
		xInsideRectangle = element.x - xRectangleOffset
		yInsideRectangle = element.y - yRectangleOffset

		
		newX = rotationCenterX + (xInsideRectangle-rotationCenterX)*cos(radian) - (yInsideRectangle-rotationCenterY)*sin(radian)
		newY = rotationCenterY + (xInsideRectangle -rotationCenterX)*sin(radian) + (yInsideRectangle-rotationCenterY)*cos(radian)


		if (newX > self.xSize-2)  or (newX <1):
			newX = xInsideRectangle
		if (newY > self.ySize-2)  or (newY <1):
			newY = yInsideRectangle
			
		newX = newX + xRectangleOffset
		newY = newY + yRectangleOffset

		#at last, put them back in their rectangle

		functionLogger.debug("I rotate point " + str(element) + " to (" + str(newX) + ", " + str(newY) + ")")
		element.x = int(newX)
		element.y = int(newY)
		