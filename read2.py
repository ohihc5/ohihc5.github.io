import pandas as pd
from openpyxl import load_workbook

# Load the Excel file with data_only=True to evaluate formulas
file_path = r'C:\Users\cleung9\Desktop\Relocation\Wave6\e-Passport-2 (PDC-PROD)_point-to-point_cabling_plan_20241125_v0.15.xlsx'  # Using raw string literal for the file path
wb1 = load_workbook(file_path, data_only=True)
sheet = wb1['Port mapping (IP)']  # Replace with the correct sheet name

# Unhide all columns
for col in sheet.column_dimensions.values():
    col.hidden = False

# Unhide all rows
for row in sheet.row_dimensions.values():
    row.hidden = False

# Remove filters
if sheet.auto_filter.ref:
    sheet.auto_filter.ref = None

# Save the modified workbook to a temporary file
temp_file_path = 'temp_unhidden.xlsx'
wb1.save(temp_file_path)

# Load the modified workbook with pandas
df = pd.read_excel(temp_file_path, sheet_name='Port mapping (IP)', engine='openpyxl')

# Clean up column names by stripping any leading/trailing spaces and replacing newline characters
df.columns = df.columns.str.strip().str.replace('\n', ' ')

# Print the cleaned column names to check for any discrepancies
print("Cleaned Column Names:")
print(df.columns)

# Print the first few rows of the DataFrame to check the data
print("First Few Rows of DataFrame:")
print(df.head())

# Print the specific columns to check if they contain any data
print("Specific Columns Data:")
print(df[['A End Information', 'A-end Panel Name', 'B-end Information', 'B-end Panel Name']].head())

# Add the new column with the concatenated values
df['New Column'] = df.apply(lambda row: (
    f"interface {row['A End Information']}\n"
    f"description TO_{row['B-end Panel Name']}\n"
    "undo enable snmp trap updown\n"
    "port link-type access\n"
    f"port default vlan {row['VLAN no']}\n"
    "stp edged-port enable\n"
    "storm suppression unknown-unicast 85\n"
    "storm suppression multicast 85\n"
    "storm suppression broadcast 85\n"
    "lldp disable"
), axis=1)

# Save the updated DataFrame back to an Excel file
output_file_path = 'updated_e-Passport-2 (PDC-PROD)_point-to-point_cabling_plan_20241125_v0.15.xlsx'
df.to_excel(output_file_path, index=False, engine='openpyxl')

print(f"New column added and saved to {output_file_path}")

# Grab all rows information for the specified columns
try:
    all_rows = df[['Item', 'A End Information', 'A-end Panel Name', 'B-end Information', 'B-end Panel Name']]

    # Export the data to a new Excel file
    extracted_data_path = 'extracted_data.xlsx'
    all_rows.to_excel(extracted_data_path, index=False)

    print(f"All rows information has been successfully exported to {extracted_data_path}.")
except KeyError as e:
    print(f"Error: {e}")
    print("Please check the column names in the Excel file and ensure they match exactly with the specified columns.")