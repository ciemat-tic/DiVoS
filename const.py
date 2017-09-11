'''
Created on 26/02/2015

@author: supermanue
'''
import configparser


RANDOM_INDIVIDUAL=0
MUTATION_INDIVIDUAL=1
CROSSOVER_INDIVIDUAL=2
ROTATION_INDIVIDUAL=3

f_0 = 3.08e-6
min_distance = 100
lammda=2600
#maxCores=1024
maxCores=9999999

class Const(object):

    def __init__(self, inputFile):

        ####PROBLEM SIZE
        self.maxX = 0
        self.maxY =0
        self.multiplicity =0
        self.vortices =0
        self.population =0

        #PROBLEM CONFIGURATION
        self.geometry='square'
        self.anclajesInfluence = False
        self.totallyRandomInicialization = False
        self.outputFolder= ''
        self.executionMode= ''

        #GENETIC ALGORITHM CONFIGURATION
        self.geneticGenerations = 0
        self.geneticCROSSOVER_PROBABILITY = 0
        self.geneticMUTATION_PROBABILITY = 0
        self.geneticROTATION_PROBABILITY = 0
        self.geneticFractionOfOldElementsKept=0
        self.geneticMinIndividualLife = 0

        #SIMMULATED ANNEALING CONFIGURATION
        self.annealingTemperature = 0
        self.annealingEpoch=0
        self.annealingLength=0
        #PHYSICAL PARAMETERS
        self.lammda=0

        self.read_input_file(inputFile)

        print ("INPUT FILE NAME:" + inputFile)
        print ("INPUT FILE DUMP")
        f = open(inputFile, 'r')
        for line in f.readlines():
            print (line)
        f.close()
        print ("DONE")
            

    def get_typename(self, number):
        response = "No tipe"
        if number == RANDOM_INDIVIDUAL:
            response = "RANDOM_INDIVIDUAL"
        elif number == MUTATION_INDIVIDUAL:
            response = "MUTATION_INDIVIDUAL"
        elif number == CROSSOVER_INDIVIDUAL:
            response = "CROSSOVER_INDIVIDUAL"
        elif number == ROTATION_INDIVIDUAL:
            response = "ROTATION_INDIVIDUAL"
        return response

    def read_input_file(self,inputFile):
        config = configparser.ConfigParser()
        config.sections()
        config.read(inputFile)

        ####PROBLEM SIZE
        self.maxX = config.getint('default', 'maxX', fallback='0')
        self.maxY =config.getint('default', 'maxY', fallback='0')
        self.multiplicity =config.getint('default', 'multiplicity', fallback=0)
        self.vortices =config.getint('default', 'vortices', fallback='0')
        self.population =config.getint('default', 'population', fallback='15')
        self.maxCores = config.getint('default', 'maxCores', fallback='1152')
            
        #PROBLEM CONFIGURATION
        self.geometry=config.get('default', 'geometry', fallback='square')
        self.anclajesInfluence =config.getboolean('default', 'anclajesInfluence', fallback='False')
        self.totallyRandomInicialization =config.getboolean('default', 'totallyRandomInicialization', fallback='False')
        self.outputFolder=config.get('default', 'outputFolder', fallback='results')
        self.executionMode=config.get('default', 'executionMode', fallback='batch')

        #GENETIC ALGORITHM CONFIGURATION
        self.geneticGenerations =config.getint('genetic','generations' ,fallback='0')
        self.geneticCROSSOVER_PROBABILITY =config.getfloat('genetic','CROSSOVER_PROBABILITY' ,fallback='0')
        self.geneticMUTATION_PROBABILITY =config.getfloat('genetic','MUTATION_PROBABILITY' ,fallback='0')
        self.geneticROTATION_PROBABILITY =config.getfloat('genetic','ROTATION_PROBABILITY' ,fallback='0')
        self.geneticFractionOfOldElementsKept=config.getfloat('genetic','fractionOfOldElementsKept' ,fallback='0')
        self.geneticMinIndividualLife =config.getint('genetic','minIndividualLife' ,fallback='1')
        #SIMMULATED ANNEALING CONFIGURATION
        self.annealingTemperature =config.getint('annealing','temperature' ,fallback='25000')
        self.annealingEpoch=config.getint('annealing','epoch' ,fallback='100')
        self.annealingLength=config.getint('annealing','length' ,fallback='100')
        
        #BASIN HOPPING CONFIGURATION
        self.basinTemperature =config.getint('basin','temperature' ,fallback='25000')
        self.basinLength=config.getint('basin','length' ,fallback='100')
        
        #PHYSICAL PARAMETERS
        self.lammda=config.getint('bessel','lammda',fallback='2600')
        
        #ALGORITHM CHOOSING
        self.chooseRecocido = config.getboolean('choice','recocido',fallback='False')
        self.chooseBasin = config.getboolean('choice','basin',fallback='False')
        self.chooseGenetico = config.getboolean('choice','genetico',fallback='False')
        self.chooseVoraz = config.getboolean('choice','voraz',fallback='False')
