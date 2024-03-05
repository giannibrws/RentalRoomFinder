import os, json, sys, csv
import pandas as pd

"""
Write data to csv file

Args: 
    csvFilePath (str): path to the csv file
    rowHeaders (dict)
    rowValues (list): list of values

Returns:
    Void
"""
def writeToCsv(csvFilePath: str, rowHeaders: dict, rowValues: list):
    # Check if the file is empty
    file_exists = fileExistsCheck(csvFilePath)
    writeMode = 'a' if file_exists else 'w'
    file_is_empty = os.path.getsize(csvFilePath) == 0 if file_exists else True

    # Open the CSV file in write mode
    with open(csvFilePath, writeMode, newline='') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        if file_is_empty:
            csv_writer.writerow(rowHeaders) # Write the header row

        # Write data to the CSV file
        csv_writer.writerow(rowValues)

    print(rowValues)


def fileExistsCheck(csvFilePath: str) -> bool:
    return os.path.isfile(csvFilePath)

# Check if a key value already existst inside the csv file
def checkCsvValueExists(csvFilePath: str, columnName: str, targetValue: str) -> bool:
    file_exists = fileExistsCheck(csvFilePath)
    file_is_empty = os.path.getsize(csvFilePath) == 0 if file_exists else True

    if not file_exists or file_is_empty:
        return False

    # Open the CSV file in read mode
    with open(csvFilePath, 'r', newline='') as csv_file:
        # Create a CSV reader object
        csv_reader = csv.DictReader(csv_file)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Check if the targetValue exists in the specified column
            if row[columnName] == targetValue:
                return True  # Return True if the value is found

    return False  # Return False if the value is not found


def convertCsvToExcel(csvFilePath: str, excelFilePath: str, columnNames: dict, encoding='latin1'):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csvFilePath, encoding=encoding, names=columnNames)

    # Write the DataFrame to an Excel file
    df.to_excel(excelFilePath, index=False)
