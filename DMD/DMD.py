import matplotlib.pyplot as plt
import numpy as np
import math
import os

debug = False

store = False
offset = 0
xVal = 0
rollOverCount = 0
rawData = []
cleanData = []
data = []
test = []
rows = []

dataPage = []
eventCount = []
slope = []
timeStamp = []
torqueTicks = []

cadence = []
torque = []
power = []
time = []

if(not debug):
    print("Working...\n")

file = open(r"C:\Users\taivassalolab\AppData\Roaming\ANTwareII\logs\Device0.txt","r+")

for line in file:
    if len(line) == 82:
        for character in line:
            if character == '[':
                store = True
            if character == ']':
                store = False
            if store and character != '[':
                rawData.append(character)

for i in range(0, int(len(rawData)/2)):
   data.append(format(int(rawData[2*i] + rawData[(2*i)+1], 16), '#04x'))

#Deletes File Contents After Opening
if(not debug):
    file.truncate(0)
file.close()

for i in range(0, len(data), 13):
   test.append(data[i:i+13])

rowNum = len(test)

for i in range(0, rowNum):
    #Only if row data type is type '32'
    #Takes corresponding hex data from long string of data
    if int(data[13*i + 4], 16) == 32:
        eventCount.append(int(data[13*i + 5], 16))
        slope.append(int(data[13*i + 6] + data[13*i + 7][:0] + data[13*i + 7][2:], 16)*10)
        timeStamp.append(int(data[13*i + 8] + data[13*i + 9][:0] + data[13*i + 9][2:], 16))
        torqueTicks.append(int(data[13*i + 10] + data[13*i + 11][:0] + data[13*i + 11][2:], 16))

if(debug):
    for i in range(0, len(eventCount)):
       print("Event Count: " + str(eventCount[i])) 
       print("Slope: " + str(slope[i])) 
       print("Time Stamp: " + str(timeStamp[i])) 
       print("Torque Ticks: " + str(torqueTicks[i]))
       print('\n')

#Cadence Calculation
for i in range(1, len(eventCount)):
    if eventCount[i] != eventCount[i-1]:
        if (timeStamp[i] - timeStamp[i-1]) < 0:
            cadencePeriod = (timeStamp[i]-(65535-timeStamp[i-1]))*0.0005/(eventCount[i]-eventCount[i-1])
            rollOverCount = rollOverCount + 1
        else:
            cadencePeriod = (timeStamp[i]-timeStamp[i-1])*0.0005/(eventCount[i]-eventCount[i-1])
        cadence.append(round(60/cadencePeriod, 2))
        if(debug):
            print("Event Count: " + str(eventCount[i]))
        time.append(round((timeStamp[i] + 65535*rollOverCount)*0.0005 , 2))

#Torque Calculation
for i in range(1, len(eventCount)):
    if eventCount[i] != eventCount[i-1]:
        if (timeStamp[i] - timeStamp[i-1]) < 0:
            elapsedTime = (timeStamp[i]-(65535- timeStamp[i-1]))*0.0005
        else:
            elapsedTime = (timeStamp[i]-timeStamp[i-1])*0.0005
        torqueStamp = (torqueTicks[i]-torqueTicks[i-1])
        torqueFrequency = 1/(elapsedTime/torqueStamp) - offset
        torque.append(round(torqueFrequency/(slope[i]/10), 2))

for i in range(0, len(cadence)):
    power.append(round(cadence[i]*torque[i]*math.pi/30,2))
    if(debug):
        print("\nCadence: " + str(cadence[i])) 
        print("Torque: " + str(torque[i]))
        print("Power: " + str(power[i]))

#Remove Outliers
for i in range(0, len(power)-1):
    if (power[i] < 0):
        power.pop(i)
        time.pop(i)

mean = sum(power)/len(power)
variance = sum([((x - mean) ** 2) for x in power]) / len(power)
res = variance ** 0.5
scaleOffset = 3 * res
yMin = mean - scaleOffset
yMax = mean + scaleOffset

for i in range(0, len(power)-1):
    if (power[i] > yMax) or (power[i] < yMin):
        power.pop(i)
        time.pop(i)

f = open(r"C:\Users\Public\DMD Project\Data\Data.csv","w+")
f.close()

for i in range(0, len(power)):
    count = 0
    with open(r"C:\Users\Public\DMD Project\Data\Data.csv", "a") as fileToWrite:
        if count == 0:
            fileToWrite.write("Time , Power\n")
            count = count + 1
        fileToWrite.write(str(time[i]) + "," + str(power[i]) + "\n")
       
totalEnergy = round(np.trapz(power, time), 2)

plt.title("Total Energy: " + str(totalEnergy))
plt.xlabel('Time') 
plt.ylabel('Power')
plt.plot(time, power, marker='o', linestyle='')
if(debug):
    plt.show()
plt.savefig(r"C:\Users\Public\DMD Project\Data\dataPlot")

if(not debug):
    print("Success! Data Saved to Users\Public\DMD Project\Data")