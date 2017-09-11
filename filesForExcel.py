'''
Created on 24 ago. 2017

@author: Administrador
'''
import glob
import sys

files = glob.glob(sys.argv[1])
open("forExcel.txt","w+")
for myFile in files:
    f = open(myFile,'r')
    g = open("forExcel.txt","a")
    a = f.readlines()
    b = []
    for j in range(13):
        print("Una y otra vez")
        b.append( a[j].strip("\n"))
    b[11] = b[11].replace(".",",")      
    g.write(str(b[7].split(":")[1])+ ";" + str(b[4].split(":")[1])+ ";" + str(b[8].split(":")[1])+"x"+str(b[9].split(":")[1])+";"+ str(b[1].split(":")[1])+ ";" +str(b[3].split(":")[1])+ ";" +  str(b[6].split(":")[1])+ ";" + str(b[11].split(":")[1])+ ";" + str(b[0].split(":")[1]) + "\n" )