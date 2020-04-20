import numpy as np
import threading

class ProcessedDataWrapper():
    def __init__(self, filePath):
        self.m_filePath = filePath
        substrings = filePath.split('/')
        self.m_fileName = substrings[len(substrings) - 1]
        self.m_dataParsed = False
        self.m_dataInverted = False
        self.m_listOfColumns = []
        self.m_parsedInputData = []
        self.m_totalCoverages = []
        self.m_coverages = {} #dictionary to connect dataset with prefactor as key
        self.m_desorptionEnergies = {} #dictionary to connect dataset with prefactor as key

    def parseProcessedDataFile(self):
        if(self.m_dataParsed):
            return
        firstHeaderLine =  np.loadtxt(self.m_filePath, dtype=str, max_rows=1, comments=None) #ignoring comments because we want to load the header
        self.m_mass = int(firstHeaderLine[-1]) #last part of first header line is mass number
        secondHeaderLine =  np.loadtxt(self.m_filePath, dtype=str, skiprows=1, max_rows=1, comments=None) #ignoring comments, same as before
        headerLength = int (secondHeaderLine[-1]) #last part of second header line is header length

        firstTwoLines = np.loadtxt(self.m_filePath, dtype=str, max_rows=2)
        self.m_listOfColumns = firstTwoLines[0,:]
        self.m_totalCoverages = [float(c) for c in firstTwoLines[1,:]]

        temp = np.loadtxt(self.m_filePath, dtype = float, skiprows= headerLength + 2)
        
        #now columns can be traversed contiguously in memory
        self.m_parsedInputData = temp.transpose().copy()
        self.m_dataParsed = True

    def getInputData(self):
        return self.m_parsedInputData

    def clearInvertedData(self):
        self.m_coverages = {} #dictionary to connect dataset with prefactor as key
        self.m_desorptionEnergies = {} #dictionary to connect dataset with prefactor as key

    def invertProcessedData(self, prefactor, rampRate = 1, gasConstant_R = 8.314):
        #gas constant R in J/mol/K
        #ramp rate in K/s
        # coverageBuffer = np.zeros(shape=self.m_parsedInputData.shape)
        # desorptionEnergiesBuffer = np.zeros(shape=self.m_parsedInputData.shape)
        self.m_coverages[str(prefactor)] = np.zeros(shape=self.m_parsedInputData.shape)
        self.m_desorptionEnergies[str(prefactor)] = np.zeros(shape=self.m_parsedInputData.shape)

        #calculate coverage vs temperature
        for i in range(len(self.m_totalCoverages)-1):
            self.m_coverages[str(prefactor)][i,:] = np.array([self.m_totalCoverages[i+1] - np.trapz(self.m_parsedInputData[i+1,:j],x=self.m_parsedInputData[0,:j]) for j in range(self.m_parsedInputData.shape[1])])
        # if (len(self.m_totalCoverages) > 1): #if we have multiple datasets, go through all of them
        factor1 = (rampRate * prefactor)
        factor2 = - gasConstant_R * 0.001 * 0.01036410 #factor for eV
        for i in range(len(self.m_totalCoverages)-1):
            temp = self.m_parsedInputData[i+1,:] / self.m_coverages[str(prefactor)][i,:] / factor1
            # self.m_coverages = np.vstack((self.m_totalCoverages,np.trapz(self.m_parsedInputData[i,:],x=self.m_parsedInputData[0,:]) - self.m_totalCoverages[i]))
            self.m_desorptionEnergies[str(prefactor)][i,:] = factor2 * self.m_parsedInputData[0,:] * np.log(temp)

        # self.m_coverages[str(prefactor)] = coverageBuffer
        # self.m_desorptionEnergies[str(prefactor)] = desorptionEnergiesBuffer
        #E_des(:,i)=-R.*temp.*log(des_rate(:,i)./(ramp_rate.*pref_fce.*coverage_fc(:,i)))*0.001;% in kJ/mol

    def getCoverageVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_coverages[str(prefactor)]))

    def getDesEnergyVSCoverageList(self, prefactor):
        result = []
        for i in range(len(self.m_totalCoverages)-1):
            result.append(np.vstack((self.m_coverages[str(prefactor)][i,:],self.m_desorptionEnergies[str(prefactor)][i,:])))
        return result

    def saveInvertedDataToFile(self,outputFilePath):
        if(outputFilePath == None):
            raise ValueError
        
        #keys are prefactors
        for k in self.m_desorptionEnergies.keys():
            headerString = "Processed TPD data for mass " + str(self.m_mass) + \
                "\nHeader length is " + str(4) + \
                "\nPrefactor is " + "{:e}".format(k) + \
                "\nA temperature column is followed by pairs of coverage and desorption energy columns:\n"
            #outputData starts out column-major
            outputData = self.m_parsedInputData[0,:].copy() # start with temperature column
            labels = ["Temperature"]
            coverages = [str(0.0)]
            for i in range(len(self.m_totalCoverages) - 1):
                # headerString = headerString + w.m_fileName + "\n" #write filename to header for quick overview
                outputData = np.vstack((outputData, self.m_coverages[k][i,:], self.m_desorptionEnergies[k][i,:])) #append data column for coverage and then mass
                labels.append("Coverage") # append total coverage once for coverage column
                labels.append("EDes") # append total coverage a second time for desorption energy column
                coverages.append(str(self.m_totalCoverages[i+1])) # append total coverage once for coverage column
                coverages.append(str(self.m_totalCoverages[i+1])) # append total coverage a second time for desorption energy column

            #make one file per mass
            namedOutputFilePath = outputFilePath + ".M" + str(self.m_mass) + "Prefactor_" + "{:e}".format(k) + ".invdat" #pdat for processed data
            stringData = np.vstack((np.array(labels,dtype=str),np.array(coverages,dtype=str)))

            with open(namedOutputFilePath, mode='a') as fileHandle:
                #write header and stringData first
                np.savetxt(fileHandle, stringData, fmt="%s", delimiter=' ', header=headerString)
                #then write float data (after transposing it)
                np.savetxt(fileHandle, outputData.transpose(), delimiter=' ')
