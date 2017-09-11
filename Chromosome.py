# Use python 3.0 syntax
from  __future__  import  division,  print_function
import math
# Esto es igual que un cromosoma normal pero ademas almacena el rectangulo en el que esta.
# de esta manera se pueden mirar su vecinos y tal
#


# importante: la posicin X, Y es absoluta, NO dentro de su cuadrante
# eso dificultaria las operaciones y es mucho menos eficiente (aunque quede mas bonico)

class Chromosome(object):

	def __init__ (self, x, y, energy):
		
		
		
		#=======================================================================
		# self.x = numpy.int64(x)
		# self.y = numpy.int64(y)
		#=======================================================================
		
		self.x = x
		self.y = y
		
		self.energy = energy
		#print("nuevo cromosoma con x,y, xRect, yRect = " + str(x) + ","+ str(y) + ","+ str(xRectangle) + ","+ str(yRectangle) + ",")

	
	def __eq__(self, other):
		if not isinstance(other, Chromosome):
			return False
		if self.x == other.x and self.y == other.y and self.energy == other.energy:
			return True
		return False
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __repr__(self, *args, **kwargs):
		return ("(" + str(self.x) + " , " + str(self.y) + ")")
	
	#distancia desde este cromosoma a otro
	def distance(self, chromosome2):
		value =  math.sqrt((self.x - chromosome2.x) ** 2 +
				(self.y - chromosome2.y) **2)
		return value
		
		

