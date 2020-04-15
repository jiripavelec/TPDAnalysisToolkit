import numpy as np

class ProcessedDataWrapper():
    def __init__(self, filePath = None, rawDataWrapper = None):
        if(not rawDataWrapper == None):
            self.m_dataParsed = True
            self.m_fileName = rawDataWrapper.m_fileName
            self.m_filePath = rawDataWrapper.m_filePath
            self.m_listOfColumns = rawDataWrapper.m_listOfColumns
            self.m_coverages = rawDataWrapper.m_coverages
            self.m_inputData = rawDataWrapper.m_interpoaltedData
            self.m_temperatureData = rawDataWrapper.m_interpolatedTemp
        elif (not filePath == None):
            self.m_dataParsed = False
        else:#crappy input
            raise ValueError

    def parseProcessedDataFile(self):
        if(self.m_dataParsed):
            return
        raise NotImplementedError

    def getProcessedData(self):
        raise NotImplementedError

    def getMassList(self):
        raise NotImplementedError

    def massListToIndices(self, massList):
        raise NotImplementedError

    def invertProcessedData(self):
        raise NotImplementedError

    def getInvertedData(self):
        raise NotImplementedError
