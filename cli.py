import re
import hashlib
import datetime

from queryHelper import *

from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.key_binding import KeyBindings

from prettytable import PrettyTable
from prettytable import from_db_cursor
from prettytable import PLAIN_COLUMNS


### Table printing setup
x = PrettyTable(border=False, header=False)

### Prompt setup
kb = KeyBindings()
@kb.add('escape', 'enter')
def _(event):
    event.current_buffer.validate_and_handle()

@kb.add('enter')
def _(event):
    if event.current_buffer.document.char_before_cursor in (';'):
        event.current_buffer.validate_and_handle()
    event.current_buffer.insert_text('\n')

bind = KeyBindings()
@bind.add('escape')
def _(event):
    main()


# Helper Functions
def camelToSpace(str):
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', str)

def hashResultID(resultPK, length = 12):
    for i,pkElement in enumerate(resultPK):
        if pkElement is None:
            resultPK[i] = '-'
    
    pkString = " ".join(resultPK)
    pkString = pkString.encode('utf-8')
    if length<len(hashlib.sha256(pkString).hexdigest()):
        return hashlib.sha256(pkString).hexdigest()[:length]

mainMenuCompleter = NestedCompleter.from_nested_dict({
    'show\u2006': None,
    'add\u2006': None,
    'edit\u2006': None,
    'delete\u2006': None,
    'direct SQL\u2006': None,
    'export\u2006': None,
    'help\u2006': None,
    'quit\u2006': None,
})

### Global Variables
text_file = None
categories = {'1. study' : 'study', '2. journals' : 'journal', '3. results' : 'result'}

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

resultTableParams = {
            'PopulationResults' : query('PopulationResults', [param('studyName'), param('solution')], [param('addressed'), param('challenge'), param('measureType'), param('measureData')], None),
            'RelevantFactorsResults': query('RelevantFactorsResults', [param('studyName'), param('factors'), param('excerpt')], [param('influential'), param('measureType'), param('measureData')], None),
            'PatientDescriptionsResults': query('PopulationResults', [param('studyName'), param('studyType'), param('sampleObtained')], [param('sampleSize'), param('age'), param('asymptomatic'), param('viralLoadSample'), param('excerpt')], None),
            'ModelsOpenQuestionsResults': query('ModelsOpenQuestionsResults', [param('studyName'), param('excerpt')], [param('method'), param('measureType'), param('measureData')], None),
            'MaterialsResults': query('MaterialsResults', [param('studyName'), param('conclusion')], [param('patientSeverity'), param('method'), param('material'), param('measureType'), param('measureData'), param('resultType'), param('daysValue')], None),
            'DiagnosticsResults': query('DiagnosticsResults', [param('studyName'), param('detectionMethod')], [param('sampleSize'), param('testingAccuracy'), param('assaySpeed'), param('fdaApproval')], None),
            'TherapeuticInterventionsResults': query('TherapeuticInterventionsResults', [param('studyName'), param('therapeuticMethod')], [param('sampleSize'), param('diseaseSeverity'), param('generalOutcome'), param('primaryEndpoint'), param('clinicalImprovement')], None),
            'RiskFactorResults': query('RiskFactorResults', [param('studyName'), param('riskFactorName')], [param('studyPopulation'), param('sampleSize'), param('criticalOnly'), param('dvd'), param('adjustment')], None),
            'SeverityResults': query('SeverityResults', [param('studyName'), param('riskFactorName'), param('severity')], [param('severityLowerBound'), param('severityUpperBound'), param('severitypValue'), param('severitySignificance'), param('severityAdjusted'), param('severityCalculated')], None),
            'FatalityResults': query('FatalityResults', [param('studyName'), param('riskFactorName'), param('fatality')], [param('fatalityLowerBound'), param('fatalityUpperBound'), param('fatalitypValue'), param('fatalitySignificance'), param('fatalityAdjusted'), param('fatalityCalculated')], None)
            }

otherTables = { 'RiskFactor': ['RiskFactorResults'], 
                'MultivariateAdjustments': ['RiskFactorResults'],
                'MeasuresOfEvidence' : ['PopulationResults', 'RelevantFactorsResults', 'ModelsOpenQuestionsResults', 'MaterialsResults'],
                'DaysAfterOnset' : ['MaterialsResults']}

