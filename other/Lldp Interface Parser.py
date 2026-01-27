import re
import pandas as pd

# Read the content of the source file
with open('source.txt', 'r') as file:
    content = file.read()

# Split the content into interface status and LLDP sections
interface_section = re.search(r'Interface.*?Description(.*?)display lldp', content, re.DOTALL)
lldp_section = re.search(r'display lldp neighbor brief(.*)', content, re.DOTALL)

# Parse the interface status section
if interface_section:
    interface_lines = re.findall(r'^(\S+)\s+(up|down|\*down)\s+(up|down)\s*(.*)$', interface_section.group(1), re.MULTILINE)
    interface_data = []
    for line in interface_lines:
        interface = line[0]
        phy = line[1]
        protocol = line[2]
        description = line[3].strip()
        interface_data.append({
            'Interface': interface,
            'PHY': phy,
            'Protocol': protocol,
            'Description': description
        })
    interface_df = pd.DataFrame(interface_data)
else:
    interface_df = pd.DataFrame()
    print("Interface Status section not found.")

# Parse the LLDP neighbor brief section
if lldp_section:
    lldp_lines = re.findall(r'^(\S+)\s+\d+\s+(\S+)\s+(\S+)$', lldp_section.group(1), re.MULTILINE)
    lldp_data = []
    for line in lldp_lines:
        lldp_data.append({
            'Local Interface': line[0],
            'Neighbor Interface': line[1],
            'Neighbor Device': line[2]
        })
    lldp_df = pd.DataFrame(lldp_data)
else:
    lldp_df = pd.DataFrame()
    print("LLDP Neighbors section not found.")

# Create the combined dataframe based on logic required (merging rows)
combined_data = []
i = 0
while i < len(interface_df):
    row = interface_df.iloc[i].to_dict()
    if not row['Description'] and i + 1 < len(interface_df):
        # Merge with the next row
        next_row = interface_df.iloc[i + 1].to_dict()
        row['Description'] = f"{next_row['Interface']} {next_row['PHY']} {next_row['Protocol']}"
        combined_data.append(row)
        i += 2  # Skip the next row
    else:
        combined_data.append(row)
        i += 1

combined_df = pd.DataFrame(combined_data)

# Save to Excel with two sheets
with pd.ExcelWriter('network_report.xlsx', engine='openpyxl') as writer:
    combined_df.to_excel(writer, sheet_name='Interface Status', index=False)
    lldp_df.to_excel(writer, sheet_name='LLDP Neighbors', index=False)

print("network_report.xlsx has been created with two sheets.")
