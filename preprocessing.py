import csv
import os
import hashlib
from collections import namedtuple
import pandas as pd
import math

filepath = "./target_tables/"

filesToDelete = [
    "5_materials/Adhesion to hydrophilic_phobic surfaces.csv",
    "5_materials/Coronavirus susceptibility to heat light and radiation.csv",
    "5_materials/How long can other HCoV strains remain viable on common surfaces_.csv",
    "5_materials/Persistence of virus on surfaces of different materials.csv",
    "5_materials/Susceptibility to environmental cleaning agents.csv",
    "3_patient_descriptions/Incubation period across different age groups.csv",
    "3_patient_descriptions/Length of viral shedding after illness onset.csv",
    "3_patient_descriptions/Manifestations of COVID-19 including but not limited to possible cardiomyopathy and cardiac arrest.csv",
    "3_patient_descriptions/What is the incubation period of the virus_.csv",
    "4_models_and_open_questions/Serial Interval (time between symptom onset in infector-infectee pair).csv"
]

fileToMove = namedtuple('fileToMove', 'path, destination')

filesToMove = [
    fileToMove(filepath+"4_models_and_open_questions/Efforts to develop qualitative assessment frameworks.csv", filepath+"1_population/Efforts to develop qualitative assessment frameworks.csv")
]

resultsWithMeasuresOfEvidence = [
    "1_population",
    "2_relevant_factors",
    "4_models_and_open_questions",
    "5_materials"
]

resultWithPK = namedtuple('resultWithPK', 'type, PK')

resultTypes = [
    resultWithPK("1_population", ["Study", "Proposed Solution"]),
    resultWithPK("2_relevant_factors", ["Study", "Factors", "Excerpt"]),
    resultWithPK("3_patient_descriptions", ["Study", "Study Type", "Sample obtained"]),
    resultWithPK("4_models_and_open_questions", ["Study", "Result"]),
    resultWithPK("5_materials", ["Study", "Conclusion"]),
    resultWithPK("6_diagnostics", ["Study", "Detection Method", "Study Type"]),
    resultWithPK("7_therapeutics_interventions_and_clinical_studies", ["Study", "Therapeutic method(s) utilized/assessed"]),
    resultWithPK("8_risk_factors", ["Study", "RiskFactor", "Multivariate adjustment", "Severe", "Fatality", "Study Population"]),
]

def hashResultID(resultPK, length = 12):
    for i,pkElement in enumerate(resultPK):
        if pd.isnull(pkElement):
            resultPK[i] = '-'
    
    pkString = " ".join(resultPK)
    pkString = pkString.encode('utf-8')
    if length<len(hashlib.sha256(pkString).hexdigest()):
        return hashlib.sha256(pkString).hexdigest()[:length]
    else:
        raise Exception("Length too long. Length of {y} when hash length is {x}.".format(x=str(len(hashlib.sha256(pkString).hexdigest())),y=length))

def breakdownMeasureOfEvidence(measureOfEvidenceString):
    measures = []
    measureStrings = []
    delimiter = ";"

    if delimiter not in measureOfEvidenceString and ':' not in measureOfEvidenceString:
        return [("StringType", measureOfEvidenceString)]
    measureStrings = list(measureOfEvidenceString.split(delimiter))
    for measureString in measureStrings:
        delimiter2 = ':'
        if '=' in measureOfEvidenceString and delimiter2 not in measureOfEvidenceString:
            delimiter2 = "="
        # measureString will be in the format type: result
        typeAndResult = measureString.split(delimiter2)
        if len(typeAndResult) < 2:
            typeAndResult = measureString.split(' ')
        measureTuple = (typeAndResult[0].strip(), typeAndResult[1].strip())
        measures.append(measureTuple)
    return measures

def breakdownMultivariateAdjustment(inputString):
    measures = []
    measureStrings = []
    delimiter = ";"

    if delimiter not in inputString and ',' in inputString:
        delimiter = ','
    return list(inputString.split(delimiter))

