# Copyright 2013, William Edelstein, Arthur Edelstein
# All rights reserved.
# (BSD 2-Clause License attached)
#
# These packages are available at http://scipy.org and http://matplotlib.sourceforge.net
from scipy import *
from pylab import *
from numpy.random import uniform,poisson
from scipy.weave import inline
import time

# Set the rate at which voters arrive in each hour of the day:
hourlyRates = array([.1,.1,.05,.05,.05,.1,.1,.05,.05,.05,.1,.1,.1])

def generateArrivalTimes(meanTotalVoters,hourlyRates):
    startTime = 0
    arrivalTimes = array([])
    # Go through each hour and generate arrival times:
    for hourlyRate in hourlyRates:
        # The number of voters that arrive in this hour is poisson distributed:
        n = poisson(lam = meanTotalVoters * hourlyRate)
        # The time at which the voters arrive is uniformly distributed throughout the hour; sort arrivals in order
        # and concatenate them with arrivals in previous hours:
        arrivalTimes = hstack((arrivalTimes,sort(uniform(startTime,startTime+60,n))))
        # The next hour starts 60 min later:
        startTime += 60
        
    return arrivalTimes # The full list of arrival times

# The following is inline C code, requiring the "scipy.weave" module and a gcc compiler:
queueCode = """
    for (int i=numMachines+1;i<numArrivals;i++) {
        // If the ith voter arrives before the (i-numMachines)th voter has departed:
        if (arrivalTimes[i] < departureTimes[i-numMachines]) {
            // The ith voter can only start voting when the (i-numMachines)th voter has left.
            votingTimes[i] = departureTimes[i-numMachines];
            // The voter leaves after spending machineTime voting.
            departureTimes[i] = votingTimes[i] + machineTime;
        }
    }
    int k = 0;
    return_val = 0;
"""      

def runQueue(numMachines,numArrivals,arrivalTimes,votingTimes,departureTimes,machineTime):
    q = inline(code=queueCode, force=0, arg_names=['numMachines','numArrivals','arrivalTimes','votingTimes','departureTimes','machineTime'],compiler='gcc')

def simulateVoting(numMachines,machineTime,arrivalTimes):
    # Time at which ith voter starts voting; will  be corrected for voter pileup (runQueue, below):
    votingTimes = arrivalTimes.copy()
    # Time at which ith voter finishes voting and leaves; will be corrected for voter pileup (runQueue, below):
    departureTimes = votingTimes + machineTime 
    
    # Number of voters:
    numArrivals = len(arrivalTimes) 
    # Correct votingTimes and departureTimes for effects of the queue:
    runQueue(numMachines,numArrivals,arrivalTimes,votingTimes,departureTimes,machineTime)

    # If there is time between arriving and voting, that is the time spent waiting:
    waitLengths = votingTimes - arrivalTimes
    return votingTimes,departureTimes,waitLengths


def runMultipleTrials(numTrials=10000,numMachines=10,machineTime=5,meanTotalVoters=1500,hourlyRates =hourlyRates):
    # This function is for running a lot of trials with identical parameters.
    
    # Initialize results arrays:
    waitMaxes=[]
    lastVoterDepartures=[]
    
    for trial in range(numTrials):
        # Indicate progress:
        if trial % 1000 == 0:
            print '\t%d out of %d' % (trial,numTrials)
        # Run a single trial:
        arrivalTimes = generateArrivalTimes(meanTotalVoters,hourlyRates)
        votingTimes,departureTimes,waitLengths = simulateVoting(numMachines,machineTime,arrivalTimes)
        waitMaxes.append(max(waitLengths))
        lastVoterDepartures.append(departureTimes[-1])
    
    # Convert lists to numpy arrays:
    waitMaxes = array(waitMaxes)
    lastVoterDepartures = array(lastVoterDepartures)
    return waitMaxes,lastVoterDepartures


def fractionGreaterThan(data,minval):
    # Compute fraction of elements of "data" that are greater than "minval".
    return sum(data>minval)/float(len(data))

def saveStats(machineTime,numMachines,votersPerMachine,statData):
    # Write statistics to a file.
    f1 = open("dat_%d_%d_%d.txt" % (machineTime,numMachines,votersPerMachine),'w')
    savetxt(f1,statData,fmt='%g',delimiter='\t')
    f1.close()

def runHugeBatch(
  numTrials = 10000,
  machineTimeList = [2, 5, 7, 10, 15],
  numMachinesList = [2, 5, 10, 15, 20],
  votersPerMachineList = [50, 100, 150, 200, 300],
  thresholdWaitingTimeList = [15, 30, 60, 90, 120]):
    # Initialize:
    count=0
    dataRowList = []
    
    # Loop through all possible parameter combinations:
    for machineTime in machineTimeList:
        for numMachines in numMachinesList:
            for votersPerMachine in votersPerMachineList:
                meanTotalVoters = votersPerMachine * numMachines
                count +=1
                print count,machineTime,numMachines,votersPerMachine
                
                # Run the 10000 trials and save their results:
                waitMaxes,lastVoterDepatures = runMultipleTrials(numTrials = numTrials, numMachines = numMachines, machineTime = machineTime, meanTotalVoters = meanTotalVoters)
                saveStats(machineTime,numMachines,votersPerMachine,transpose(vstack((waitMaxes,lastVoterDepatures))))
                
                # Compute number of voters who wait longer than a threshold waiting time:
                angerFrac = [fractionGreaterThan(waitMaxes,t) for t in thresholdWaitingTimeList]
                
                # Store various results in a 2D list
                dataRow = [machineTime,numMachines,votersPerMachine] + angerFrac
                dataRowList.append(dataRow)

    # Save results in dataRowList:
    f1 = open('voteCombos.txt','w')
    f1.write('machineTime\tnumMachines\tvotersPerMachine\t>15\t>30\t>60\t>90\t>120\n')
    savetxt(f1,dataRowList,fmt='%g',delimiter='\t')
    f1.close()


def plotAFewRuns():
    # This plots a small number of trials.
    numMachines=10
    machineTime =5
    meanTotalVoters = 1500
    thresholdWaitingTime = 60
    threshCount = 0
    
    figure()
    
    # Run 5 individual trials and plot them:
    for i in range(5):
        arrivalTimes = generateArrivalTimes(meanTotalVoters,hourlyRates)
        votingTimes,departureTimes,waitLengths = simulateVoting(numMachines,machineTime,arrivalTimes)
        plot(arrivalTimes,waitLengths)

    xlabel('Arrival time, min')
    ylabel('Waiting time, min')
    title('Vote queuing simulation')
    show()

# Main program:
plotAFewRuns()
startTime = time.time()
runHugeBatch()
totalTime = time.time()-startTime
print "Total computer time: %g",totalTime
