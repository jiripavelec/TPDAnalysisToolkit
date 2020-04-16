import numpy as np

class ProcessedDataWrapper():
    def __init__(self, filePath):
        self.m_filePath = filePath
        substrings = filePath.split('/')
        self.m_fileName = substrings[len(substrings) - 1]
        self.m_dataParsed = False
        self.m_dataInverted = False
        self.m_listOfColumns = []
        self.m_inputData = {}
        self.m_coverages = {}
        self.m_temperatureData = []

    def parseProcessedDataFile(self):
        if(self.m_dataParsed):
            return
        raise NotImplementedError

    def getInputData(self):
        raise NotImplementedError

    def getMassList(self):
        raise NotImplementedError

    def massListToIndices(self, massList):
        raise NotImplementedError

    def invertProcessedData(self):
        raise NotImplementedError

    def getInvertedData(self):
        raise NotImplementedError
