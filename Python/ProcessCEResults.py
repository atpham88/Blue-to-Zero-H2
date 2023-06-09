#Michael Craig
#October 4, 2016
#Process CE results by: 1) save new builds, 2) add new builds to gen fleet, 
#3) determine which units retire due to economics

import copy, os, random, pandas as pd, numpy as np
from CreateFleetForCELoop import *
from AuxFuncs import *
from GAMSAuxFuncs import *

########### STORE BUILD DECISIONS FROM CAPACITY EXPANSION ######################
#Inputs: running list of CE builds (2d list), CE model output as GAMS object, 
#curr CE year
#Outputs: new gen builds by technology (list of tuples of (techtype, # builds))
def saveCEBuilds(capacExpModel,resultsDir,currYear,coOptH2):
    newGenerators = extract1dVarResultsFromGAMSModel(capacExpModel,'vN')
    newStoECap = extract1dVarResultsFromGAMSModel(capacExpModel,'vEneBuiltSto')
    newStoPCap = extract1dVarResultsFromGAMSModel(capacExpModel,'vPowBuiltSto')
    newLines = extract1dVarResultsFromGAMSModel(capacExpModel,'vLinecapacnew')
    if coOptH2:
        newH2Lines = extract1dVarResultsFromGAMSModel(capacExpModel,'vH2Linecapacnew')
    else:
        newH2Lines = newLines
    print('Investments in ' + str(currYear))
    if coOptH2:
        for n,d in zip(['vN','vEneBuiltSto','vPowBuiltSto','vLinecapacnew','vH2Linecapacnew'],[newGenerators,newStoECap,newStoPCap,newLines,newH2Lines]):
            s = pd.Series(d)
            s.to_csv(os.path.join(resultsDir,n+str(currYear)+'.csv'))
            print('***',n.upper(),'\n',s.loc[s>0])
    else:
        for n,d in zip(['vN','vEneBuiltSto','vPowBuiltSto','vLinecapacnew'],[newGenerators,newStoECap,newStoPCap,newLines]):
            s = pd.Series(d)
            s.to_csv(os.path.join(resultsDir,n+str(currYear)+'.csv'))
            print('***',n.upper(),'\n',s.loc[s>0])
    return newGenerators,newStoECap,newStoPCap,newLines,newH2Lines
                
########### ADD CAPACITY EXPANSION BUILD DECISIONS TO FLEET ####################
#Adds generators to fleet
def addNewGensToFleet(genFleet,newGenerators,newStoECap,newStoPCap,newTechs,currYear):
    #print(newGenerators.items())
    for tech,newBuilds in newGenerators.items():
        #print(tech,newBuilds)
        #print(newBuilds,type(newBuilds),newBuilds>0)
        if newBuilds>0:
            techRow = newTechs.loc[newTechs['GAMS Symbol']==tech].copy()
            #Add new info to tech row
            #print(techRow)
            techRow['Unit ID'],techRow['YearAddedCE'] = '1',currYear
            techRow['On Line Year'],techRow['Retired'] = currYear,False
            #Add rows to genFleet by building full units then the remaining partial unit
            #print(techRow['PlantType'].values[0])
            if techRow['PlantType'].values[0] != 'Hydrogen':
                #print(techRow)
                #Add rows for each full build
                while newBuilds > 1: 
                    genFleet = addNewTechRowToFleet(genFleet,techRow)    
                    newBuilds -= 1
                    #print(newBuilds)
                #Add row for partial build
                techRow['Capacity (MW)'] *= newBuilds
                techRow['Nameplate Energy Capacity (MWh)'] *= newBuilds
                genFleet = addNewTechRowToFleet(genFleet,techRow)
            else:
                #print('in else!')
                #Add seasonal storage (hydrogen) by evenly dividing added E & P capacity among new units (E capacity is separate variable)
                numNewH2Facilities = int(np.ceil(newBuilds))
                for newH2Facility in range(numNewH2Facilities):
                    techRow['Nameplate Energy Capacity (MWh)'] = newStoECap[tech]/numNewH2Facilities*1000 #1000 to go from GWh to MWh
                    techRow['Capacity (MW)'] = newStoPCap[tech]/numNewH2Facilities*1000 #1000 to go from GW to MW
                    genFleet = addNewTechRowToFleet(genFleet,techRow)
    genFleet.reset_index(inplace=True,drop=True)
    for item in list(range(len(genFleet))):
        if pd.isnull(genFleet.at[item,'Retirement Year']):
            genFleet['Retirement Year'][item] = 0
            genFleet['Retirement Year'][item] = genFleet['On Line Year'][item] + genFleet['Lifetime(years)'][item]
    return genFleet

def addNewTechRowToFleet(genFleet,techRow):
    techRow['ORIS Plant Code'] = int(genFleet['ORIS Plant Code'].max())+1
    techRow['GAMS Symbol'] = techRow['ORIS Plant Code'].astype(str) + "+" + techRow['Unit ID'].astype(str)
    genFleet = pd.concat([genFleet,techRow])
    return genFleet

