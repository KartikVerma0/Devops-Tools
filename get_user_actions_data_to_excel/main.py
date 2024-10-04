import json
import xlsxwriter

# Function to convert JSON file to Excel
def json_to_excel(json_file, excel_file):
    # Read the JSON data from the file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Create a new Excel file and add a worksheet
    workbook = xlsxwriter.Workbook(excel_file)
    worksheet = workbook.add_worksheet()

    # Define the desired order of the headers
    headers = [
        "adminName", "date", "orgName", "adminId", "action", 
        "module", "name", "id", "type", "data", 
        "userName", "userId", "orgId"
    ]

    # Write the headers in the specified order
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Keep track of the additional child keys
    additional_headers = []

    # Extract additional headers from nested values
    for item in data:
        for key, value in item.items():
            if isinstance(value, dict):
                for child_key in value.keys():
                    new_header = f"{key}.{child_key}"  # Create new header for child keys
                    if new_header not in additional_headers:
                        additional_headers.append(new_header)
            elif isinstance(value, list):
                for index, child_value in enumerate(value):
                    if isinstance(child_value, dict):
                        for child_key in child_value.keys():
                            new_header = f"{key}[{index}].{child_key}"  # Handle lists with index
                            if new_header not in additional_headers:
                                additional_headers.append(new_header)

    # Write additional headers
    for col_num, header in enumerate(additional_headers, start=len(headers)):
        worksheet.write(0, col_num, header)

    # Write the data rows
    for row_num, item in enumerate(data, start=1):
        # Write the main item values
        for col_num, header in enumerate(headers):
            value = item.get(header)  # Get value for the current header
            # Leave empty if value is a dict or list
            if isinstance(value, (dict, list)):
                worksheet.write(row_num, col_num, "")  # Keep original column empty
            else:
                worksheet.write(row_num, col_num, value)

        # Write child values from nested objects
        for col_num, header in enumerate(additional_headers):
            key, child_key = header.split('.', 1) if '.' in header else (header.split('[', 1)[0], header.split('.', 1)[-1])
            if '.' in header:
                # Handle nested dictionary
                value = item.get(key, {}).get(child_key)
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)  # Convert dict or list to string
            elif '[' in header:  # Handle indexed lists
                index = int(header.split('[')[1].split(']')[0])
                key = header.split('[')[0]
                value = item.get(key, [])[index] if index < len(item.get(key, [])) else None
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)  # Convert dict or list to string
            else:
                value = item.get(header)

            worksheet.write(row_num, col_num + len(headers), value)

    # Close the workbook
    workbook.close()

    print(f"Excel file '{excel_file}' created successfully!")

# Specify the JSON file and Excel file names
json_file = 'data2.json'  # Replace with your JSON file name
excel_file = 'output7.xlsx'  # Desired name for the output Excel file

# Convert the JSON to Excel
json_to_excel(json_file, excel_file)
