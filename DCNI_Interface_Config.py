import re
import pandas as pd
from typing import List, Dict, Any, Optional


class NetworkConfigParser:
    """Class for parsing network configuration data from switches"""

    def __init__(self):
        self.hostname = None

    def _extract_hostname(self, text: str) -> str:
        """Extract hostname from configuration text"""
        hostname_match = re.search(r'<(\S+)>display', text)
        return hostname_match.group(1) if hostname_match else "network_configuration"

    def _split_interface(self, interface: str) -> tuple:
        """Split interface name into slot and port components
        Handles formats like:
        - 100GE7/0/0 → ('100GE', '7/0/0')
        - 100GE1/4/0/6 → ('100GE', '1/4/0/6')
        - Eth-Trunk23 → ('Eth-Trunk', '23')
        """
        if not interface:
            return "", ""

        # Handle Eth-Trunk cases
        #if interface.startswith('Eth-Trunk'):
        #    return 'Eth-Trunk', interface[9:]  # Remove 'Eth-Trunk' prefix

        # Handle interfaces with format: [TYPE][NUMBER]/... (e.g., 100GE7/0/0)
        match = re.match(r'^(\d*[A-Za-z]+)(\d+/\d+/\d+/\d+|\d+/\d+/\d+|\d+/\d+|\d+)$', interface)
        if match:
            return match.group(1), match.group(2)

        # Fallback for other formats
        parts = interface.split('/', 1)
        if len(parts) == 2:
            return parts[0].rstrip('/'), parts[1]
        return interface, ''  # Final fallback

    def parse_interfaces(self, text: str) -> List[Dict[str, str]]:
        """Parse interface status information with dynamic hostname handling"""
        interfaces = []
        pattern = r'^(\S+)\s+(\S+)\s+(\S+)(?:\s+(.*))?$'

        if not self.hostname:
            self.hostname = self._extract_hostname(text)

        interface_section = re.search(
            rf'Interface\s+PHY\s+Protocol Description(.*?)<{self.hostname}>',
            text,
            re.DOTALL
        )

        if interface_section:
            for line in interface_section.group(1).split('\n'):
                if match := re.match(pattern, line.strip()):
                    interface_name = match.group(1)
                    slot, port = self._split_interface(interface_name)
                    interfaces.append({
                        'Interface': interface_name,
                        'Interface Slot': slot,
                        'Interface Port': port,
                        'PHY': match.group(2),
                        'Protocol': match.group(3),
                        'Description': match.group(4) if match.group(4) else ''
                    })
        return interfaces

    def parse_lldp(self, text: str) -> List[Dict[str, str]]:
        """Parse LLDP neighbor information with dynamic hostname handling"""
        neighbors = []

        if not self.hostname:
            self.hostname = self._extract_hostname(text)

        lldp_section = re.search(
            rf'Local Interface\s+Exptime\(s\) Neighbor Interface\s+Neighbor Device(.*?)<{self.hostname}>',
            text,
            re.DOTALL
        )

        if lldp_section:
            for line in lldp_section.group(1).split('\n'):
                if line.strip() and not line.startswith('-----'):
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 3:
                        neighbors.append({
                            'Local Interface': parts[0],
                            'Neighbor Interface': parts[2],
                            'Neighbor Device': parts[3] if len(parts) > 3 else ''
                        })
        return neighbors

    def parse_interface_configs(self, text: str) -> List[Dict[str, Any]]:
        """Parse detailed interface configurations"""
        configs = []
        eth_trunk_vlans = {}
        current_interface = None
        current_config = {}

        # First pass: Collect Eth-Trunk VLAN configurations
        for line in text.split('\n'):
            stripped_line = line.strip()

            if stripped_line.startswith('interface '):
                current_interface = stripped_line[9:].strip()
                if current_interface.startswith('Eth-Trunk'):
                    eth_trunk_vlans[current_interface] = {'VLAN': ''}

            elif current_interface and current_interface.startswith('Eth-Trunk'):
                if stripped_line.startswith('port default vlan '):
                    eth_trunk_vlans[current_interface]['VLAN'] = stripped_line.split('port default vlan ')[1].strip()
                elif stripped_line.startswith('port trunk allow-pass vlan '):
                    eth_trunk_vlans[current_interface]['VLAN'] = stripped_line.split('port trunk allow-pass vlan ')[
                        1].strip()

        # Second pass: Process all interfaces
        current_interface = None
        current_config = {}

        for line in text.split('\n'):
            stripped_line = line.strip()

            if stripped_line.startswith('interface '):
                if current_interface:
                    if current_config.get('Eth-Trunk') in eth_trunk_vlans:
                        current_config['Eth-Trunk VLAN'] = eth_trunk_vlans[current_config['Eth-Trunk']]['VLAN']
                    configs.append(current_config)

                current_interface = stripped_line[9:].strip()
                current_config = {
                    'Interface': current_interface,
                    'Description': '',
                    'Eth-Trunk': '',
                    'Eth-Trunk VLAN': '',
                    'IP Address': '',
                    'Subnet Mask': '',
                    'VLAN': '',
                    'OSPF Area': ''
                }

            elif stripped_line.startswith('description '):
                current_config['Description'] = stripped_line[len('description '):].strip()

            elif stripped_line.startswith('ip address '):
                parts = stripped_line[len('ip address '):].split()
                if len(parts) >= 2:
                    current_config['IP Address'] = parts[0]
                    current_config['Subnet Mask'] = parts[1]

            elif stripped_line.startswith('port default vlan '):
                current_config['VLAN'] = stripped_line.split('port default vlan ')[1].strip()

            elif stripped_line.startswith('port trunk allow-pass vlan '):
                current_config['VLAN'] = stripped_line.split('port trunk allow-pass vlan ')[1].strip()

            elif stripped_line.startswith('ospf enable '):
                parts = stripped_line[len('ospf enable '):].split()
                if parts:
                    current_config['OSPF Area'] = parts[0]

            elif stripped_line.startswith('eth-trunk '):
                current_config['Eth-Trunk'] = f"Eth-Trunk{stripped_line.split('eth-trunk ')[1].strip()}"

        # Add the last interface
        if current_interface:
            if current_config.get('Eth-Trunk') in eth_trunk_vlans:
                current_config['Eth-Trunk VLAN'] = eth_trunk_vlans[current_config['Eth-Trunk']]['VLAN']
            configs.append(current_config)

        return configs

    def generate_excel_report(self, text: str, output_file: Optional[str] = None) -> None:
        """Generate Excel report from configuration text"""
        # Extract hostname if not already set
        if not self.hostname:
            self.hostname = self._extract_hostname(text)

        # Set default output filename using hostname
        if output_file is None:
            output_file = f"{self.hostname}.xlsx"

        # Parse all data
        interfaces_df = pd.DataFrame(self.parse_interfaces(text))
        neighbors_df = pd.DataFrame(self.parse_lldp(text))
        configs_df = pd.DataFrame(self.parse_interface_configs(text))

        # Create lookup dictionaries
        neighbors_lookup = neighbors_df.set_index('Local Interface').to_dict('index')
        configs_lookup = configs_df.set_index('Interface').to_dict('index')

        # Initialize all additional columns first
        interfaces_df['Hostname'] = self.hostname
        interfaces_df['Neighbor Interface Slot'] = ''
        interfaces_df['Neighbor Interface Port'] = ''
        interfaces_df['Neighbor Device'] = ''
        interfaces_df['Eth-Trunk'] = ''
        interfaces_df['Eth-Trunk VLAN'] = ''
        interfaces_df['VLAN'] = ''

        # Fill in the additional columns with direct values
        for index, row in interfaces_df.iterrows():
            full_interface = row['Interface']

            # Lookup neighbor info
            neighbor_data = neighbors_lookup.get(full_interface, {})
            neighbor_interface = neighbor_data.get('Neighbor Interface', '')

            # Split neighbor interface
            if neighbor_interface:
                neighbor_slot, neighbor_port = self._split_interface(neighbor_interface)
                interfaces_df.at[index, 'Neighbor Interface Slot'] = neighbor_slot
                interfaces_df.at[index, 'Neighbor Interface Port'] = neighbor_port

            interfaces_df.at[index, 'Neighbor Device'] = neighbor_data.get('Neighbor Device', '')

            # Lookup config info
            config_data = configs_lookup.get(full_interface, {})
            interfaces_df.at[index, 'Eth-Trunk'] = config_data.get('Eth-Trunk', '')
            interfaces_df.at[index, 'VLAN'] = config_data.get('VLAN', '')

            # Lookup Eth-Trunk VLAN if applicable
            if interfaces_df.at[index, 'Eth-Trunk']:
                trunk_vlan = configs_lookup.get(interfaces_df.at[index, 'Eth-Trunk'], {}).get('VLAN', '')
                interfaces_df.at[index, 'Eth-Trunk VLAN'] = trunk_vlan

        # Define and apply column order
        column_order = [
            'Hostname', 'Interface Slot', 'Interface Port', 'PHY', 'Protocol', 'Description',
            'Neighbor Interface Slot', 'Neighbor Interface Port', 'Neighbor Device',
            'Eth-Trunk', 'Eth-Trunk VLAN', 'VLAN'
        ]

        interfaces_df = interfaces_df[column_order]

        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Write data to sheets
            interfaces_df.to_excel(writer, sheet_name='Interfaces', index=False)
            neighbors_df.to_excel(writer, sheet_name='LLDP Neighbors', index=False)
            configs_df.to_excel(writer, sheet_name='Interface Configs', index=False)

            # AutoFit column widths for all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # Iterate through all columns
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter  # Get the column name

                    # Find the maximum length of content in the column
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    # Set column width with some padding
                    adjusted_width = (max_length + 2) * 1.2
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"Excel report generated successfully: {output_file}")


def main():
    parser = NetworkConfigParser()

    with open('session.log', 'r') as file:
        text = file.read()

    parser.generate_excel_report(text)


if __name__ == '__main__':
    main()