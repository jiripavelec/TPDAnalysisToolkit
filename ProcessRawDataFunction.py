import numpy as np

class RawDataWrapper():
    def __init__(self, filePath, tRampStart, tRampEnd, tCutStart, tCutEnd, tStep, listOfMasses):
        self.m_filePath = filePath
        self.m_tRampStart = tRampStart
        self.m_tRampEnd = tRampEnd
        self.m_tCutStart = tCutStart
        self.m_tCutEnd = tCutEnd
        self.m_tStep = tStep
        self.m_listOfMasses = listOfMasses

    def running_average(self, x, N):
        cumsum = np.cumsum(np.insert(x, 0, 0)) 
        return (cumsum[N:] - cumsum[:-N]) / float(N)

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
        self.m_parsedData = temp.transpose().copy()
        print(self.m_parsedData.shape) #for debugging
        del temp #free memory, or at least suggest it to the garbage collector

    def getRawData(self):
        temp = self.m_parsedData[self.m_listOfColumns.index('temperature'):,:]
        return temp

    def processParsedData(self):
        # self.m_correctedTemp = np.zeros(self.m_parsedData.shape[1])
        # correct temperature (taken from Honza's scripts)
        self.m_correctedTemp = np.array(self.m_parsedData[(self.m_listOfColumns.index('temperature')),:])
        self.m_correctedTemp *= 0.985
        self.m_correctedTemp += 0.836

        #get running average from temperature data
        self.m_correctedTemp = self.running_average(self.m_correctedTemp, 20)

        print(self.m_correctedTemp.item(0), self.m_parsedData.item((self.m_listOfColumns.index('temperature'),0))) #debugging

    def getProcessedData(self):
        return np.concatenate(self.m_correctedTemp,self.m_parsedData[self.m_listOfColumns.index('temperature')+1:,:])