attributes = dict()
attributes['show'] = dict()
attributes['show']['study'] = query('Study', [], [param('studyName', True), param('journalName'), param('studyType'), param('studyLink')], ['studyName', 'journalName', 'studyType', 'studyLink', 'datePublished'])
attributes['show']['journal'] = query('Study', [], [param('journalName', True)], ['journalName', 'studyName', 'studyType', 'studyLink', 'datePublished'])
attributes['show']['result'] = query(None, [param('studyName')], [], None)

attributes['add'] = dict()
attributes['add']['study'] = query('Study', [param('journalName', True), param('studyName', True), param('studyLink')], [param('studyType'), param('datePublished')], None)
attributes['add']['journal'] = query('Journal', [param('journalName', True)], None, None)
attributes['add']['result'] = query(None, [], [], None)

attributes['update'] = dict()
attributes['update']['study'] = query('Study', [param('studyName', True)], [param('studyType'), param('studyLink'), param('datePublished')], None)
attributes['update']['journal'] = query('Journal', [param('journalName', True)], [param('journalName')], None)
attributes['update']['result'] = query(None, [], [], None)

attributes['delete'] = dict()
attributes['delete']['study'] = query('Study', [param('studyName', True)], None, None)
attributes['delete']['journal'] = query('Journal', [param('journalName', True)], None, None)
attributes['delete']['result'] = query(None, [param('studyName')], None, None)

def chooseCategory():
    catCompleter = NestedCompleter.from_nested_dict(dict.fromkeys(categories.values()))
    showCategories()
    category = prompt('\n> ', completer=catCompleter)

    for k, v in categories.items():
        if category.lower() in k:
            return v
    
    return chooseCategory()

def getRequiredParams(req, params):
    for att in req:
        while att not in params:
            label = camelToSpace(att.name)
            value = prompt(label.title() + ' (Required): ')
            if value:
                if value == 'quit':
                    main()
                if att.name == 'studyName' or att.name == 'journalName' or att.name == 'riskFactorName':
                    possible = getPossibleValue(att.name, value)
                    if len(possible) < 1:
                        print("No {0} found, please try again.\n".format(label.replace('Name','')))
                        continue
                    listStudies = [str(i+1)+". "+ str(j) for i,j in enumerate(possible)]
                    options = PrettyTable(["Matching Results:"])              
                    options.add_rows([[i] for i in listStudies])  
                    options.align = 'l'
                    print(options)
                    while att not in params:
                        studyNum = prompt("Please enter the number for the {0} you wish to refer to: ".format(att.name.replace('Name','')))
                        if studyNum and int(studyNum) in range(1, len(possible)+1):
                            params[att] = possible[int(studyNum)-1]
                        else:
                            continue
                else:
                    params[att] = value
            else:
                continue
    return params

def getOptionalParams(opt, params):
    for att in opt:
            label = camelToSpace(att.name)
            value = prompt(label.title() + ': ')
            if value:
                params[att] = value
    return params

def getResultTable():
    showResults()
    while True:
        resultNum = prompt("Please enter the number for the result you wish to refer to: ")
        if resultNum and int(resultNum) in range(1, len(results.keys())+1):
            resultList = list(results.values())
            return resultList[int(resultNum)-1]
        else:
            continue

def getUniqueColumnNames(fields, uniqueFields):
    done = False
    for i in range(len(fields)):
        f = fields[i]
        if f == 'studyName':
            fields[i] = '{0}{1}'.format(f, str(i))
            if not done:
                fields[i] = '{0}'.format(f, str(i))
                uniqueFields.append('{0}'.format(f, str(i)))
                done = True
        else:
            uniqueFields.append(f)
    
def show(*args):
    category = chooseCategory()

    req = attributes['show'][category].required
    opt = attributes['show'][category].optional
    table = attributes['show'][category].table
    cols = attributes['show'][category].showColumns

    params = dict()

    params = getRequiredParams(req, params)
    
    if category == 'result':
        table = getResultTable()
    else:
        params = getOptionalParams(opt, params)
        
    q = queryBuilder_select(table, params, cols)
    cursor.execute(q)
    result = cursor.fetchall()
    if (len(result) == 0):
        print("\nNo records found")
        return
    fields = list(cursor.column_names) if cols is None else cols
    uniqueFields = list()
    getUniqueColumnNames(fields, uniqueFields)
    uniqueFields = [camelToSpace(i).title() for i in uniqueFields]
    cols = [camelToSpace(i).title() for i in fields]
    y = PrettyTable(cols)
    y.align = 'l'
    y.add_rows([list(i) for i in result])
    y = y.get_string(fields=list(dict.fromkeys(uniqueFields)))
    print(y)
    if (text_file):
        text_file.write(y + "\n")
    return

