import json
import os
import pandas as pd

def extract_table_column_pairs(data, parent_key="", result=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if key == 'name':
                table_name = value
                extract_columns(data.get('columns', []), table_name, result)
            extract_table_column_pairs(value, new_key, result)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key = f"{parent_key}[{index}]"
            extract_table_column_pairs(item, new_key, result)

def extract_columns(columns, table_name, result):
    for column in columns:
        column_name = column.get('name')
        column_description = column.get('description', 'N/A')
        source_column = column.get('sourceColumn', 'N/A')
        column_expression = get_column_expression(column)
        if column_name:
            result.append({'Table': table_name, 'Column': column_name, 'SourceColumn': source_column, 'Expression': column_expression, 'Description': column_description})

def get_column_expression(column):
    if 'expression' in column:
        return column['expression']
    else:
        return ''

def extract_measures_and_expressions(data, parent_key="", result=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if key == 'name':
                table_name = value
                measures = data.get('measures', [])
                extract_measures(measures, table_name, result)
            extract_measures_and_expressions(value, new_key, result)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key = f"{parent_key}[{index}]"
            extract_measures_and_expressions(item, new_key, result)

def extract_measures(measures, table_name, result):
    for measure in measures:
        measure_name = measure.get('name')
        measure_description = measure.get('description', 'N/A')
        measure_expression = measure.get('expression', '')
        if measure_name:
            result.append({'Table': table_name, 'Measure': measure_name,  'Expression': measure_expression,'Description': measure_description,})

# Folder containing JSON files
json_folder = r"C:\Users\sunny.chandel\Desktop\7Eleven-reporting-team\cubes_json"

output_excel_file = r"C:\Users\sunny.chandel\Desktop\output.xlsx"
with pd.ExcelWriter(output_excel_file) as writer:
    for file_name in os.listdir(json_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(json_folder, file_name)
            cube_name = os.path.splitext(file_name)[0]
            # Load the JSON file
            with open(file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)

            # Extract measures and expressions into a list of dictionaries
            measures_result = []
            extract_measures_and_expressions(json_data, result=measures_result)

            # Create a DataFrame for measures and expressions
            df_measures = pd.DataFrame(measures_result)
            df_measures.insert(0, 'CubeName', cube_name)  # Corrected

            # Extract table and column pairs into a list of dictionaries
            table_column_result = []
            extract_table_column_pairs(json_data, result=table_column_result)

            # Create a DataFrame for table and column pairs
            df_table_column = pd.DataFrame(table_column_result)
            df_table_column.insert(0, 'CubeName', cube_name)

            # Extract table partitions into a list of dictionaries
            table_partition_result = []
            extract_table_partitions(json_data, result=table_partition_result)  # Define this function

            # Create a DataFrame for table partitions
            df_table_partition = pd.DataFrame(table_partition_result)
            df_table_partition.insert(0, 'CubeName', cube_name)  # Corrected

            # Save the DataFrames in separate sheets
            df_measures.to_excel(writer, sheet_name='Measures', index=False)
            df_table_column.to_excel(writer, sheet_name='TableColumnPairs', index=False)
            df_table_partition.to_excel(writer, sheet_name='TablePartitions', index=False)  # Corrected

print("DataFrames saved to Excel file:", output_excel_file)