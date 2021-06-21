import numpy as np

#As the name says, this class is intended to wrap the raw TPD data.
#This means it acts as an interface between the data file (.csv) and the UI.
#It also contains the relevant methods for processing the raw data
# This could be decoupled by adding a class responsible for the processing.
class RawDataWrapper():
    def __init__(self, filePath):
        self.m_filePath = filePath
        substrings = filePath.split('/')
        self.m_fileName = substrings[len(substrings) - 1]
        self.m_dataParsed = False
        self.m_dataProcessed = False
        self.m_correctedTemp = None
        self.m_interpolatedTemp = None
        self.m_reciprocalTemp = None
        # self.m_interpolatedTime = None
        self.m_coveragesNormalized = False
        self.m_interpolatedData = {}
        self.m_logInterpolatedData = {}
        self.m_parsedCoverage = "No coverage in filename!"
        self.m_parsedCoverageAvailable = False
        self.m_coverages = {}
        self.m_parsedExperimentNumber = "No experiment number!"

    def parseRawDataFile(self): #This function parses the .csv
        if(self.m_dataParsed):
            return

        substrings = self.m_fileName.split(' ')
        self.m_parsedExperimentNumber = substrings[0] #first substring should always be number
        for s in substrings:
            if (s[-1] == 'L' or s[-1] == 'l'):
                try:
                    s = float(s[:-1]) #this will throw a value error if not possible
                    self.m_parsedCoverage = "{:04.2f}L".format(s)
                    self.m_parsedCoverageAvailable = True
                    break
                except ValueError:
                    continue #Not a float

        self.m_headerData = np.loadtxt(self.m_filePath,dtype=str, skiprows=1,max_rows=1, delimiter=',')
         #second item is the number of lines remaining in the header after the second line
        headerLength = int(self.m_headerData.item(1))

        m_parsedDataTitles = np.loadtxt(self.m_filePath,dtype=str, skiprows=headerLength + 1,max_rows=1, delimiter=',')
        self.m_listOfColumns = [t for t in [e.strip("\'\"") for e in m_parsedDataTitles.tolist()] if not t == '']
        self.m_listOfColumns.remove('Time') #we are ignornign the first column
        # print(self.m_listOfColumns) #for debugging

        #parsed data is in row major format i.e. time(ms),temp, m1, m2, m3...
        temp = np.loadtxt(self.m_filePath, dtype = float, skiprows=headerLength + 2, delimiter=',', usecols=range(1,len(self.m_listOfColumns)+1))

        #now columns can be traversed contiguously in memory
        self.m_parsedRawData = temp.transpose().copy()
        self.m_dataParsed = True
        # del temp #free memory, or at least suggest it to the garbage collector

    def getRawTempMin(self): #Get lowest available temperature from raw temperature data.
        return np.amin(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])

    def getRawTempMax(self): #Get highest available temperature from raw temperature data.
        return np.amax(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])

    def getRawDataVSRawTemp(self, desiredMasses): #Get raw data vs temperature as np.array
        result = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        for i in self.massListToIndices(desiredMasses):
            result = np.vstack((result, self.m_parsedRawData[i,:]))
        return result

    def getRawDataVSRawTime(self, desiredMasses): #Get raw data vs time as np.array
        result = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('ms')),:])
        for i in self.massListToIndices(desiredMasses):
            result = np.vstack((result, self.m_parsedRawData[i,:]))
        return result

    def getRawTempVSRawTime(self): #Get raw temperature vs time as np.array
        # result = np.vstack((self.m_interpolatedTime, self.m_interpolatedTemp))
        result = np.vstack((self.m_parsedRawData[0,:], self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:]))
        return result

    def getMassList(self): #return all available massses in the file
        return self.m_listOfColumns[2:] #first two columns are "ms" and "temperature"

    def massListToIndices(self, massList): #convert mass list argument to indices in self.m_parsedRawData
        result = list()
        for m in massList:
            try:
                result.append(self.m_listOfColumns.index(m))
            except ValueError:
                continue
        return result#[self.m_listOfColumns.index(m) for m in massList]

    def smooth_running_average(self, x, N): #running average over N points
        cumsum = np.cumsum(np.insert(x, 0, 0))
        smoothResult = (cumsum[N:] - cumsum[:-N]) / float(N)
        smoothResult = np.insert(smoothResult,0,x[:N-1])
        smoothResult = np.append(smoothResult,x[N:-1:-1])
        return smoothResult

    #The process parsed data function takes care of smoothing and interpolating the raw (noisy) temperature data on a uniform grid.
    #The counts can then also be interpolated and provided on a uniform grid. This makes inversion analysis (the integration part)
    #easier down the line.
    def processParsedData(self, tRampStart, tRampEnd, tCutStart, tCutEnd, removeBackground, smooth,
     tempScaleCorrection, tempOffsetCorrection, smoothpoints = 5, tStep = 0.1):
        if (self.m_dataProcessed == True):
            return
        # self.m_tStep = tStep
        # self.m_correctedTemp = np.zeros(self.m_parsedRawData.shape[1])
        # correct temperature (taken from Honza's scripts)
        self.m_correctedTemp = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        self.m_correctedTemp *= tempScaleCorrection
        self.m_correctedTemp += tempOffsetCorrection

        #get running average from temperature data
        self.m_correctedTemp = self.smooth_running_average(self.m_correctedTemp, 20)
        tRampStart = np.median(self.m_correctedTemp) # starting the search in the middle of the temperature ramp (approximately)
        tRampEnd = tRampStart

        tempSearchInput = np.abs(self.m_correctedTemp - tRampStart)
        tRampStartIndex = np.argwhere(tempSearchInput == np.amin(tempSearchInput))[-1][0] #find closest value to input

        while self.m_correctedTemp[tRampStartIndex + 1] > self.m_correctedTemp[tRampStartIndex]:
            tRampStartIndex -= 1 # find lowest index of the ramp
            if(tRampStartIndex == 0): break

        tempSearchInput = np.abs(self.m_correctedTemp - tRampEnd)
        tRampEndIndex = np.argwhere(tempSearchInput == np.amin(tempSearchInput))[-1][0] #find closest value to input

        del tempSearchInput #no need to waste memory

        while self.m_correctedTemp[tRampEndIndex - 1] < self.m_correctedTemp[tRampEndIndex]:
            tRampEndIndex += 1 # find highest index of the ramp
            if(tRampEndIndex == self.m_correctedTemp.size - 1): break

        self.m_interpolatedTemp = np.arange(tCutStart, tCutEnd, tStep) #generate equidistantly spaced range of temperature points
        self.m_reciprocalTemp = np.reciprocal(self.m_interpolatedTemp)
        # self.m_interpolatedTime = np.interp(self.m_interpolatedTemp, self.m_correctedTemp[tRampStartIndex:tRampEndIndex], self.m_parsedRawData[0,tRampStartIndex:tRampEndIndex])
        # print(tRampStartIndex, tRampEndIndex)


        for m in self.getMassList(): #for each mass
            #interpolate data by default
            interpDataBuffer = np.interp(self.m_interpolatedTemp, self.m_correctedTemp[tRampStartIndex:tRampEndIndex],
                self.m_parsedRawData[self.m_listOfColumns.index(m),tRampStartIndex:tRampEndIndex])
            if smooth: #if we use the smooth option, also smooth the data (counts/s)
                interpDataBuffer = self.smooth_running_average(interpDataBuffer, smoothpoints)
            if removeBackground: #if we want to remove the background, do that
                interpDataBuffer -= np.amin(interpDataBuffer)
                zeroIndices = np.where(interpDataBuffer == 0) #find zeros
                for i in zeroIndices:
                    interpDataBuffer[i] = np.finfo(float).eps #add machine epsilon to zeros to avoid divide by zero in log later on
            # if normalize: #first step to normalizing -> find coverages
            self.m_coverages[m] = np.trapz(interpDataBuffer, dx= tStep) #write absolute coverage into dictionary
            self.m_interpolatedData[m] = interpDataBuffer #write buffer into "permanent" storage
            self.m_logInterpolatedData[m] = np.log(interpDataBuffer)
        self.m_dataProcessed = True

    #This function allows normalizing the available spectra to a specific spectrum which is defined to be the "monolayer coverage".
    #Doesn't actually need to be the monolayer, but the area under that spectrum will be defined as 1, and all others will be normalized to it.
    def normalizeDataTo(self, referenceRawDataWrapper):
        if (not self.m_dataProcessed or not referenceRawDataWrapper.m_dataProcessed):
            return
        #only try to normalize masses which we actually have access to
        availableMasses =  list(set(self.getMassList()) & set(referenceRawDataWrapper.getMassList()))
        for m in availableMasses:
            referenceCoverage = referenceRawDataWrapper.m_coverages[m]
            # self.m_coverages[m] = np.trapz(self.m_interpolatedData[m], dx= self.m_tStep)
            self.m_coverages[m] /= referenceCoverage
            self.m_interpolatedData[m] /= referenceCoverage
        self.m_coveragesNormalized = True

    def getProcessedData(self, desiredMasses): #get processed data versus temperature as np.array
        result = self.m_interpolatedTemp
        for m in desiredMasses:
            if m in self.m_listOfColumns:
                result = np.vstack((result, self.m_interpolatedData[m]))
        # return np.concatenate((self.m_correctedTemp,self.m_parsedRawData[self.m_listOfColumns.index('temperature')+1:,:]))
        return result

    def getProcessedLNData(self, desiredMasses): #ln(desorption rate) vs temperature
        result = self.m_interpolatedTemp
        for m in desiredMasses:
            if m in self.m_listOfColumns:
                result = np.vstack((result, self.m_logInterpolatedData[m]))
        return result

    def getProcessedArrheniusData(self, desiredMasses):  #ln(desorption rate) vs 1/temperature
        result = self.m_reciprocalTemp
        for m in desiredMasses:
            if m in self.m_listOfColumns:
                result = np.vstack((result, self.m_logInterpolatedData[m]))
        return result

    def getParsedCoverageAsFloat(self):
        return float(self.m_parsedCoverage[0:-1]) #TODO: in the future, one can use the calibration mol/uc/L to get ML normalized coverages

    def getCoverageLabels(self, desiredMasses):#get the labels for the plot legend for each of the desired masses.
        result = []
        for m in desiredMasses:
            if m in self.m_listOfColumns:
                if self.m_coveragesNormalized: #Either returning normalized coverages
                    result.append("M" + m + ' {:04.2f} ML'.format(self.m_coverages[m]) + " #" + self.m_parsedExperimentNumber)
                else:#Or returning absolute counts
                    result.append("M" + m + " " + self.m_parsedCoverage + " #" + self.m_parsedExperimentNumber)
                    # result.append("M" + m + ' {:f} Counts'.format(self.m_coverages[m]))
        return result

    def getLangmuirLabels(self, desiredMasses):#get labels for the plot legend in langmuir
        result = []
        for m in desiredMasses:
            if m in self.m_listOfColumns:
                result.append("M" + m + " " + self.m_parsedCoverage + " #" + self.m_parsedExperimentNumber)
        return result