def add(*args):
    category = chooseCategory()

    req = attributes['add'][category].required
    opt = attributes['add'][category].optional
    table = attributes['add'][category].table

    params = dict()
    if category == 'result':
        table = getResultTable()
        req = resultTableParams[table].required
        opt = resultTableParams[table].optional

    notSearch = []
    if category == 'study':
        notSearch = [a for a in req if a.name == 'studyName']
        req = [a for a in req if a.name != 'studyName']

    if category == 'journal':
        notSearch = req
        req = []

    params = getRequiredParams(req, params)

    for att in notSearch:
        while att not in params:
            label = camelToSpace(att.name)
            value = prompt(label.title() + ' (Required): ')
            if value:
                params[att] = value
            else:
                continue

    params = getOptionalParams(opt, params)
    if category == 'result':
        pk = req + notSearch
        pk = [k.name for k in pk]
        pk = [v for (k,v) in params.items() if k.name in pk]  
        params[param('resultID')] = hashResultID(pk)

    q = queryBuilder_add(table, params)
    cursor.execute(q)

    try:
        mydb.commit()
    except:
        print("Error: Please try again")
        add()
    print("\nAdded Successfully!")
    return

def update(*args):
    category = chooseCategory()

    req = attributes['update'][category].required
    opt = attributes['update'][category].optional
    table = attributes['update'][category].table

    params = dict()
    search = dict()
    if category == 'result':
        table = getResultTable()
        req = [param('studyName', True)]
        opt = resultTableParams[table].optional

    search = getRequiredParams(req, search)

    if category == 'result':
        q = queryBuilder_select(table, search, None)
        dictCursor.execute(q)
        allRows = dictCursor.fetchall()
        if len(allRows) < 1:
            print("\nNo records found")
            main()

        for i in allRows:
            if i['studyName'] is None:
                i['studyName'] = [v for (k,v) in search.items() if k.name == 'studyName'][0]

        cursor.execute(q)
        result = cursor.fetchall()
        fields = list(cursor.column_names)
        uniqueFields = list()
        getUniqueColumnNames(fields, uniqueFields)
        uniqueFields = [camelToSpace(i).title() for i in uniqueFields]
        cols = [camelToSpace(i).title() for i in fields]
        y = PrettyTable(cols)
        y.align = 'l'
        y.add_rows([list(i) for i in result])
        y._field_names.insert(0, "Row Number")
        y._align['Row Number'] = 'l'
        y._valign['Row Number'] = 't'
        uniqueFields.append('Row Number') 
        for i, _ in enumerate(y._rows): 
            y._rows[i].insert(0, i+1) 
        y = y.get_string(fields=list(dict.fromkeys(uniqueFields)))
        print(y)
        toUpdate = None
        while not toUpdate:
            resultID = prompt("Please enter the row number for the result you wish to refer to: ")
            try:
                toUpdate = allRows[int(resultID)-1]
            except:
                continue

    print("Update Fields\n")

    params = getOptionalParams(opt, params)

    if  category == 'result':
        q = queryBuilder_update(table, params, toUpdate)
    else:
        q = queryBuilder_update(table, params, {k.name:v for (k,v) in search.items()})
    
    try:
        cursor.execute(q)
        mydb.commit()
    except:
        print("Error: Please try again")
        add()
    print("\nUpdated Successfully!")
    return

