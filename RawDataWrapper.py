import numpy as np

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
        self.m_coverages = {}

    def parseRawDataFile(self):
        if(self.m_dataParsed):
            return

        substrings = self.m_fileName.split(' ')
        for s in substrings:
            if (s[-1] == 'L'):
                try:
                    s = float(s[:-1]) #this will throw a value error if not possible
                    self.m_parsedCoverage = "{:04.2f}L".format(s)
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

    def getRawDataVSRawTemp(self, desiredMasses):
        result = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        for i in self.massListToIndices(desiredMasses):
            result = np.vstack((result, self.m_parsedRawData[i,:]))
        return result

    def getRawDataVSRawTime(self, desiredMasses):
        result = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('ms')),:])
        for i in self.massListToIndices(desiredMasses):
            result = np.vstack((result, self.m_parsedRawData[i,:]))
        return result

    def getRawTempVSRawTime(self):
        # result = np.vstack((self.m_interpolatedTime, self.m_interpolatedTemp))
        result = np.vstack((self.m_parsedRawData[0,:], self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:]))
        return result

    def getMassList(self):
        return self.m_listOfColumns[2:] #first two columns are "ms" and "temperature"

    def massListToIndices(self, massList):
        return [self.m_listOfColumns.index(m) for m in massList]

    def smooth_running_average(self, x, N): #running average
        cumsum = np.cumsum(np.insert(x, 0, 0))
        smoothResult = (cumsum[N:] - cumsum[:-N]) / float(N)
        smoothResult = np.insert(smoothResult,0,x[:N-1])
        smoothResult = np.append(smoothResult,x[N:-1:-1])
        return smoothResult

    def processParsedData(self, tRampStart, tRampEnd, tCutStart, tCutEnd, removeBackground, smooth, smoothpoints = 5, tStep = 0.1):
        if (self.m_dataProcessed == True):
            return
        # self.m_tStep = tStep
        # self.m_correctedTemp = np.zeros(self.m_parsedRawData.shape[1])
        # correct temperature (taken from Honza's scripts)
        self.m_correctedTemp = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        self.m_correctedTemp *= 0.985
        self.m_correctedTemp += 0.836

        #get running average from temperature data
        self.m_correctedTemp = self.smooth_running_average(self.m_correctedTemp, 20)

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

    def getProcessedData(self, desiredMasses):
        result = self.m_interpolatedTemp
        for m in desiredMasses:
            result = np.vstack((result, self.m_interpolatedData[m]))
        # return np.concatenate((self.m_correctedTemp,self.m_parsedRawData[self.m_listOfColumns.index('temperature')+1:,:]))
        return result

    def getProcessedArrheniusData(self, desiredMasses):
        result = self.m_reciprocalTemp
        for m in desiredMasses:
            result = np.vstack((result, self.m_logInterpolatedData[m]))
        return result

    def getCoverageLabels(self, desiredMasses):
        result = []
        for m in desiredMasses:
            if self.m_coveragesNormalized:
                result.append("M" + m + ' {:04.2f} ML'.format(self.m_coverages[m]))
            else:
                result.append("M" + m + " " + self.m_parsedCoverage)
                # result.append("M" + m + ' {:f} Counts'.format(self.m_coverages[m]))
        return result

    def getLangmuirLabels(self, desiredMasses):
        result = []
        for m in desiredMasses:
            result.append("M" + m + " " + self.m_parsedCoverage)
        return result
    # def saveProcessedData(self, massList = None, filename = None):
    #     #use tkFileDialog.asksaveasfile
    #     if not self.m_dataProcessed:
    #         return
    #     if(filename == None):
    #         filename = self.m_fileName + '_processed.csv'
    #     substrings = self.m_filePath.split('/')
    #     outputFilePath = ""
    #     for s in substrings[:-1]:
    #         outputFilePath = outputFilePath + s + '/'
    #     outputFilePath = outputFilePath + filename

    #     headerString = "Temperature"
    #     if (massList == None):
    #         massList = self.getMassList()
    #     for m in massList:
    #         headerString = headerString + " " + m
    #     headerString += "\n 0"
    #     for m in massList:
    #         headerString = headerString + " " + str(self.m_coverages[m])

    #     output = self.m_interpolatedTemp
    #     for m in massList:
    #         output = np.vstack((output, self.m_interpolatedData[m]))

    #     np.savetxt(outputFilePath, output.transpose(), delimiter=',', header=headerString)