def main():
    # Delete extra tables that don't align with table definitions
    # This is tables 1-5 in Materials
    #         tables 3, 4, 5, 8 in Patient Descriptions
    for fileToDelete in filesToDelete:
        if(os.path.exists(filepath + fileToDelete)):
            os.remove(filepath+fileToDelete)

    # Move any misplaced tables
    # This is table [Efforts to develop qualitative assessment frameworks.csv] from Models and Open Questions to Population
    for listFile in filesToMove:
        if(os.path.exists(listFile.path)):
            os.replace(listFile.path, listFile.destination)
    
    # Drop Property 2 column from all Materials tables since it's all NULLs anyway
    # Also split Measure of Evidence into MeasureOfEvidence and PatientSeverity
    # Additional processing will be required on MeasureOfEvidence columns
    for materialsTable in os.listdir(filepath+"5_materials"):
        tablePath = f"{filepath}5_materials/{materialsTable}"
        outputPath = f"{filepath}5_materials/clean_{materialsTable}"
        if(materialsTable[0:5] != 'clean'):
            f = pd.read_csv(tablePath)
            f.drop('Property 2', axis=1, inplace=True)
            f.insert(11, 'PatientSeverity', '-')
            for i, row in f.iterrows():
                if( ',' in row['Measure of Evidence']):
                    severity = row['Measure of Evidence'].split(',',1)[1]
                    f.at[i, 'Measure of Evidence'] = row['Measure of Evidence'].split(',',1)[0]
                    severity = severity.split(':',1)[1][1:]
                    f.at[i, 'PatientSeverity'] = severity
                    f.at[i, 'Conclusion'] += severity
                if( ';' in row['Measure of Evidence']):
                    severity = row['Measure of Evidence'].split(';',1)[1]
                    f.at[i, 'Measure of Evidence'] = row['Measure of Evidence'].split(';',1)[0]
                    severity = severity.split(':',1)[1][1:]
                    f.at[i, 'PatientSeverity'] = severity
                    f.at[i, 'Conclusion'] += severity
            
            f.to_csv(outputPath, index=False)
            os.remove(tablePath)
    
    # Drop rows in relevantFactorsTables where
    # Influential = 'N' and Exceprt is -
    for factorsTable in os.listdir(filepath+"2_relevant_factors"):
        tablePath = f"{filepath}2_relevant_factors/{factorsTable}"
        outputPath = f"{filepath}2_relevant_factors/clean_{factorsTable}"
        if(factorsTable[0:5] != 'clean'):
            f = pd.read_csv(tablePath)
            if 'Infuential' in f:
                f.rename(columns={'Infuential':'Influential'}, inplace=True)
            if 'Influential (Y/N)' in f:
                f.rename(columns={'Influential (Y/N)':'Influential'}, inplace=True)
            f.drop(f[((f['Influential'] == 'N') & (f['Excerpt'] == '-'))].index, inplace=True)
            f.to_csv(outputPath, index=False)
            os.remove(tablePath)

    # Update patientFactors to have uniform format across the Asymptomatic column
    for factorsTable in os.listdir(filepath+"3_patient_descriptions"):
        tablePath = f"{filepath}3_patient_descriptions/{factorsTable}"
        outputPath = f"{filepath}3_patient_descriptions/clean_{factorsTable}"
        if(factorsTable[0:5] != 'clean'):
            f = pd.read_csv(tablePath)
            if 'Aymptomatic' in f:
                f.rename(columns={'Aymptomatic':'Asymptomatic'}, inplace=True)
            if 'Asymptomatic Transmission' in f:
                f.rename(columns={'Asymptomatic Transmission':'Asymptomatic'}, inplace=True)
            if(f['Asymptomatic'].dtype != 'float64'):
                if(f.at[1, 'Asymptomatic'] == 'Y' or f.at[1, 'Asymptomatic'] == 'N'):
                    f.loc[f['Asymptomatic'] =='Y', 'Asymptomatic'] = 1.0
                    f.loc[f['Asymptomatic'] =='N', 'Asymptomatic'] = 0.0
                else:
                    for i, row in f.iterrows():
                        test = 0
                        try:
                            float(row['Asymptomatic'][:-1])/100
                        except:
                            f.drop([f.index[i]], inplace=True)
                            continue
                        f.at[i, 'Asymptomatic'] = float(row['Asymptomatic'][:-1])/100
            f.to_csv(outputPath, index=False)
            os.remove(tablePath)
    
    # Clean up Asymptomatic column and convert to a numeric measures
    for factorsTable in os.listdir(filepath+"3_patient_descriptions"):
        tablePath = f"{filepath}3_patient_descriptions/{factorsTable}"
        outputPath = f"{filepath}3_patient_descriptions/clean_{factorsTable}"
        if(factorsTable[0:5] != 'clean'):
            f = pd.read_csv(tablePath)
            if 'Aymptomatic' in f:
                f.rename(columns={'Aymptomatic':'Asymptomatic'}, inplace=True)
            if 'Asymptomatic Transmission' in f:
                f.rename(columns={'Asymptomatic Transmission':'Asymptomatic'}, inplace=True)
            if(f['Asymptomatic'].dtype != 'float64'):
                if(f.at[1, 'Asymptomatic'] == 'Y' or f.at[1, 'Asymptomatic'] == 'N'):
                    f.loc[f['Asymptomatic'] =='Y', 'Asymptomatic'] = 1.0
                    f.loc[f['Asymptomatic'] =='N', 'Asymptomatic'] = 0.0
                else:
                    for i, row in f.iterrows():
                        try:
                            float(row['Asymptomatic'][:-1])/100
                        except:
                            f.drop([f.index[i]], inplace=True)
                            continue
                        f.at[i, 'Asymptomatic'] = float(row['Asymptomatic'][:-1])/100
            f.to_csv(outputPath, index=False)
            os.remove(tablePath)

    # Concatenate all files in each result into one file for each result type
    os.makedirs(f"{filepath}output/", exist_ok = True)
    measurePath = f"{filepath}output/measures.csv"
    measuresList = []
    adjustmentPath = f"{filepath}output/multivaradjustments.csv"
    adjustmentList = []
    daysPath = f"{filepath}output/daysafteronset.csv"
    daysList = []
    studiesPath = f"{filepath}output/studies.csv"
    studiesList = []
    for result in resultTypes:
        outputPath = f"{filepath}output/{result.type}.csv"        
        dataframes = []
        measureOfEvidenceFrames = []
        for resultTable in os.listdir(filepath+result.type):
            tablePath = f"{filepath}{result.type}/{resultTable}"
            f = pd.read_csv(tablePath)
            if result.type == '1_population':
                f.rename(columns={'Strength of Evidence':'Measure of Evidence'}, inplace=True)
                f.rename(columns={'Solution':'Proposed Solution'}, inplace=True)
                f.rename(columns={'Added On':'Added on'}, inplace=True)
            if result.type == '2_relevant_factors':
                f.rename(columns={'Factors Described':'Factors'}, inplace=True)
                f.rename(columns={'Date Published':'Date'}, inplace=True)
            if result.type == '3_patient_descriptions':
                f.drop(f.columns[f.columns.str.contains('Characteristic',case = False)],axis = 1, inplace = True)
                f.rename(columns={'Sample Obtained':'Sample obtained'}, inplace=True)
                f.rename(columns={'Added On':'Added on'}, inplace=True)
            if result.type == '4_models_and_open_questions':
                f.rename(columns={'Excerpt':'Result'}, inplace=True)
            if result.type == '6_diagnostics':
                f.rename(columns={'Speed of assay':'Speed of Assay'}, inplace=True)
                f.rename(columns={'FDA approval (Y/N)':'FDA Approval'}, inplace=True)
                for i, row in f.iterrows():
                    f.at[i, 'Date'] = f.at[i, 'Date'].replace('/', '-')
                    f.at[i, 'Date'] = f.at[i, 'Date'].replace('--', '-')
                f['Date'] = pd.to_datetime(f['Date'], errors = 'coerce')
                f['Date'] = f['Date'].dt.strftime("%Y-%m-%d")
            if result.type == '8_risk_factors':
                for i, row in f.iterrows():
                    f.at[i, 'Date'] = f.at[i, 'Date'].replace('/', '-')
                    f.at[i, 'Date'] = f.at[i, 'Date'].replace('--', '-')
                f.rename(columns={'Discharge vs. death?':'Discharged vs. death?'}, inplace=True)
                f.rename(columns={'Critical only?':'Critical only'}, inplace=True)
                f['Date'] = pd.to_datetime(f['Date'], errors = 'coerce')
                f['Date'] = f['Date'].dt.strftime("%Y-%m-%d")
                # Add RiskFactor column
                f.insert(len(f.columns), 'RiskFactor', resultTable.split('.')[0])
            if 'Added on' in f.columns:
                f.drop(f.columns[f.columns.str.contains('Added on',case = False)],axis = 1, inplace = True)
                        
            # combine all the tables into one dataframe
            dataframes.append(f)
        
        if(os.path.exists(filepath + outputPath)):
            os.remove(filepath+outputPath)
        
        resultTable = pd.concat(dataframes, ignore_index=True)
        resultTable.drop(resultTable.columns[resultTable.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
        resultTable.insert(4, 'ResultID', '-')
        for i, row in resultTable.iterrows():
            rowPK = []
            for column in result.PK:
                rowPK.append(resultTable.at[i, column])
            resultTable.at[i, 'ResultID'] = hashResultID(rowPK)
        resultTable.drop_duplicates(keep='first', inplace=True)

        if result.type in resultsWithMeasuresOfEvidence:
            # For each row in MeasureOFEvidence, pull that row, split it on , or ;, and 
            for i, row in resultTable.iterrows():
                measures = []
                measureOfEvidenceString = resultTable.at[i, 'Measure of Evidence']
                if measureOfEvidenceString == '-' or measureOfEvidenceString == '' or pd.isnull(measureOfEvidenceString):
                    continue
                else:
                    measures = breakdownMeasureOfEvidence(measureOfEvidenceString)
                    for measure in measures:
                        measureDict = {
                            "Study": resultTable.at[i, "Study"],
                            "ResultID": resultTable.at[i, 'ResultID'],
                            "Type": measure[0],
                            "Measure": measure[1]
                        }
                        measuresList.append(measureDict)
        
        if result.type == '8_risk_factors':
            for i, row in resultTable.iterrows():
                multiVarString = resultTable.at[i, 'Multivariate adjustment']
                if multiVarString == '-' or multiVarString == '' or pd.isnull(multiVarString):
                    continue
                else:
                    adjustments = breakdownMultivariateAdjustment(multiVarString)
                    for adjustment in adjustments:
                        adjustDict = {
                            "Study": resultTable.at[i, "Study"],
                            "ResultID": resultTable.at[i, 'ResultID'],
                            "Adjustment": adjustment.strip()
                        }
                        adjustmentList.append(adjustDict)
        
        if result.type == '5_materials':
            # There's a couple studies in materials that link back to the same published study
            # That's a PITA to deal with, so just drop anything that doesn't align with our PK
            resultTable.drop_duplicates(subset=['Study', 'Conclusion'], keep='first', inplace=True)
            for i, row in resultTable.iterrows():
                rowString = resultTable.at[i, 'Days After Onset/Admission (+) Covid-19 Presence (maximum unless otherwise stated)']

                if rowString == '-' or rowString == '' or pd.isnull(rowString):
                    continue
                else:
                    days = breakdownMeasureOfEvidence(rowString)
                    for day in days:
                        dayDict = {
                            "Study": resultTable.at[i, "Study"],
                            "ResultID": resultTable.at[i, 'ResultID'],
                            "Type": day[0],
                            "Days": day[1]
                        }
                        daysList.append(dayDict)
        print(result.type)
        resultTable.to_csv(outputPath)
        test = resultTable[["Date", "Study", "Study Link", "Journal", "Study Type"]]
        studiesList.append(test)
    
    measuresTable = pd.DataFrame(measuresList, columns=["Study", "ResultID", "Type", "Measure"])
    measuresTable.drop_duplicates(keep='first', inplace=True)
    measuresTable.to_csv(measurePath)
    adjustmentTable = pd.DataFrame(adjustmentList, columns=["Study", "ResultID", "Adjustment"])
    adjustmentTable.drop_duplicates(keep='first', inplace=True)
    adjustmentTable.to_csv(adjustmentPath)
    daysTable = pd.DataFrame(daysList, columns=["Study", "ResultID", "Type", "Days"])
    daysTable.drop_duplicates(keep='first', inplace=True)
    daysTable.to_csv(daysPath)

    # This generates a study table with unique study names and drops the rest of the rows. This is also done in SQL so not used here.
    # studiesTable = pd.concat(studiesList)
    # studiesTable.drop_duplicates(keep='first', inplace=True, subset=["Study"])
    # studiesTable.to_csv(studiesPath)

if __name__ == "__main__":
    main()

