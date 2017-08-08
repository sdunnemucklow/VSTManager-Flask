# Original work Copyright (c) 2017 Samuel Dunne-Mucklow

# This code supports CSV (comma-separated values) text files like the csv library,
# but adds set-type operations AddRow() and DeleteRow()

# Each CSV file consists of a series of zero or more lines called rows.
# Each row is a comma-separated list of values.
# ReadToList() returns a list of row-elements, where each row-element is
# itself a list of the values in the corresponding row (line) of the file.

# AddRow() and DeleteRow() each take a row-element as their second argument.


import os, csv

# Read CSV file into a list of lists
def ReadToList(csvPath):
    try:
        with open(csvPath, 'r') as csvFile:
            reader = csv.reader(csvFile)
            return list(reader)
    except:
        print("The CSV could not be read.")
        return []

def AddRow(csvPath, rowToAdd):
    alreadyExists = False
    if os.path.exists(csvPath):
        try:
            with open(csvPath, 'r') as csvFile:
                for row in csv.reader(csvFile):
                    if row == rowToAdd:
                        alreadyExists = True
        except:
            print("The CSV could not be read.")
    
    if not alreadyExists:
        with open(csvPath, 'a') as csvFile:
            csvFile.write(','.join(rowToAdd) + "\n")
    
    return not alreadyExists
    
def DeleteRow(csvPath, rowToRemove):
    csvList = ReadToList(csvPath)
    with open(csvPath, 'w', newline='') as csvOut:
        writer = csv.writer(csvOut)
        for row in csvList:
            if row != rowToRemove:
                writer.writerow(row)

def _TestAddRow():
    csvList = ReadToList('local.csv')
    rowToAdd = csvList[1]
    rowToAdd[0] = 'ElBarfo'
    if AddRow('local.csv', rowToAdd):
        print('line added')
    else:
        print('line was already present')
    csvList = ReadToList('local.csv')
    for line in csvList:
        print(line)

def _TestDeleteRow():
    csvList = ReadToList('local.csv')
    rowToRemove = csvList[1]
    DeleteRow('local.csv', rowToRemove)
    csvList = ReadToList('local.csv')
    for line in csvList:
        print(line)


if __name__ == "__main__":
    _TestDeleteRow()