def delete(*args):
    category = chooseCategory()

    req = attributes['delete'][category].required
    table = attributes['delete'][category].table
    params = dict()
    params = getRequiredParams(req, params)

    if category == 'result':
        table = getResultTable()
        q = queryBuilder_select(table, params, None)
        dictCursor.execute(q)
        allRows = dictCursor.fetchall()
        if len(allRows) < 1:
            print("\nNo records found")
            main()
        for i in allRows:
            if i['studyName'] is None:
                i['studyName'] = [v for (k,v) in params.items() if k.name == 'studyName'][0]

        cursor.execute(q)
        result = cursor.fetchall()
        fields = list(cursor.column_names)
        uniqueFields = list()
        getUniqueColumnNames(fields, uniqueFields)
        uniqueFields = [camelToSpace(i).title() for i in uniqueFields]
        cols = [camelToSpace(i).title() for i in fields]
        y = PrettyTable(cols)
        y.align = 'l'
        y.add_rows([list(i) for i in result])
        y._field_names.insert(0, "Row Number")
        y._align['Row Number'] = 'l'
        y._valign['Row Number'] = 't' 
        for i, _ in enumerate(y._rows): 
            y._rows[i].insert(0, i+1) 
        uniqueFields.append('Row Number')
        y = y.get_string(fields=list(dict.fromkeys(uniqueFields)))
        print(y)
        toDelete = None
        while not toDelete:
            resultID = prompt("\nPlease enter the row number for the result you wish to refer to: ")
            try:
                toDelete = allRows[int(resultID)-1]
            except:
                continue
        
        try:    
            deleteResult(table, toDelete)

        except:
            print("Error: Please try again")
            main()

    try:
        if category == 'study':
            deleteStudy([v for (k,v) in params.items() if k.name == 'studyName'][0])
        elif category == 'journal':
            deleteJournal([v for (k,v) in params.items() if k.name == 'journalName'][0])
    except:
            print("Error: Please try again")
            main()

    print("Deleted Sucessfully!")
    return

def directSQLMode(*_): 
  print("\nPress [Enter] to start a new line, line must end with semicolon (;) to execute query. To exit type 'quit;'")
  while True:
    user_input = prompt('sql> ', key_bindings=kb, multiline=True)
    try:
        if ('quit' in user_input):
            break;
        if (any(word in user_input for word in ['DELETE', 'TRUNCATE'])):
            print("Error: Invalid command")
            continue
        cursor.execute(user_input)
        result = from_db_cursor(cursor)
        result.align = 'l'
        print(result)
    except:
        print("Error in SQL syntax, please try again.")

def export(*args):
    global text_file
    if ((len(args[0]) == 0 or len(args[0][0]) == 0) and text_file == None):
        args[0].insert(0, 'start')
    elif ((len(args[0]) == 0 or len(args[0][0]) == 0) and text_file != None):
        args[0].insert(0, 'end')

    if args[0][0] == 'start':
        text_file = open("{0}.txt".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")), "w")
        print("\nExporting to file: {0}".format(text_file.name))
    elif args[0][0] == 'end':
        text_file.close()
        text_file = None
        print("\nExport finished.")

def help(*args):
    print("From the Main Menu type the number or option name to go to that function.")
    print("Follow instructions to choose category and fill out required and optional parameters. Optional parameters can be left blank.")
    print("In 'Direct SQL Mode', you can directly type the SQL query. Note: Deleting records is not allowed through 'Direct SQL Mode")
    print("The export function can export the results you see from the 'Show' function to a text file. Type 'export start' to create a new text file and begin writing to the file. Type 'export end' to stop writing.")

def quit(*args):
    exit()

mainMenu = {'1. show': show, '2. add': add, '3. edit': update, '4. delete': delete, '5. direct sql mode' : directSQLMode, '6. export': export, '7. help' : help, '8. quit': quit}


def makeMainMenu():
    string = []
    for i, (k,v) in enumerate(mainMenu.items()):
        string.append(k.title().replace('Sql', 'SQL'))
    
    c1 = string[:len(string)//2]
    c2 = string[len(string)//2:]
    for i in range(len(c1)):
          x.add_row([c1[i], c2[i]])

    x.align = 'l'

def showMainMenu():
    print("\nMain Menu:")
    makeMainMenu()
    print(x)
    x.clear()

def showCategories():
    print("\nPlease Select a Category:")
    for k in categories.keys():
        x.add_row([k.title(), ""])    
    x.align = 'l'
    print(x)
    x.clear()

def showResults():
    print("\nPlease Select a Result Type:")
    for i, k in enumerate(results.keys()):
        x.add_row([str(i+1)+". " + k.title(), ""])    
    x.align = 'l'
    print(x)
    x.clear()

def main():
    while True:
        showMainMenu()
        user_input = prompt('\n> ', completer=mainMenuCompleter)
        inputArray = user_input.split('\u2006')
        inputWithSpace = user_input.split(' ')
        function = inputArray[0] if inputArray[0] in mainMenu else inputWithSpace[0]
        args = inputWithSpace[1:] if not inputArray[1:] else inputArray[1:]
        for key in mainMenu:
            if function.lower().strip().replace('\u2006', '') in key:
                mainMenu[key](args)
                
        if user_input == 'quit':
            break;


if __name__ == '__main__':
    main()