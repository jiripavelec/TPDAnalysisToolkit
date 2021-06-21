import numpy as np
import threading
import multiprocessing

#As defined in the name this class wraps the processed data file.
#It provides methods for further processing of this data, for example inversion analysis.
#Potentially look at the RawDataWrapper first if this class is too confusing.
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
        self.m_includedFiles = []

    def parseProcessedDataFile(self):
        if(self.m_dataParsed):
            return True
        try: #try parsing so we can return false if we catch an exception
            firstHeaderLine =  np.loadtxt(self.m_filePath, dtype=str, max_rows=1, comments=None) #ignoring comments because we want to load the header
            self.m_mass = int(firstHeaderLine[-1]) #last part of first header line is mass number
            secondHeaderLine =  np.loadtxt(self.m_filePath, dtype=str, skiprows=1, max_rows=1, comments=None) #ignoring comments, same as before
            headerLength = int (secondHeaderLine[-1]) #last part of second header line is header length

            for i in range(3, headerLength-1):
                includedFileNameBuffer = np.loadtxt(self.m_filePath, dtype=str, skiprows=i, max_rows = 1, comments= None)
                self.m_includedFiles.append(' '.join(includedFileNameBuffer[2:]))#ignore '# ' before line

            firstTwoLines = np.loadtxt(self.m_filePath, dtype=str, max_rows=2)
            self.m_listOfColumns = firstTwoLines[0,:]
            self.m_totalCoverages = [float(c) for c in firstTwoLines[1,:]]
            if not (1.0 in self.m_totalCoverages):
                self.m_normalized = False
            else:
                self.m_normalized = True
            temp = np.loadtxt(self.m_filePath, dtype = float, comments = None, skiprows= headerLength + 2)
            #now columns can be traversed contiguously in memory
            self.m_parsedInputData = temp.transpose().copy()
            self.m_dataParsed = True
            return True
        except Exception:
            return False
        return False

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
            temp = self.m_parsedInputData[i+1,:] / (self.m_expCoverages[str(prefactor)][i,:] * factor1)
            # self.m_expCoverages = np.vstack((self.m_totalCoverages,np.trapz(self.m_parsedInputData[i,:],x=self.m_parsedInputData[0,:]) - self.m_totalCoverages[i]))
            self.m_desorptionEnergies[str(prefactor)][i,:] = factor2 * self.m_parsedInputData[0,:] * np.log(temp)
            # self.m_desorptionEnergies[str(prefactor)][i,np.where(self.m_expCoverages[str(prefactor)][i,:] == self.m_totalCoverages[i+1])] = 0.0 #set desorption energy to zero where coverage stays constant (i.e. temperatures below desorption peaks)

        # self.m_expCoverages[str(prefactor)] = coverageBuffer
        # self.m_desorptionEnergies[str(prefactor)] = desorptionEnergiesBuffer
        #E_des(:,i)=-R.*temp.*log(des_rate(:,i)./(ramp_rate.*pref_fce.*coverage_fc(:,i)))*0.001;% in kJ/mol
        self.m_dataInverted = True

    def getExpCoverageVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_expCoverages[str(prefactor)][:-1,:]))

    def getExpDesorptionRateVSTemp(self):
        return self.m_parsedInputData

    def fileNameToExpDesorptionRateVSTemp(self, fileName):
        try:
            index = self.m_includedFiles.index(fileName) + 1
            return np.vstack((self.m_parsedInputData[0,:],self.m_parsedInputData[index,:]))
        except:
            return None

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
                "\nPrefactor is " + "{:e}".format(float(k)) + \
                "\nA temperature column is followed by pairs of coverage and desorption energy columns:"
            #outputData starts out column-major
            outputData = self.m_parsedInputData[0,:].copy() # start with temperature column
            labels = ["Temperature"]
            coverages = [str(0.0)]
            for i in range(len(self.m_totalCoverages) - 1):
                # headerString = headerString + w.m_fileName + "\n" #write filename to header for quick overview
                outputData = np.vstack((outputData, self.m_expCoverages[k][i,:], self.m_desorptionEnergies[k][i,:])) #append data column for coverage and then mass
                labels.append("Coverage_" + self.m_listOfColumns[i+1]) # append total coverage once for coverage column
                labels.append("EDes_" + self.m_listOfColumns[i+1]) # append total coverage a second time for desorption energy column
                coverages.append(str(self.m_totalCoverages[i+1])) # append total coverage once for coverage column
                coverages.append(str(self.m_totalCoverages[i+1])) # append total coverage a second time for desorption energy column

            #make one file per mass
            namedOutputFilePath = outputFilePath + ".M" + str(self.m_mass) + "Prefactor_" + "{:e}".format(float(k)) + ".invdat" #pdat for processed data
            stringData = np.vstack((np.array(labels,dtype=str),np.array(coverages,dtype=str)))

            with open(namedOutputFilePath, mode='a') as fileHandle:
                #write header and stringData first
                np.savetxt(fileHandle, stringData, fmt="%s", delimiter=' ', header=headerString)
                #then write float data (after transposing it)
                np.savetxt(fileHandle, outputData.transpose(), delimiter=' ')

    #Represents the polanyi wigner equation. Used for the Runga-Kutta integration.
    def polanyiWigner(self,prefactor,coverageRow,monolayerCoverage,monolayerDesEnergy,temperature,eCharge = 1.6022e-19,kBoltz=1.3806e-23):
        interpolatedEnergyInEV = np.interp(coverageRow,monolayerCoverage,monolayerDesEnergy)
        result = -prefactor*coverageRow*np.exp(-interpolatedEnergyInEV*(eCharge/kBoltz)/temperature)
        return result

    #Effectively this is the heart of inversion analysis. It is an RK4 integrator.
    #This function is called in the following function, depending on whether we have multiple prefactors and multiple available threads.
    def simulateCoverageFromInvertedDataForSinglePrefactor(self, strPrefactor, tStep = 0.1):
        monolayerIndex = self.m_totalCoverages.index(1.0) - 1 #index of the data column associated with 1ML coverage            
        # self.m_monolayerIndex = self.m_totalCoverages.index(1.0) - 1 #index of the data column associated with 1ML coverage
        # self.m_totalCoverages[self.m_monolayerIndex] = 1.0-np.finfo(float).eps
        # monolayerIndex = self.m_monolayerIndex #index of the data column associated with 1ML coverage
        temperature = self.m_parsedInputData[0,:] #temperature data column
        monolayerCoverage = self.m_expCoverages[strPrefactor][monolayerIndex,::-1].copy() #should be same every time
        monolayerDesEnergy = self.m_desorptionEnergies[strPrefactor][monolayerIndex,::-1].copy() #should be different every time
        floatPrefactor = float(strPrefactor)
        simCoverageBuffer = np.zeros(shape=(len(temperature), len(self.m_totalCoverages) - 1))
        simDesorptionRateBuffer = simCoverageBuffer.copy() #start with zeros and same shape
        simCoverageBuffer[0,:] = self.m_totalCoverages[1:] #starting values for coverages
        simCoverageBuffer[np.where(simCoverageBuffer == 1.0)] -= 0.0001
        for i in range(len(temperature) - 1):
            refSimCoverageRow = simCoverageBuffer[i,:]
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
            simDesorptionRateBuffer[i,:] = - k1.copy()
            # for e in self.m_simDesorptionRate[k][i,:]:
            #     if e >= 1.0:
            #         e = 0.0
            newSimCoverageRow = refSimCoverageRow + (1.0/6.0)*(k1+ 2.0*k2 + 2.0*k3 + k4)*tStep
            for j in range(len(newSimCoverageRow)):
                if newSimCoverageRow[j] < 1.0e-6: #don't care about smaller values, effectively is zero 
                    newSimCoverageRow[j] = 0.0
                if newSimCoverageRow[j] > 1.0: #at some point the simulation diverges
                    newSimCoverageRow[j] = 0.0

            simCoverageBuffer[i+1,:] = newSimCoverageRow.copy() # write new row to simulated data array

        return strPrefactor, simCoverageBuffer.transpose().copy() , simDesorptionRateBuffer.transpose().copy() #column major now

    #This is somewhat like a dispatching function for the inversion analysis. One thread per pre-factor on basis of the if-branch-conditions.
    def simulateCoveragesFromInvertedData(self):
        if (not self.m_dataInverted):
            raise ValueError #we need to perform inversion before simulation and evaluation

        prefactorList = list(self.m_expCoverages)

        if( len(prefactorList) == 1): #only one prefactor
            trash, self.m_simCoverages[prefactorList[0]], self.m_simDesorptionRate[prefactorList[0]] = self.simulateCoverageFromInvertedDataForSinglePrefactor(prefactorList[0]) #column major now
        else: #try multiprocessing
            cpu_count = multiprocessing.cpu_count()
            if( cpu_count == 1): #single-core
                for k in prefactorList:
                    trash, self.m_simCoverages[k], self.m_simDesorptionRate[k] = self.simulateCoverageFromInvertedDataForSinglePrefactor(k) #column major now
            else: #try using as many cores as there are prefactors, or at least as many cores as we have (minus one for UI thread)
                print("Using " + str(min(cpu_count - 1, len(prefactorList))) + " processes!") #debug
                with multiprocessing.Pool(min(cpu_count - 1, len(prefactorList))) as p:
                    # keys, simCoverages, simDesorptionRates = p.map(self.simulateCoverageFromInvertedDataForSinglePrefactor, prefactors)
                    results = p.map(self.simulateCoverageFromInvertedDataForSinglePrefactor, prefactorList)
                    for r in results: #r[0] is the prefactor key, r[1] is the simCoverage, r[2] is the simDesorptionRate
                        self.m_simCoverages[r[0]] = r[1]
                        self.m_simDesorptionRate[r[0]] = r[2]
        self.m_dataSimulated = True #simulation done?

    def getSimCoverageVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_simCoverages[str(prefactor)]))

    def getSimDesRateVSTemp(self, prefactor):
        return np.vstack((self.m_parsedInputData[0,:],self.m_simDesorptionRate[str(prefactor)]))

    #Here we calulcate the chi-squared as the last step of the inversion analysis.
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
                # self.m_chiSquared[k][i] = np.sum(np.where( obs != 0.0, diffSquared/obs, diffSquared/np.finfo(float).eps))
                # self.m_chiSquared[k][i] = np.sum(np.where( obs > 1.0e-6, diffSquared/obs, diffSquared/np.finfo(float).eps))
                self.m_chiSquared[k][i] = np.sum(np.where( obs > 1.0e-6, diffSquared/obs, 0))
                # if self.m_chiSquared[k][i] > 1000:
                #     print("Wierd chiSquared")

    def getChiSquaredVSPrefactor(self):
        prefactorList = list(self.m_chiSquared) #this returns the keys of the dictionary as an indexable list
        dataPointsPerPrefactor = len(self.m_chiSquared[prefactorList[0]]) - 1 #-1 because we don't want the chisquared for the monolayer coverage
        result = np.zeros((len(prefactorList),dataPointsPerPrefactor))
        #result[0,:]
        for i in range(len(prefactorList)):
            for j in range(dataPointsPerPrefactor):
                result[i,j] = self.m_chiSquared[prefactorList[i]][j]
        result = np.vstack((np.array([float(p) for p in prefactorList]),result.transpose()))
        return result

    def getChiSquaredSumVSPrefactor(self):
        prefactorList = list(self.m_chiSquared) #this returns the keys of the dictionary as an indexable list
        result = np.zeros(len(prefactorList))
        for i in range(len(prefactorList)):
            for j in range(len(self.m_chiSquared[prefactorList[i]]) - 1): #-1 because we don't want the chisquared for the monolayer coverage
                result[i] += self.m_chiSquared[prefactorList[i]][j] #sum of chi squared values for a prefactor
        result = np.vstack((np.array([float(p) for p in prefactorList]),result.transpose()))
        return result


    def getCoverageLabels(self):
        result = []
        for c in self.m_totalCoverages[1:]:
            result.append("M" + str(self.m_mass) + ' {:04.2f} ML'.format(c))
        return result

    def fileNameToCoverageLabel(self, fileName):
        try:
            index = self.m_includedFiles.index(fileName) + 1
            c = self.m_totalCoverages[index]
            return "M" + str(self.m_mass) + ' {:04.2f} ML'.format(c)
        except:
            return None

    def getMinTemp(self):
        return self.m_parsedInputData[0,0]

    def getMaxTemp(self):
        return self.m_parsedInputData[0,-1]

    def getProcessedDataBetweenForFile(self, t1, t2, fileName):
        try:
            dataIndex = self.m_includedFiles.index(fileName) + 1
            indices = np.where((self.m_parsedInputData[0,:] > t1) & (self.m_parsedInputData[0,:] < t2))[0]
            idx1 = indices[0]
            idx2 = indices[-1]
            result = (self.m_parsedInputData[0,idx1:idx2],self.m_parsedInputData[dataIndex,idx1:idx2])
            return result
        except:
            return None

    def integrateDesorptionRate(self, t1, t2, fileName):
        try:
            # dataIndex = self.m_includedFiles.index(fileName) + 1
            # indices = np.where((self.m_parsedInputData[0,:] > t1) & (self.m_parsedInputData[0,:] < t2))[0]
            # # idx1 = np.where(self.m_parsedInputData[0,:] == t1)
            # # idx2 = np.where(self.m_parsedInputData[0,:] == t2)
            # idx1 = indices[0]
            # idx2 = indices[-1]
            # result = np.trapz(self.m_parsedInputData[dataIndex,idx1:idx2],self.m_parsedInputData[0,idx1:idx2])
            data = self.getProcessedDataBetweenForFile(t1,t2,fileName)
            result = np.trapz(data[1],data[0]) #y, then x
            return result
        except:
            return None