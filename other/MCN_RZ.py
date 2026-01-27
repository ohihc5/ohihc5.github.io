from netmiko import ConnectHandler
import time

device = {
    'device_type': 'huawei',
    'host': '10.26.169.209',
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
                # Stelnet to target ITPNHQSBRZ01C01
                # remote_prompt = handle_stelnet(conn, "172.17.100.251", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ01C02
                # remote_prompt = handle_stelnet(conn, "172.17.100.252", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ11D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.249", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ11D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.250", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ12D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.247", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ12D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.248", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ13D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.245", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ13D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.246", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ14D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.243", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ14D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.244", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ15D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.241", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNHQSBRZ15D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.242", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNRRSBRZ11D01
                # remote_prompt = handle_stelnet(conn, "172.17.100.239", "pccw2023", "P@ssw0rd")
                # Stelnet to target ITPNRRSBRZ11D02
                # remote_prompt = handle_stelnet(conn, "172.17.100.240", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQDCIFO01
                # remote_prompt = handle_stelnet(conn, "172.17.99.66", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQDCIFO02
                # remote_prompt = handle_stelnet(conn, "172.17.99.67", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZCAD01
                # remote_prompt = handle_stelnet(conn, "172.17.100.237", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZCBD01
                remote_prompt = handle_stelnet(conn, "172.17.100.238", "pccw2023", "P@ssw0rd")

                # Access Switch
                # Stelnet to target: ITPNHQSBRZ11F01
                # remote_prompt = handle_stelnet(conn, "172.17.99.17", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11F02
                # remote_prompt = handle_stelnet(conn, "172.17.99.18", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11F11
                # remote_prompt = handle_stelnet(conn, "172.17.99.63", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11F12
                # remote_prompt = handle_stelnet(conn, "172.17.99.64", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11F21
                # remote_prompt = handle_stelnet(conn, "172.17.99.59", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11F22
                # remote_prompt = handle_stelnet(conn, "172.17.99.60", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T01
                # remote_prompt = handle_stelnet(conn, "172.17.99.15", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T02
                # remote_prompt = handle_stelnet(conn, "172.17.99.16", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T03
                # remote_prompt = handle_stelnet(conn, "172.17.99.71", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T04
                # remote_prompt = handle_stelnet(conn, "172.17.99.72", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T05
                # remote_prompt = handle_stelnet(conn, "172.17.99.19", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T06
                # remote_prompt = handle_stelnet(conn, "172.17.99.19", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T07
                # remote_prompt = handle_stelnet(conn, "172.17.99.31", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T08
                # remote_prompt = handle_stelnet(conn, "172.17.99.32", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T09
                # remote_prompt = handle_stelnet(conn, "172.17.99.73", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T10
                # remote_prompt = handle_stelnet(conn, "172.17.99.74", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T11
                # remote_prompt = handle_stelnet(conn, "172.17.99.61", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T12
                # remote_prompt = handle_stelnet(conn, "172.17.99.62", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T13
                # remote_prompt = handle_stelnet(conn, "172.17.99.33", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T14
                # remote_prompt = handle_stelnet(conn, "172.17.99.34", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T21
                # remote_prompt = handle_stelnet(conn, "172.17.99.57", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ11T22
                # remote_prompt = handle_stelnet(conn, "172.17.99.58", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12F01
                # remote_prompt = handle_stelnet(conn, "172.18.250.69", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12F02
                # remote_prompt = handle_stelnet(conn, "172.18.250.70", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T01
                # remote_prompt = handle_stelnet(conn, "172.18.250.71", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T02
                # remote_prompt = handle_stelnet(conn, "172.18.250.72", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T03
                # remote_prompt = handle_stelnet(conn, "172.18.250.73", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T04
                # remote_prompt = handle_stelnet(conn, "172.18.250.74", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T05
                # remote_prompt = handle_stelnet(conn, "172.18.250.75", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T06
                # remote_prompt = handle_stelnet(conn, "172.18.250.76", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T07
                # remote_prompt = handle_stelnet(conn, "172.18.250.77", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T08
                # remote_prompt = handle_stelnet(conn, "172.18.250.78", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T09
                # remote_prompt = handle_stelnet(conn, "172.18.250.79", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ12T10
                # remote_prompt = handle_stelnet(conn, "172.18.250.80", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ13F01
                # remote_prompt = handle_stelnet(conn, "172.20.250.69", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ13F02
                # remote_prompt = handle_stelnet(conn, "172.20.250.70", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ13T01
                # remote_prompt = handle_stelnet(conn, "172.20.250.71", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ13T02
                # remote_prompt = handle_stelnet(conn, "172.20.250.72", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14F01
                # remote_prompt = handle_stelnet(conn, "172.21.250.69", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14F02
                # remote_prompt = handle_stelnet(conn, "172.21.250.70", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T01
                # remote_prompt = handle_stelnet(conn, "172.21.250.71", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T02
                # remote_prompt = handle_stelnet(conn, "172.21.250.72", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T03
                # remote_prompt = handle_stelnet(conn, "172.21.250.73", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T04
                # remote_prompt = handle_stelnet(conn, "172.21.250.74", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T05
                # remote_prompt = handle_stelnet(conn, "172.21.250.75", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ14T06
                # remote_prompt = handle_stelnet(conn, "172.21.250.76", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15F01
                # remote_prompt = handle_stelnet(conn, "172.22.250.69", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15F02
                # remote_prompt = handle_stelnet(conn, "172.22.250.70", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15F03
                # remote_prompt = handle_stelnet(conn, "172.22.250.67", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15F04
                # remote_prompt = handle_stelnet(conn, "172.22.250.68", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T01
                # remote_prompt = handle_stelnet(conn, "172.22.250.71", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T02
                # remote_prompt = handle_stelnet(conn, "172.22.250.72", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T03
                # remote_prompt = handle_stelnet(conn, "172.22.250.73", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T04
                # remote_prompt = handle_stelnet(conn, "172.22.250.74", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T05
                # remote_prompt = handle_stelnet(conn, "172.22.250.75", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T06
                # remote_prompt = handle_stelnet(conn, "172.22.250.76", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T07
                # remote_prompt = handle_stelnet(conn, "172.22.250.77", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T08
                # remote_prompt = handle_stelnet(conn, "172.22.250.78", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T09
                # remote_prompt = handle_stelnet(conn, "172.22.250.79", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T10
                # remote_prompt = handle_stelnet(conn, "172.22.250.80", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T11
                # remote_prompt = handle_stelnet(conn, "172.22.250.81", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T12
                # remote_prompt = handle_stelnet(conn, "172.22.250.82", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T13
                # remote_prompt = handle_stelnet(conn, "172.22.250.83", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZ15T14
                # remote_prompt = handle_stelnet(conn, "172.22.250.84", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZNCE01
                # remote_prompt = handle_stelnet(conn, "172.17.98.187", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZNCE02
                # remote_prompt = handle_stelnet(conn, "172.17.98.188", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZNCE03
                # remote_prompt = handle_stelnet(conn, "172.17.98.184", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNHQSBRZNCE04
                # remote_prompt = handle_stelnet(conn, "172.17.98.185", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNRRSBRZ11T01
                # remote_prompt = handle_stelnet(conn, "172.17.98.134", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ITPNRRSBRZ11T02
                # remote_prompt = handle_stelnet(conn, "172.17.98.135", "pccw2023", "P@ssw0rd")

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