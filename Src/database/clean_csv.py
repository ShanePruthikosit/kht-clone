'''
clean_csv.py
A python program to read a CSV file, select columns,
convert columns to an appropriate format to store
tables in the database.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import pandas as pd

'''Function to convert columns to integer
Arguments
    dataset     - dataset to be converted
    columns     - columns to be converted 
'''
def convert_to_integer(dataset, columns):
        for column in columns:
            dataset[column] = pd.to_numeric(dataset[column], errors='coerce', downcast='integer')
            dataset[column] = dataset[column].fillna(-1).astype(int)

'''Function to select columns and save to csv file
Arguments
    input_file_path     - input file path
    output_file_path    - output file path
    columns_to_select   - columns to select
    columns_to_convert  - columns to convert
'''
def select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select, columns_to_convert=''):
    # Read the CSV file into a DataFrame with explicit delimiter
    dataset = pd.read_csv(input_file_path, delimiter=',')

    # Remove leading and trailing whitespaces from column names
    dataset.columns = dataset.columns.str.strip()
 
    dataset = dataset[columns_to_select]

    # Remove leading and trailing whitespaces from column names
    dataset.columns = dataset.columns.str.strip().str.replace(' ', '_').str.lower().str.replace('(', '').str.replace(')', '').str.replace('%', '')

    # Remove any whitespace in all the values of the column
    for col in dataset.columns:
        if dataset[col].dtype == object:
            dataset[col] = dataset[col].str.strip().str.replace(',', '.')
         
    convert_to_integer(dataset, columns_to_convert)

    # Save the new DataFrame to the same CSV file
    dataset.to_csv(output_file_path, index=False)


