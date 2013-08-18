### Voting Queue Simulation Script Usage Instructions

- Arthur D. Edelstein, arthuredelstein@gmail.com
- William A. Edelstein, w.edelstein@gmail.com

Source code from [Edelstein, William A., and Arthur D. Edelstein. "Queuing and elections: long lines, DREs and paper ballots." Proceedings of EVT/WOTE 2010.](http://bit.ly/T2BEFr)

The accompanying code, (./voteQueueSimulator.py), was used to simulate the queuing of voters at a polling station. The code assumes that during each voting period, voters arrive at the polling station with a fixed number of voting machines (`numMachines`) in a Poisson process (voter arrival has constant probability per unit time). An array of pseudorandomly-generated times (`arrivalTimes`) is created by the function `generateArrivalTimes`.

Next in the function `simulateVoting`, the time at which each voter commences voting (`votingTimes`) and the time at which each voter finishes voting and vacates the voting machine (`departureTimes`) are computed. The voter departs after a fixed time (`machineTime`) has elapsed since voting commenced, i.e. `departureTimes = votingTimes + machineTime`.

When a voter arrives, if a voting machine is available, then by default that voter should begin voting immediately. If however, no machines are available when the voter arrives, then the voter is forced to wait until a voting machine is vacated. Voters will vote in the order that they arrive (and join the queue). According to these rules, each voter is assessed in chronological order and assigned a `votingTime` and `departureTime` by the `queueCode`. 

Polling conditions of interest that may be varied, including the rates of voter arrival by the hour (`hourlyRates`), the time a voter requires to vote at a machine (`machineTime`), the number of voting machines at the polling station (`numMachines`), the number of voters expected per machine (`votersPerMachine`). One may also count the proportion of trials that meet a certain condition, such as a `thresholdWaitingTime`.

The function `plotAFewRuns` may be modified to plot any number of runs with any parameters of the users choice. The function `runHugeBatch` allows large numbers of trials to be run and the statistics collected. Output files are named `voteCombos.txt` and `dat_[machineTime]_[numMachines]_[votersPerMachine].txt`.

This code is written in the Python programming language (version 2.5 was used at the time of publication), and requires the Python packages [scipy](http://scipy.org), [numpy](numpy.org), and [matplotlib](http://matplotlib.org). Additionally, part of the script contains inline C code that requires a C compiler (we used gcc). 

The output files were analyzed and plotted using Excel and plotted with Axum 5.0.

