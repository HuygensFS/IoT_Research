##Part 1
import matplotlib.pyplot as plt
import numpy as np
import sys
#%matplotlib inline
import pandas as pd
import time

file_name = sys.argv[1]
new_day_marker = int(sys.argv[2])
n_limit = int(sys.argv[3])
dif_sec = int(sys.argv[4])

#new_day_marker = 18000 # Number of seconds until next sequence of events
#n_limit = 4 # Number of events to analyse per day start
#dif_sec = 60 #define the time between events
#file_name = 'event_data.json'

df = pd.read_json(file_name,convert_dates=False,convert_axes=False)#,typ='series')
time = df['timestamp']
dp = df['device_position']

list_num = []
count = 0
for i in xrange(len(time)):
    if(i != 0):
        if((time[i] - time[i-1])> new_day_marker):
            list_num.append([])
            for t in range(0, n_limit):
                list_num[count].append(i+t)
            count = count + 1

##Part 2
sequences = []
codes = []
count = 0

for i in xrange(len(list_num)):
    checker = []
    for j in xrange(len(list_num[i])):
        #Compare times and vote
        if(j == 0):
            checker = []
            sequences.append([])
            sequences[count].append(list_num[i][j])
            codes.append([])
            codes[count].append(dp[list_num[i][j]])
            checker.append(dp[list_num[i][j]])
        else:
            if(time[list_num[i][j]] - time[list_num[i][j-1]] < dif_sec and dp[list_num[i][j]] not in checker): #and dp[list_num[i][j]] != dp[list_num[i][j-1]]
                sequences[count].append(list_num[i][j])
                codes[count].append(dp[list_num[i][j]])
                checker.append(dp[list_num[i][j]])
            else:
                checker = []
                sequences.append([])
                codes.append([])
                count = count + 1
                sequences[count].append(list_num[i][j])
                codes[count].append(dp[list_num[i][j]])
                checker.append(dp[list_num[i][j]])
    count = count + 1  

##Part 3
codes_list = []
codes_vote = []
count = 0
for i in xrange(len(codes)):
    a = 0
    for j in xrange(len(codes_list)):
        if np.array_equal(codes[i],codes_list[j]):
            codes_vote[j] = codes_vote[j] + 1
            a = a+1
    if(a == 0):
        if(i > 0):
            count = count + 1
        codes_list.append([])
        #codes_vote.append([])
        for t in xrange(len(codes[i])):
            codes_list[count].append(codes[i][t])
        codes_vote.append(1)
total_list = zip(np.transpose(codes_list), np.transpose(codes_vote))    
print(total_list)
sys.stdout.flush()
