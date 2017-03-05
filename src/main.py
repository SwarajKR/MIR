from essentia.standard import MonoLoader
from essentia.standard import LowLevelSpectralEqloudExtractor
from essentia.standard import LowLevelSpectralExtractor
from essentia.standard import Loudness
from essentia.standard import RhythmExtractor2013
from essentia.standard import KeyExtractor
from essentia.standard import LogAttackTime
import essentia.streaming
import numpy as np
from math import sqrt
import re
from os import listdir
from multiprocessing import Pool
from random import randint

def euclidieanDistance(listOne,listTwo):
	distance = 0
	length = len(listOne)
	for i in range(length):
		distance += (listOne[i]-listTwo[i])*(listOne[i]-listTwo[i])
	return sqrt(distance)

def lowLevel(songName):
	loader = MonoLoader(filename = songName)
	audio = loader()
	extractor = LowLevelSpectralEqloudExtractor()
	feature =list(extractor(audio))
	del feature[1];del feature[1]
	extractor =LowLevelSpectralExtractor()
	featureTwo = list(extractor(audio))
	del  featureTwo[0]
	del featureTwo[-2]
	featureTwo[4] = feature[4][1]
	feature.extend(featureTwo)
	extractor = Loudness()
	feature.append(extractor(audio))
	extractor = LogAttackTime()
	feature.append(extractor(audio)[0])
	extractor = KeyExtractor()
	feature.append(extractor(audio)[2])
	extractor = RhythmExtractor2013()
	data = extractor(audio)
	feature.append(data[0])
	feature.append(data[2])
	for x in  range(len(feature)) :
		if type(feature[x]) is  np.ndarray :
			feature[x] = avg(feature[x])
	return feature
	
def avg(arr):
    return sum(arr)/len(arr)
   
def normalize(val,norm):
 	for i in range(len(val)):
    		val[i] = ((val[i]- norm[i][1])/(norm[i][0]-norm[i][1]))*(100-0.1)+0.1
    	return val

def findCost(medoid,names,distance):
	cost = 0
	for i in range(len(names)):
		temp = distance[medoid[0]][i]
		for x in medoid:
			if distance[x][i] < temp:
				temp = distance[x][i]
		cost += temp
	return cost

def recluster(medoid,names,distance,numCluster,clusters):
	medNum = 0
	newMedoids = []
	newMedoids.extend(medoid)
	newCost = 0
	rMedoid = []
	while(medNum < len(medoid)):
		arr=clusters[medoid[medNum]]
		for start in range(len(arr)):
			newMedoids[medNum] = arr[start]
			cost = findCost(newMedoids,names,distance)
			if  cost < newCost or newCost == 0: 
				newCost = cost
				rMedoid = []
				rMedoid.extend(newMedoids)
			start += 1
		for x in range(len(newMedoids)):
			newMedoids[x] = medoid[x]
		medNum += 1
	return newCost,rMedoid

def cluster(medoid,names,distance,numCluster):
	clusters = {}
	for med in medoid:
		clusters[med] = []
	cost=0;
	for i in range(len(names)):
		temp = distance[medoid[0]][i]
		closestMedoid = medoid[0]
		for x in medoid:
			if distance[x][i] < temp:
				temp = distance[x][i]
				closestMedoid = x
		cost += temp
		clusters[closestMedoid].append(names[i])
	newCost,newMedoids = recluster(medoid,names,distance,numCluster,clusters)
	if newCost < cost:
		cost,clusters = cluster(newMedoids,names,distance,numCluster)
	return cost,clusters

def findMusic():
	print "Enter The path : example /home/swaraj/Music \n"
	#myPath = raw_input()
	#myPath = "/home/swaraj/workspace/test"
	myPath = "/home/swaraj/Music"
	files = [myPath+"/"+file for file in listdir(myPath) if  re.match(r'(.*)mp3',file)]
	return files
    	
def main():
	names = []
	extract = Pool(4)
	featureList = {}
	songList = findMusic()
	extractedList = extract.map(lowLevel,songList)
	norm = []
	for i in zip(*extractedList):
		norm.append([max(i),min(i)])
	for x in range(len(songList)):
		names.append(songList[x].split("/")[-1])
		featureList[names[-1]] =  normalize(extractedList[x],norm)
	distance = {}
	#Find euclidiean Distances
	for song in names:
		distance[song] = []
		current = featureList[song]
		for songitem in  names:
			if songitem == song :
				distance[song].append(0)
			else:
				value = featureList[songitem]
				distance[song].append(euclidieanDistance(current,value))
	#no of clusters = 2
	numCluster = 5
	for i,j in enumerate(names):
		print i,j
	#CHOOSE MEDOIDS RANDOMLY FOR THE FIRST TIME
	medoid = []
	while(len(medoid) < numCluster):
		temp = randint(0,len(names)-1)
		if names[temp] not in medoid:
			medoid.append(names[temp])	
	#CALL CLUSTER METHOD
	cost,clusters = cluster(medoid,names,distance,numCluster)
	#PRINTING THE OUTPUT
	print "\n\n",cost
	for key,value in clusters.iteritems():
		print "\n",key,":",value
main()