########### ADD NEW LINE CAPACITIES TO LINE LIMITS #############################
def addNewLineCapToLimits(lineLimits, newLines, gwToMW = 1000):
    for line,newCapacity in newLines.items():
        lineLimits.loc[lineLimits['GAMS Symbol']==line,'TotalCapacity'] += newCapacity*gwToMW #CE solves for GW; scale to MW
    return lineLimits

def addNewH2LineCapToLimits(H2lineLimits, newH2Lines, gwToMW = 1000):
    for line,newCapacity in newH2Lines.items():
        H2lineLimits.loc[H2lineLimits['GAMS Symbol']==line,'TotalCapacity'] += newCapacity*gwToMW #CE solves for GW; scale to MW
    return H2lineLimits












# ########### SAVE CAPACITY EXPANSION RESULTS ####################################
# #Write some results into CSV files
# def writeCEInfoToCSVs(capacExpBuilds,capacExpRetiredUnitsByCE,capacExpRetiredUnitsByAge,resultsDir,currYear):
#     write2dListToCSV(capacExpBuilds,os.path.join(resultsDir,'genAdditionsCE' + str(currYear) + '.csv'))
#     write2dListToCSV(capacExpRetiredUnitsByCE,os.path.join(resultsDir,'genRetirementsEconCE' + str(currYear) + '.csv'))
#     write2dListToCSV(capacExpRetiredUnitsByAge,os.path.join(resultsDir,'genRetirementsAgeCE' + str(currYear) + '.csv'))

# ########### FIND AND MARK UNITS RETIRED BY CE ##################################
# #Retire units based on generation. 
# def selectAndMarkUnitsRetiredByCE(genFleet,retirementCFCutoff,ceModel,
#         currYear,capacExpRetiredUnitsByCE,hoursForCE,capacExpRetiredUnitsByAge,
#         netDemand,newCfs,ptEligForRetireByCF):
#     genFleetUpdated = getOnlineGenFleet(genFleet,currYear)
#     gen = getPriorGen(genFleet,hoursForCE,ceModel)
#     peakNetDemand = getPeakNetDemand(netDemand,newCfs,genFleetUpdated,currYear)
#     retiredUnitsByCE = selectRetiredUnitsByCE(retirementCFCutoff,gen,genFleetUpdated,
#         hoursForCE,ptEligForRetireByCF,peakNetDemand)
#     print('Num units that retire due to economics in ' + str(currYear) + ':' + str(len(retiredUnitsByCE)))
#     print('Units that retire due to econ from CE in ' + str(currYear) + ':',retiredUnitsByCE)
#     capacExpRetiredUnitsByCE.append(['UnitsRetiredByCE' + str(currYear)] + retiredUnitsByCE)
#     #Mark retired units
#     genFleet.loc[genFleet['GAMS Symbol'].isin(retiredUnitsByCE),'YearRetiredByCE'] = currYear
#     genFleet.loc[genFleet['GAMS Symbol'].isin(retiredUnitsByCE),'Retired'] = True
#     return genFleet

# #Get peak net demand w/ new wind & solar built
# def getPeakNetDemand(netDemand,newCfs,fleet,currYear):
#     print('getPeakNetDemand')
#     print(netDemand)
#     newRE = fleet.loc[(fleet['FuelType'].isin(['Wind','Solar'])) & (fleet['YearAddedCE']==currYear)]
#     reCapacsByLoc = newRE.groupby('PlantType').sum()
#     newREGen = newCfs * reCapacsByLoc['Capacity (MW)']
#     return (netDemand - newREGen.sum(axis=1).values).max()

# #Determines which units retire for economic reasons after CE run.
# def selectRetiredUnitsByCE(retirementCFCutoff,gen,genFleet,hoursForCE,ptEligForRetireByCF,
#         peakNetDemand):
#     totalGen = gen.sum(axis=1)
#     capacs = pd.Series((genFleet['Capacity (MW)']*hoursForCE.shape[0]).values,index=genFleet['GAMS Symbol'])
#     cfs = totalGen*1000/(capacs*len(hoursForCE))
#     symbols = genFleet.loc[genFleet['PlantType'].isin(ptEligForRetireByCF)]['GAMS Symbol']
#     cfsEligibleForRetirements = cfs[symbols]
#     cfsSorted = cfsEligibleForRetirements.sort_values()
#     cfsSorted = cfsSorted.loc[cfsSorted<retirementCFCutoff]
#     nonRECapacity = genFleet.loc[~genFleet['FuelType'].isin(['Wind','Solar'])]['Capacity (MW)'].sum()
#     capToDrop = nonRECapacity - peakNetDemand
#     droppedCap,dropUnits = 0,list()
#     if capToDrop > 0:
#         for idx in cfsSorted.index:
#             droppedCap += genFleet.loc[genFleet['GAMS Symbol']==idx,'Capacity (MW)'].values[0]
#             if droppedCap > capToDrop: break
#             else: dropUnits.append(idx)
#     return dropUnits
