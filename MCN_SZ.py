from netmiko import ConnectHandler
import time

device = {
    'device_type': 'huawei',
    'host': '10.26.169.210',
    'username': 'pccw2023',
    'password': 'P@ssw0rd',
    'session_log': 'session.log',
    'global_delay_factor': 8,
    'fast_cli': False,
}


def handle_stelnet(conn, target_ip, username, password):
    """Handle Huawei stelnet with proper prompt sequence"""
    original_prompt = conn.find_prompt()

    try:
        # 1. Initiate stelnet connection
        conn.write_channel(f"stelnet {target_ip}\n")
        time.sleep(3)

        # 2. Handle security warning
        output = conn.read_channel()
        if "Continue to access it? [Y/N]:" in output:
            conn.write_channel("Y\n")
            time.sleep(2)

        # 3. Handle public key prompt
        output += conn.read_channel()
        if "Save the server's public key? [Y/N]:" in output:
            conn.write_channel("N\n")
            time.sleep(2)

        # 4. Handle username/password
        output += conn.read_channel()
        if "Please input the username:" in output:
            conn.write_channel(f"{username}\n")
            time.sleep(2)

        output += conn.read_channel()
        if "Enter password:" in output:
            conn.write_channel(f"{password}\n")
            time.sleep(3)

        # 5. Verify connection
        conn.write_channel("\n")
        time.sleep(2)
        remote_prompt = conn.find_prompt()
        if not remote_prompt:
            raise Exception("Stelnet connection failed")

        return remote_prompt

    except Exception as e:
        print(f"Stelnet Error: {str(e)}")
        conn.write_channel("\x03\x03quit\n")  # Ctrl+C and quit
        time.sleep(2)
        return None


def main():
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            with open('source.txt', 'w', encoding='utf-8') as f:
                # Initial setup
                output = conn.send_command("screen-length 0 temporary")
                f.write(f"{conn.find_prompt()}screen-length 0 temporary\n{output}\n")

                # Core & Distribution SW
                # Stelnet to target ITPNHQSBSZ11D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.253", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBSZ11D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.254", "pccw2023", "P@ssw0rd")

                # Access Switch
                # Stelnet to target: ITPNHQSBSZ11F01
                # remote_prompt = handle_stelnet(conn, "172.17.101.30", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11F02
                # remote_prompt = handle_stelnet(conn, "172.17.101.29", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11F03
                # remote_prompt = handle_stelnet(conn, "172.17.101.13", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11F04
                # remote_prompt = handle_stelnet(conn, "172.17.101.14", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T01
                # remote_prompt = handle_stelnet(conn, "172.17.101.28", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T02
                # remote_prompt = handle_stelnet(conn, "172.17.101.27", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T03
                # remote_prompt = handle_stelnet(conn, "172.17.101.19   ", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T04
                # remote_prompt = handle_stelnet(conn, "172.17.101.20", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T05
                # remote_prompt = handle_stelnet(conn, "172.17.101.21", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T06
                # remote_prompt = handle_stelnet(conn, "172.17.101.22", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T07
                # remote_prompt = handle_stelnet(conn, "172.17.101.23", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T08
                # remote_prompt = handle_stelnet(conn, "172.17.101.24", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T09
                # remote_prompt = handle_stelnet(conn, "172.17.101.17", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T10
                # remote_prompt = handle_stelnet(conn, "172.17.101.18", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T11
                # remote_prompt = handle_stelnet(conn, "172.17.101.15", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T12
                # remote_prompt = handle_stelnet(conn, "172.17.101.16", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T13
                # remote_prompt = handle_stelnet(conn, "172.17.101.11", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBSZ11T14
                # remote_prompt = handle_stelnet(conn, "172.17.101.12", "pccw2023", "P@ssw0rd")


                if remote_prompt:
                    # Execute remote commands
                    commands = [
                        'screen-length 0 temporary',
                        'display interface description',
                        'display lldp neighbor brief',
                        'display current-configuration interface'
                    ]

                    for cmd in commands:
                        output = conn.send_command(cmd, delay_factor=10)
                        f.write(f"{remote_prompt}{cmd}\n{output}\n")

                    # Exit stelnet properly
                    conn.write_channel("quit\n")
                    time.sleep(2)

                # Local commands
                local_commands = [
                    'quit'
                ]

                for cmd in local_commands:
                    output = conn.send_command(cmd, delay_factor=8)
                    f.write(f"{conn.find_prompt()}{cmd}\n{output}\n")

    except Exception as e:
        print(f"Main Error: {str(e)}")


if __name__ == "__main__":
    main()
    print("Operation completed. Check source.txt for output.")