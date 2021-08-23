
import mysql.connector
import yaml

### DB Connection and cursor setup
try:
    with open(r'./databaseDetails.yml') as file:
        details = yaml.load(file, Loader=yaml.FullLoader)
    mydb = mysql.connector.connect(
    host=details['host'],
    database=details['database'],
    user=details['user'],
    password=details['password']
    )
    cursor = mydb.cursor();
    dictCursor = mydb.cursor(dictionary=True)
except (KeyError, FileNotFoundError) as e:
    print('Your databaseDetails.yml file is corrupted or absent. Please make sure it is in the same folder as the client with read permissions and follows the format specified in the documentation')
    exit()
except Exception as e:
    print("Connection could not be made to the MySQL server. Please verify that your specified database is available and that your credentials and connection settings are correct.")
    print("To modify your credentials, please update databaseDetails.yml")
    exit()

class param:
    def __init__(self, name, useLike=False):
        self.name = name
        self.useLike = useLike

class query:
    def __init__(self, table, required, optional, showColumns=None):
        self.table = table
        self.required = required
        self.optional = optional
        self.showColumns = showColumns


# Globals
results = { 'Population': 'PopulationResults', 
            'Relevant Factors' : 'RelevantFactorsResults',
            'Patient Descriptions' : 'PatientDescriptionsResults',
            'Models and Open Questions' : 'ModelsOpenQuestionsResults',
            'Materials' : 'MaterialsResults',
            'Diagnostics' : 'DiagnosticsResults',
            'Therapeutic Interventions' : 'TherapeuticInterventionsResults',
            'Risk Factors' : 'RiskFactorResults',
            'Severity' : 'SeverityResults',
            'Fatality' : 'FatalityResults'}

otherTables = { 'RiskFactor': ['RiskFactorResults'], 
                'MultivariateAdjustments': ['RiskFactorResults'],
                'MeasuresOfEvidence' : ['PopulationResults', 'RelevantFactorsResults', 'ModelsOpenQuestionsResults', 'MaterialsResults'],
                'DaysAfterOnset' : ['MaterialsResults']}


def queryBuilder_select(tableName, params, columns):
    join = ""
    for t, v in otherTables.items():
        if tableName in v and t != 'RiskFactor':
            join += "LEFT JOIN {0} USING(resultID) ".format(t)
    query = "SELECT {0} FROM {1} {2} {3}"
    query = query.format(','.join(columns) if columns else '*', tableName, join if join else '', 'WHERE ' if params else '')
    for k,v in params.items():
        col = "{0}.{1}".format(tableName, k.name) if k.name == 'studyName' else k.name
        query += col + " {0} '" + v + "{1}' AND "
        query = query.format('LIKE' if k.useLike else '=', '%' if k.useLike else '')
    if query[-4:] == 'AND ':
        query = query[:-4]
    return query

def queryBuilder_add(tableName, params):
    for k,v in params.copy().items():
        if k.name == 'measureType':
            data = {k:v for (k,v) in params.items() if k.name == 'measureData'}
            params = {k:v for (k,v) in params.items() if k.name != 'measureData' and k.name != 'measureType'}

            data.update({k:v for (k,v) in params.items() if k.name == 'resultID' or k.name == 'studyName'})
            data[k] = v
            query = "INSERT INTO {0}({1}) VALUES({2})".format('MeasuresOfEvidence',','.join([k.name for k in data.keys()]), ','.join('"' + v + '"' for v in data.values()))
            cursor.execute(query)
        elif k.name == 'resultType':
            data = {k:v for (k,v) in params.items() if k.name == 'daysValue'}
            params = {k:v for (k,v) in params.items() if k.name != 'resultType' and k.name != 'daysValue'}

            data.update({k:v for (k,v) in params.items() if k.name == 'resultID' or k.name == 'studyName'})
            data[k] = v                                                                                                                                                                         
            query = "INSERT INTO {0}({1}) VALUES({2})".format('DaysAfterOnset',','.join([k.name for k in data.keys()]), ','.join('"' + v + '"' for v in data.values()))
            cursor.execute(query)
        elif k.name == 'adjustment':
            params.pop(k, None)
            data = k
            data.update({k:v for (k,v) in params.items() if k.name == 'resultID' or k.name == 'studyName'})
            query = "INSERT INTO {0}({1}) VALUES({2})".format('MultivariateAdjustments',','.join([k.name for k in data.keys()]), ','.join('"' + v + '"' for v in data.values()))
            cursor.execute(query)
    
    query = "INSERT INTO {0}({1}) VALUES({2})"
    query = query.format(tableName, ','.join([k.name for k in params.keys()]), ','.join('"' + v + '"' for v in params.values()))
    print(query)
    return query

