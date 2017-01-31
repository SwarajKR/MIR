#NOTE

# MAKE Process Multiprocessing Threading Only Uses  one core at time
#perfomance will improve considerably

#IMPORTS
from essentia.standard import MonoLoader
from essentia.standard import Extractor
import essentia.streaming
import numpy as np
from os import listdir
from os.path import isfile, join
import re
import threading
import time

#AVG FUNCTION TO FIND LIST AVG
def avg(arr):
	return sum(arr)/len(arr)

#THE FUNCTION WHICH PERFOMS MIR AND STRORES INTO 
class  findFeature(threading.Thread):
		def __init__(self,songName):
			 threading.Thread.__init__(self)
			 self.name = songName
		def run(self):
			#LOAD THE SONG
			loader = MonoLoader(filename = self.name)
			audio = loader()
			extractor =  Extractor()
			#Return a pool (DS WITH ALL THE  MUSIC FEATUES VALUES )
			pool = extractor(audio)
			name=self.name.split("/")[-1]
			arr = []
			arr.append(name)
			#LIST OF FEATURE NAMES
			features = ['lowLevel.average_loudness', 'rhythm.bpm', 'rhythm.confidence', 'rhythm.onset_rate', 'sfx.pitch_after_max_to_before_max_energy_ratio', 'sfx.pitch_centroid', 'sfx.pitch_max_to_total', 'sfx.pitch_min_to_total', 'tonal.chords_changes_rate', 'tonal.chords_number_rate', 'tonal.key_strength', 'tonal.tuning_diatonic_strength', 'tonal.tuning_equal_tempered_deviation', 'tonal.tuning_frequency', 'tonal.tuning_nontempered_energy_ratio', 'lowLevel.barkbands_kurtosis', 'lowLevel.barkbands_skewness', 'lowLevel.barkbands_spread', 'lowLevel.dissonance', 'lowLevel.hfc', 'lowLevel.pitch', 'lowLevel.pitch_instantaneous_confidence', 'lowLevel.pitch_salience', 'lowLevel.silence_rate_20dB', 'lowLevel.silence_rate_30dB', 'lowLevel.silence_rate_60dB', 'lowLevel.spectral_centroid', 'lowLevel.spectral_complexity', 'lowLevel.spectral_crest', 'lowLevel.spectral_decrease', 'lowLevel.spectral_energy', 'lowLevel.spectral_energyband_high', 'lowLevel.spectral_energyband_low', 'lowLevel.spectral_energyband_middle_high', 'lowLevel.spectral_energyband_middle_low', 'lowLevel.spectral_flatness_db', 'lowLevel.spectral_flux', 'lowLevel.spectral_kurtosis', 'lowLevel.spectral_rms', 'lowLevel.spectral_rolloff', 'lowLevel.spectral_skewness', 'lowLevel.spectral_spread', 'lowLevel.spectral_strongpeak', 'lowLevel.zerocrossingrate', 'rhythm.beats_loudness', 'rhythm.first_peak_bpm', 'rhythm.first_peak_spread', 'rhythm.first_peak_weight', 'rhythm.second_peak_bpm', 'rhythm.second_peak_spread', 'rhythm.second_peak_weight', 'sfx.inharmonicity', 'sfx.oddtoevenharmonicenergyratio', 'tonal.chords_strength', 'rhythm.bpm_intervals', 'tonal.chords_histogram', 'tonal.thpcp', 'tonal.chords_key', 'tonal.chords_scale', 'tonal.key_key', 'tonal.key_scale']
			#ELIMINATED MUSIC FEATURES
			#'tonal.chords_progression' ,  'rhythm.histogram','rhythm.onset_times','rhythm.beats_position', , 'rhythm.bpm_estimates'
			#Temperory Eliminations
			# 'lowLevel.barkbands', 'lowLevel.mfcc', 'lowLevel.sccoeffs', 'lowLevel.scvalleys', 'rhythm.beats_loudness_band_ratio', 'sfx.tristimulus', 'tonal.hpcp',
			for i in features :
				if  type(pool[i]) is np.ndarray:
					arr.append(avg(pool[i]))
				else :
		 		   arr.append(pool[i])
			arr =str(arr)
			arr =  arr[1:-1]+"\n"
			f=  open('dataset.csv','a')
			lock.acquire()
			f.write(arr)
			print "Added",self.name
			lock.release()
			f.close()
			
#Find the  Songs in Specified directory and Return them as a list
def findMusic():
        print "Enter The path : example /home/swaraj/Music \n"
	myPath =  raw_input()
	files = [myPath+"/"+file for file in listdir(myPath) if  re.match(r'(.*)mp3',file)]
	return files

#THE MAIN METHOD FOR UNIT TESTING
def main():
	fileList  =  findMusic()
	count =  0
	threads = []
	for song in fileList :
		threads.append( findFeature(song))
		count+=1
		threads[-1].start()
		if(count == 6):
			count = 0
			for thread  in threads: 
				thread.join()
			del threads[0:5]
	for  t in  range(len(threads)):
		 t.join()
		 
#LOCK FOR SYNC
lock = threading.Lock()
main()
