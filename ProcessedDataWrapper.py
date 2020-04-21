import numpy as np
import threading

class ProcessedDataWrapper():
    def __init__(self, filePath):
        self.m_filePath = filePath
        substrings = filePath.split('/')
        self.m_fileName = substrings[len(substrings) - 1]
        self.m_dataParsed = False #data has been parsed?
        self.m_dataInverted = False #data has been inverted?
        self.m_normalized = False #input data is normalized?
        self.m_dataSimulated = False #simulation done?
        self.m_listOfColumns = [] #labels for columns
        self.m_parsedInputData = [] #effectively experimental desorption rate normalized to units of 1ML
        self.m_totalCoverages = [] #total coverage for an input data column
        self.m_expCoverages = {} #dictionary to connect dataset with prefactor as key, coverage(temp), from experiment
        self.m_desorptionEnergies = {} #dictionary to connect dataset with prefactor as key
        self.m_simCoverages = {} #dictionary to connect dataset with prefactor as key, coverage(temp), from simulation
        self.m_simDesorptionRate = {} #dictionary to connect dataset with prefactor as key, dTheta/dT, from sim
        self.m_chiSquared = {}

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
        if not (1.0 in self.m_totalCoverages):
            self.m_normalized = False
            raise ValueError
        else:
            self.m_normalized = True

        temp = np.loadtxt(self.m_filePath, dtype = float, skiprows= headerLength + 2)
        
        #now columns can be traversed contiguously in memory
        self.m_parsedInputData = temp.transpose().copy()
        self.m_dataParsed = True

    def getInputData(self):
        return self.m_parsedInputData

    def clearInvertedData(self):
        self.m_expCoverages = {} #dictionary to connect dataset with prefactor as key
        self.m_desorptionEnergies = {} #dictionary to connect dataset with prefactor as key

    def invertProcessedData(self, prefactor, rampRate = 1, gasConstant_R = 8.314):
        #gas constant R in J/mol/K
        #ramp rate in K/s
        # coverageBuffer = np.zeros(shape=self.m_parsedInputData.shape)
        # desorptionEnergiesBuffer = np.zeros(shape=self.m_parsedInputData.shape)
        self.m_expCoverages[str(prefactor)] = np.zeros(shape=self.m_parsedInputData.shape)
        self.m_desorptionEnergies[str(prefactor)] = np.zeros(shape=self.m_parsedInputData.shape)

        #calculate coverage vs temperature
        for i in range(len(self.m_totalCoverages)-1):
            self.m_expCoverages[str(prefactor)][i,:] = np.array([self.m_totalCoverages[i+1] - np.trapz(self.m_parsedInputData[i+1,:j],x=self.m_parsedInputData[0,:j]) for j in range(self.m_parsedInputData.shape[1])])
        # if (len(self.m_totalCoverages) > 1): #if we have multiple datasets, go through all of them
        factor1 = (rampRate * prefactor)
        factor2 = - gasConstant_R * 0.001 * 0.01036410 #factor for eV
        for i in range(len(self.m_totalCoverages)-1):
            temp = self.m_parsedInputData[i+1,:] / self.m_expCoverages[str(prefactor)][i,:] / factor1
            # self.m_expCoverages = np.vstack((self.m_totalCoverages,np.trapz(self.m_parsedInputData[i,:],x=self.m_parsedInputData[0,:]) - self.m_totalCoverages[i]))
            self.m_desorptionEnergies[str(prefactor)][i,:] = factor2 * self.m_parsedInputData[0,:] * np.log(temp)

        # self.m_expCoverages[str(prefactor)] = coverageBuffer
        # self.m_desorptionEnergies[str(prefactor)] = desorptionEnergiesBuffer
        #E_des(:,i)=-R.*temp.*log(des_rate(:,i)./(ramp_rate.*pref_fce.*coverage_fc(:,i)))*0.001;% in kJ/mol
        self.m_dataInverted = True

    def getExpCoverageVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_expCoverages[str(prefactor)]))

    def getExpDesorptionRateVSTemp(self):
        return self.m_parsedInputData

    def getDesEnergyVSCoverageList(self, prefactor):
        result = []
        for i in range(len(self.m_totalCoverages)-1):
            result.append(np.vstack((self.m_expCoverages[str(prefactor)][i,:],self.m_desorptionEnergies[str(prefactor)][i,:])))
        return result

    def saveInvertedDataToFile(self,outputFilePath):
        if(outputFilePath == None):
            raise ValueError
        
        #keys are prefactors
        for k in self.m_desorptionEnergies.keys():
            headerString = "Processed TPD data for mass " + str(self.m_mass) + \
                "\nHeader length is " + str(4) + \
                "\nPrefactor is " + "{:e}".format(k) + \
                "\nA temperature column is followed by pairs of coverage and desorption energy columns:"
            #outputData starts out column-major
            outputData = self.m_parsedInputData[0,:].copy() # start with temperature column
            labels = ["Temperature"]
            coverages = [str(0.0)]
            for i in range(len(self.m_totalCoverages) - 1):
                # headerString = headerString + w.m_fileName + "\n" #write filename to header for quick overview
                outputData = np.vstack((outputData, self.m_expCoverages[k][i,:], self.m_desorptionEnergies[k][i,:])) #append data column for coverage and then mass
                labels.append("Coverage_" + self.m_listOfColumns[i]) # append total coverage once for coverage column
                labels.append("EDes_" + self.m_listOfColumns[i]) # append total coverage a second time for desorption energy column
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

    def polanyiWigner(self,prefactor,coverageRow,monolayerCoverage,monolayerDesEnergy,temperature,eCharge = 1.6022e-19,kBoltz=1.3806e-23):
        return -prefactor*coverageRow*np.exp(-np.interp(coverageRow,monolayerCoverage,monolayerDesEnergy)*eCharge/(kBoltz*temperature))

    def simulateCoveragesFromInvertedData(self, tStep = 0.1):
        if (not self.m_dataInverted):
            raise ValueError #we need to perform inversion before simulation and evaluation

        monolayerIndex = self.m_totalCoverages.index(1.0) #index of the data column associated with 1ML coverage
        temperature = self.m_parsedInputData[0,:] #temperature data column
        for k in self.m_expCoverages.keys():
            monolayerCoverage = self.m_expCoverages[k][monolayerIndex,:] #should be same every time
            monolayerDesEnergy = self.m_desorptionEnergies[k][monolayerIndex,:] #should be different every time
            floatPrefactor = float(k)
            self.m_simCoverages[k] = np.zeros(shape=(len(temperature), len(self.m_totalCoverages) - 1))
            self.m_simDesorptionRate[k] = self.m_simCoverages[k].copy() #start with zeros and same shape
            self.m_simCoverages[k][0,:] = self.m_totalCoverages[1:] #starting values for coverages
            for i in range(len(temperature) - 1):
                refSimCoverageRow = self.m_simCoverages[k][i,:]
                #RK4 integration
                k1 = self.polanyiWigner(floatPrefactor,
                                        refSimCoverageRow,
                                        monolayerCoverage,
                                        monolayerDesEnergy,
                                        temperature[i])
                k2 = self.polanyiWigner(floatPrefactor,
                                        refSimCoverageRow + 0.5*tStep*k1,
                                        monolayerCoverage,
                                        monolayerDesEnergy,
                                        temperature[i] + 0.5*tStep)
                k3 = self.polanyiWigner(floatPrefactor,
                                        refSimCoverageRow + 0.5*tStep*k2,
                                        monolayerCoverage,
                                        monolayerDesEnergy,
                                        temperature[i] + 0.5*tStep)
                k4 = self.polanyiWigner(floatPrefactor,
                                        refSimCoverageRow + tStep*k3,
                                        monolayerCoverage,
                                        monolayerDesEnergy,
                                        temperature[i] + tStep)
                self.m_simDesorptionRate[k][i,:] = - k1.copy()
                newSimCoverageRow = refSimCoverageRow + (1.0/6.0)*(k1+ 2.0*k2 + 2.0*k3 + k4)*tStep
                done = False
                for c in newSimCoverageRow:
                    if c <= 0.0: #if simulated coverage is zero we have effectively desorbed the original dosed coverage
                        c = 0
                        done = True
                self.m_simCoverages[k][i+1,:] = newSimCoverageRow # write new row to simulated data array
                if done:
                    break
            self.m_simCoverages[k] = self.m_simCoverages[k].transpose().copy() #column major now
            self.m_simDesorptionRate[k] = self.m_simDesorptionRate[k].transpose().copy() #column major now
        self.m_dataSimulated = True #simulation done?

    def getSimCoverageVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_simCoverages[str(prefactor)]))

    def getSimDesRateVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_simDesorptionRate[str(prefactor)]))

    def evaluateData(self):
        if not self.m_dataSimulated:
            raise ValueError #cant evaluate before simulation
        for k in self.m_expCoverages.keys():
            self.m_chiSquared[k] = np.zeros(len(self.m_totalCoverages) - 1)
            for i in range(len(self.m_totalCoverages) - 1):
                sim = self.m_simDesorptionRate[k][i,:] #simulated desorption rate
                obs = self.m_parsedInputData[i+1,:] #observed desorption rate
                difference = sim - obs
                diffSquared = difference*difference
                self.m_chiSquared[k][i] = np.cumsum(np.where(not obs == 0.0, diffSquared/obs, diffSquared/np.finfo(float).eps))

    def getChiSquaredVSPrefactor(self):
        prefactorList = self.m_chiSquared.keys()
        result = np.zeros((len(prefactorList),len(self.m_chiSquared[prefactorList[0]])))
        for i in range(len(prefactorList)):
            for j in range(len(self.m_chiSquared[prefactorList[i]])):
                result[i,j] = self.m_chiSquared[prefactorList[i]][j]
        return result.transpose().copy()
                
                
                

