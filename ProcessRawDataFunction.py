import numpy as np

class RawDataWrapper():
    def __init__(self, filePath):
        self.m_filePath = filePath
        # self.m_tRampStart = tRampStart
        # self.m_tRampEnd = tRampEnd
        # self.m_tCutStart = tCutStart
        # self.m_tCutEnd = tCutEnd
        # self.m_tStep = tStep
        self.m_dataProcessed = False
        self.m_interpolatedData = {}

    def smooth(self, x, N): #running average
        cumsum = np.cumsum(np.insert(x, 0, 0)) 
        smoothResult = (cumsum[N:] - cumsum[:-N]) / float(N)
        smoothResult = np.insert(smoothResult,0,x[:N-1])
        smoothResult = np.append(smoothResult,x[N:-1:-1])
        return smoothResult

    def parseRawDataFile(self):
        self.m_headerData = np.loadtxt(self.m_filePath,dtype=str, skiprows=1,max_rows=1, delimiter=',')
         #second item is the number of lines remaining in the header after the second line
        headerLength = int(self.m_headerData.item(1))

        m_parsedDataTitles = np.loadtxt(self.m_filePath,dtype=str, skiprows=headerLength + 1,max_rows=1, delimiter=',')
        self.m_listOfColumns = [t for t in [e.strip("\'\"") for e in m_parsedDataTitles.tolist()] if not t == '']
        self.m_listOfColumns.remove('Time') #we are ignornign the first column
        print(self.m_listOfColumns) #for debugging

        #parsed data is in row major format i.e. time(ms),temp, m1, m2, m3...
        temp = np.loadtxt(self.m_filePath, dtype = float, skiprows=36, delimiter=',', usecols=range(1,len(self.m_listOfColumns)+1))

        #now columns can be traversed contiguously in memory
        self.m_parsedRawData = temp.transpose().copy()
        print(self.m_parsedRawData.shape) #for debugging
        del temp #free memory, or at least suggest it to the garbage collector

    def getRawData(self, desiredMasses):
        temp = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        for i in self.massListToIndices(desiredMasses):
            temp = np.vstack((temp, self.m_parsedRawData[i,:]))
        return temp

    def getMassList(self):
        return self.m_listOfColumns[2:] #first two columns are "ms" and "temperature"

    def massListToIndices(self, massList):
        return [self.m_listOfColumns.index(m) for m in massList]

    def processParsedData(self, tRampStart, tRampEnd, tCutStart, tCutEnd, removeBackground, smooth, smoothpoints = 5, tStep = 0.1):
        # self.m_correctedTemp = np.zeros(self.m_parsedRawData.shape[1])
        # correct temperature (taken from Honza's scripts)
        self.m_correctedTemp = np.array(self.m_parsedRawData[(self.m_listOfColumns.index('temperature')),:])
        self.m_correctedTemp *= 0.985
        self.m_correctedTemp += 0.836
        print(self.m_correctedTemp.shape) #for debugging

        #get running average from temperature data
        self.m_correctedTemp = self.smooth(self.m_correctedTemp, 20)
        print(self.m_correctedTemp.shape) #for debugging

        print(self.m_correctedTemp.item(0), self.m_parsedRawData.item((self.m_listOfColumns.index('temperature'),0))) #debugging

        tempSearchInput = np.abs(self.m_correctedTemp - tRampStart)
        tRampStartIndex = np.argwhere(tempSearchInput == np.amin(tempSearchInput))[-1][0]

        while self.m_correctedTemp[tRampStartIndex + 1] > self.m_correctedTemp[tRampStartIndex]:
            tRampStartIndex -= 1 # find lowest index of the ramp
            if(tRampStartIndex == 0): break

        tempSearchInput = np.abs(self.m_correctedTemp - tRampEnd)
        tRampEndIndex = np.argwhere(tempSearchInput == np.amin(tempSearchInput))[-1][0]

        del tempSearchInput #no need to waste memory

        while self.m_correctedTemp[tRampEndIndex - 1] < self.m_correctedTemp[tRampEndIndex]:
            tRampEndIndex += 1 # find highest index of the ramp
            if(tRampEndIndex == self.m_correctedTemp.size - 1): break

        #TODO: cut data by finding correct temperature, taking its index => then the time
        self.m_desiredTempValues = np.arange(tCutStart, tCutEnd, tStep)
        for m in self.getMassList():
            temp = np.interp(self.m_desiredTempValues, self.m_correctedTemp[tRampStartIndex:tRampEndIndex],
                self.m_parsedRawData[self.m_listOfColumns.index(m),tRampStartIndex:tRampEndIndex])
            if smooth:
                temp = self.smooth(temp, smoothpoints)
            if removeBackground:
                temp -= np.amin(temp)
            self.m_interpolatedData[m] = temp
        self.m_dataProcessed = True


    def getProcessedData(self, desiredMasses):
        result = self.m_desiredTempValues
        # for i in self.massListToIndices(desiredMasses):
        for m in desiredMasses:
            result = np.vstack((result, self.m_interpolatedData[m]))
        # return np.concatenate((self.m_correctedTemp,self.m_parsedRawData[self.m_listOfColumns.index('temperature')+1:,:]))
        return result