def queryBuilder_update(tableName, set, params):
    for k,v in set.copy().items():
        if k.name == 'measureType' or k.name == 'measureData':
            data = {k.name:v for (k,v) in set.items() if k.name == 'measureData' or k.name == 'measureType'}
            if not data:
                continue
            if 'measureData' not in data:
                data.update({k:v for (k,v) in params.items() if k == 'measureData'})
            if 'measureType' not in data:
                data.update({k:v for (k,v) in params.items() if k == 'measureType'})

            data.update({k:v for (k,v) in params.items() if k == 'resultID' or k == 'studyName'})
            print(data)
            if [v for k,v in params.items() if k == 'measureType'][0] is None:
                query = "INSERT INTO {0}({1}) VALUES({2})".format('MeasuresOfEvidence', ','.join(data.keys()), ','.join(data.values()))
            else:
                query = "UPDATE {0} SET {1} = '{2}', {3} = '{4}' WHERE resultID = '{5}' AND measureType = '{6}'".format('MeasuresOfEvidence', 'measureData', data['measureData'], 'measureType',  data['measureType'], data['resultID'], [v for k,v in params.items() if k == 'measureType'][0])
            print(query)
            cursor.execute(query)

            set = {k:v for (k,v) in set.items() if k.name != 'measureData' and k.name != 'measureType'}
            params = {k:v for (k,v) in params.items() if k != 'measureData' and k != 'measureType'}

        elif k.name == 'resultType' or k.name == 'daysValue':
            data = {k:v for (k,v) in params.items() if k.name == 'resultType' or k.name == 'daysValue'}
            if not data:
                continue
            if 'resultType' not in data:
                data.update({k:v for (k,v) in params.items() if k == 'resultType'})
            if 'daysValue' not in data:
                data.update({k:v for (k,v) in params.items() if k == 'daysValue'})

            data.update({k:v for (k,v) in params.items() if k == 'resultID' or k == 'studyName'})
            print(data)
            if [v for k,v in params.items() if k == 'resultType'][0] is None:
                query = "INSERT INTO {0}({1}) VALUES({2})".format('MeasuresOfEvidence', ','.join(data.keys()), ','.join(data.values()))
            else :
                query = "UPDATE {0} SET {1} = '{2}', {3} = '{4}' WHERE resultID = '{5}' AND resultType = '{6}'".format('DaysAfterOnset', 'resultType', data['resultType'], 'daysValue',  data['daysValue'], data['resultID'], [v for k,v in params.items() if k == 'resultType'][0])
            print(query)
            cursor.execute(query)

            set = {k:v for (k,v) in set.items() if k.name != 'resultType' and k.name != 'daysValue'}
            params = {k:v for (k,v) in params.items() if k != 'resultType' and k != 'daysValue'}
        elif k.name == 'adjustment':
            data = {k.name:v for (k,v) in set.items()}
            data.update({k:v for (k,v) in params.items() if k == 'resultID' or k == 'studyName'})
            print(data)
            if [v for k,v in params.items() if k == 'adjustment'][0] is None:
                query = "INSERT INTO {0}({1}) VALUES({2})".format('MultivariateAdjustments', ','.join(data.keys()), ','.join(['"' + v + '"' for v in data.values()]))
            else:
                query = "UPDATE {0} SET {1} = '{2}' WHERE resultID = '{3}' AND adjustment = '{4}'".format('MultivariateAdjustments', 'adjustment', data['adjustment'], data['resultID'], [v for k,v in params.items() if k == 'adjustment'][0])
            print(query)
            cursor.execute(query)
            
            set = {k:v for (k,v) in set.items() if k.name != 'adjustment'}
            params = {k:v for (k,v) in params.items() if k != 'adjustment'}
    if not set:
        return 

    query = "UPDATE {0} SET ".format(tableName)
    for k,v in set.items():
        query += "{0} = '{1}',".format(k.name, v)

    query = query[:-1] + " WHERE "
    for k,v in params.items():
        query += "{0} = '{1}' AND ".format(k, v)
    if query[-4:] == 'AND ':
        query = query[:-4]

    return query

def getPossibleValue(col, value):
    if col == 'studyName':
        return getPossibleStudies(value) 
        
    elif col == 'journalName':
        return getPossibleJournals(value)

    elif col == 'riskFactorName':
        return getPossibleRiskFactors()

def getPossibleStudies(studyName):
    query = "SELECT studyName FROM Study WHERE studyName LIKE \'" + studyName + "%\'"
    cursor.execute(query)
    result = [i[0] for i in cursor.fetchall()]
    return result

def getPossibleJournals(journalName):
    query = "SELECT journalName FROM Journal WHERE journalName LIKE \'" + journalName + "%\'"
    cursor.execute(query)
    result = [i[0] for i in cursor.fetchall()]
    return result

def getPossibleRiskFactors():
    query = "SELECT DISTINCT riskFactorName FROM RiskFactor"
    cursor.execute(query)
    result = [i[0] for i in cursor.fetchall()]
    return result


# DELETE QUERIES
def deleteStudy(studyName):
    query = ""
    for table in otherTables.keys():
        query = "DELETE FROM {0} WHERE studyName = '{1}'; " .format(table, studyName)
        cursor.execute(query)
            
    for table in results.values():
        query = "DELETE FROM {0} WHERE studyName = '{1}'; " .format(table, studyName)
        cursor.execute(query)

    query = "DELETE FROM Study WHERE studyName = '{0}'; " .format(studyName)
    print(query)
    cursor.execute(query)
    mydb.commit()

def deleteJournal(journalName):
    query = "DELETE FROM Journal WHERE journalName = '{0}'; " .format(journalName)
    cursor.execute(query)

    q = queryBuilder_select("Study", {param('journalName'):journalName}, ['studyName'])
    cursor.execute(q)
    result = [i[0] for i in cursor.fetchall()]
    for study in result:
        deleteStudy(study)
   
    mydb.commit()

def deleteResult(resultTable, toDelete):
    resultID = toDelete['resultID']
    query = ""
    for table, value in otherTables.items():
        if (resultTable in value):
            if table == 'RiskFactor':
                query = "DELETE FROM {0} WHERE studyName = '{1}' AND riskFactorName = '{2}' ;".format(table, toDelete['studyName'], toDelete['riskFactorName']) 
                deleteResult('SeverityResults', {'resultID':resultID})
                deleteResult('FatalityResults', {'resultID':resultID})
            else:
                query = "DELETE FROM {0} WHERE resultID = '{1}' ;".format(table, resultID) 
            print(query)
            cursor.execute(query)
            mydb.commit()

    query = "DELETE FROM {0} WHERE resultID = '{1}' ".format(resultTable, resultID)
    print(query)
    cursor.execute(query)
    mydb.commit()