# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 23:06:36 2018

@author: Florian
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 02:22:34 2018

@author: cummi
"""

from scipy.fftpack import fft
import scipy.io.wavfile as wav
import numpy as np
import os
import os.path
import csv
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank

length = 2
silence = 0.01
    
# frames the signal at 25ms per frame
def framing(signal, fr,rate):
    result = []
    # result is a list of frames, each frame having (smapling_frequency * 25ms) samples
    for i in range(round((len(signal))/fr)-1):
        result.append([(i*fr),(i+1)*fr])
    return  result

# gets the maximum frequency of each frame
def max_amp(frames,signal):
    amp = []
    for frame in frames:
        for i in frame:
            if signal[i] == max(signal[frame[0]:frame[1]]):
                amp.append(i)
                break
    # frqs is a list of frequencies
    return amp

""" detects fast changes in frequency using the standard deviation
 of the list of  frequencies from above function """
def fast_changes(amp,fs,signal):
    x, z = [], []
    for i in range(1,len(amp)):
        j,k=amp[i-1],amp[i]
        """ detect fast change if the difference between the current and previous frequency
         is greater that the standard deviation of the frequency list"""
        if i == len(amp) -1:
            z.append(x)
            break
        if abs(signal[k]-signal[j]) < np.std([signal[x] for x in amp]):
            x.append(k)
        else:
            z.append(x)
            x=[]
            
            x.append(k)
        # z is a list of lists 
    for i in range(len(z)):
        #take only the first and last index of z
        z[i] = [z[i][0],z[i][len(z[i])-1]]
    print("z")
    print(z)
    return z

""" this keeps the file length to n seconds and removes the silent files"""
def filter_frames(signal,p,fs):
    s = round(length * fs);
    arr = []
    for x in p[:]:
        diff = x[1] - x[0]
        if diff > s:
            temp = round(diff / s)
            t = x[0]
            for i in range(temp):
                arr.append([t,t+s])
                bit = signal[t:t+s] / 32768
                # remove silent files if amplitude is < 0.1 
                if max(bit) < silence:
                    arr.remove([t,t+s])
                t += s
        else:
            arr.append([x[0],x[0]+s])
            bit = signal[x[0]:x[0]+s] / 32768
            # remove silent files if amplitude is < 0.1 
            if max(bit) < silence:
                arr.remove([x[0],x[0]+s])
    return arr


## check for repeated files
#def over_lap(p,signal,fs):
#    s=p[:]
#    j = 0
#    for i in range(1,len(p)):
#        if p[i][0] < p[j][1] or p[i][1] > len(signal):
#            s.remove(p[i])
#        else:
#            j = i
#    return s

def save(final,rate,signal,dest):
    for i in range(len(final)):
        if final[i][1]-final[i][0] > (rate/10):
            wav.write(dest+"sample"+str(i)+".wav",rate,signal[final[i][0]:final[i][1]])

def get_files(target_dir):
    item_list=os.listdir(target_dir)
    return item_list

def save_feature(d,rate,name,path,dest):
    (rate,sig) = wav.read(dest+d)
    mfcc_feat = mfcc(sig,rate)
#    d_mfcc_feat = delta(mfcc_feat, 2)
#    fbank_feat = logfbank(sig,rate)
    
    with open(path+"MFCC\\"+name+".csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in mfcc_feat:
            spamwriter.writerow(i)
            
def run(source,dest,name,path):
    print('Starting '+ source)
    (rate,sig) = wav.read(source)
    signal =sig
    print(rate)
    print("Framming...")
    frames = framing(signal,round(0.025*rate),rate)
    print("Getting max frequencies")
    amps = max_amp(frames,signal)
    print("fast changes")
    p = fast_changes(amps,rate,signal)
    print("filter")
    filterate = filter_frames(signal,p,rate)
    print("saving")
    print(filterate)
    save(filterate,rate,signal,dest)
    print('Finishing ' + dest)
    data = get_files(dest)
    for d in data:
        save_feature(d,rate,name,path,dest)

           
            
def start_all(path):
    files = get_files(path)
    os.mkdir(path+"\\MFCC\\")
    for file in files:
        name=file.split('.')[0]
        source=path+file
        os.mkdir(path+name+"\\")
        dest = path+name+"\\"
        run(source,dest,name,path)
    print("Done......")
  

def start_single(path,file):
    name=file.split('.')[0]
    source=path+file
    os.mkdir(path+name+"\\")
    dest = path+name+"\\"
    run(source,dest,name,path)
    print("Done......")
    
    
start_all(path_to_file)

