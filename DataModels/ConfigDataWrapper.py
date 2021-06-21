import numpy as np

#This class is probably superfluous as we have decided to store calibration data directly in a processed data file.
class ConfigDataWrapper():
    def __init__(self,filePath):
        self.m_filepath = filePath
        #TODO: the various temperature calibration data points should be stored in the config

    def loadFromFile(filePath):
        pass

    def savetoFile(filePath):
        pass
