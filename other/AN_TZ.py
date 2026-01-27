from netmiko import ConnectHandler
import time

device = {
    'device_type': 'huawei',
    'host': '10.26.169.203',
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
                # Stelnet to target ANPNHQSBTZ01C01
                # remote_prompt = handle_stelnet(conn, "10.26.241.81", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ01C02
                # remote_prompt = handle_stelnet(conn, "10.26.241.82", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ11D01
                # remote_prompt = handle_stelnet(conn, "10.26.241.83", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ11D02
                # remote_prompt = handle_stelnet(conn, "10.26.241.84", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ12D01
                # remote_prompt = handle_stelnet(conn, "10.26.241.85", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ12D02
                # remote_prompt = handle_stelnet(conn, "10.26.241.86", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ13D01
                # remote_prompt = handle_stelnet(conn, "10.26.241.80", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZ13D02
                # remote_prompt = handle_stelnet(conn, "10.26.241.95", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNRRSBTZ11D01
                # remote_prompt = handle_stelnet(conn, "10.26.241.87", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNRRSBTZ11D02
                # remote_prompt = handle_stelnet(conn, "10.26.241.88", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQDCIFO01
                # remote_prompt = handle_stelnet(conn, "10.26.22.143", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQDCIFO02
                # remote_prompt = handle_stelnet(conn, "10.26.22.144", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZCAD01
                # remote_prompt = handle_stelnet(conn, "10.26.22.89", "pccw2023", "P@ssw0rd")
                # Stelnet to target ANPNHQSBTZCBD01
                # remote_prompt = handle_stelnet(conn, "10.26.22.90", "pccw2023", "P@ssw0rd")

                # Access Switch
                # Stelnet to target: ANPNHQSBTZ11F03
                # remote_prompt = handle_stelnet(conn, "10.26.22.150", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11F04
                # remote_prompt = handle_stelnet(conn, "10.26.22.151", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T01
                # remote_prompt = handle_stelnet(conn, "10.26.22.155", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T02
                # remote_prompt = handle_stelnet(conn, "10.26.22.156", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T04
                # remote_prompt = handle_stelnet(conn, "10.26.23.7", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T05
                # remote_prompt = handle_stelnet(conn, "10.26.22.152", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T06
                # remote_prompt = handle_stelnet(conn, "10.26.22.152", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T07
                # remote_prompt = handle_stelnet(conn, "10.26.22.159", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T08
                # remote_prompt = handle_stelnet(conn, "10.26.22.160", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T09
                # remote_prompt = handle_stelnet(conn, "10.26.22.161", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T10
                # remote_prompt = handle_stelnet(conn, "10.26.22.162", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T13
                # remote_prompt = handle_stelnet(conn, "10.26.22.165", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T14
                # remote_prompt = handle_stelnet(conn, "10.26.22.166", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T15
                # remote_prompt = handle_stelnet(conn, "10.26.22.167", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T16
                # remote_prompt = handle_stelnet(conn, "10.26.22.168", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T17
                # remote_prompt = handle_stelnet(conn, "10.26.22.169", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T18
                # remote_prompt = handle_stelnet(conn, "10.26.22.170", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T19
                # remote_prompt = handle_stelnet(conn, "10.26.22.171", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T20
                # remote_prompt = handle_stelnet(conn, "10.26.22.172", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T21
                # remote_prompt = handle_stelnet(conn, "10.26.22.175", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T22
                # remote_prompt = handle_stelnet(conn, "10.26.22.176", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T23
                # remote_prompt = handle_stelnet(conn, "10.26.22.189", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T24
                # remote_prompt = handle_stelnet(conn, "10.26.22.190", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T25
                # remote_prompt = handle_stelnet(conn, "10.26.22.193", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T26
                # remote_prompt = handle_stelnet(conn, "10.26.22.194", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T27
                # remote_prompt = handle_stelnet(conn, "10.26.22.195", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T28
                # remote_prompt = handle_stelnet(conn, "10.26.22.196", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T29
                # remote_prompt = handle_stelnet(conn, "10.26.22.197", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T30
                # remote_prompt = handle_stelnet(conn, "10.26.22.198", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T31
                # remote_prompt = handle_stelnet(conn, "10.26.22.199", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T32
                # remote_prompt = handle_stelnet(conn, "10.26.22.200", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T33
                # remote_prompt = handle_stelnet(conn, "10.26.22.173", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T34
                # remote_prompt = handle_stelnet(conn, "10.26.22.174", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T35
                # remote_prompt = handle_stelnet(conn, "10.26.22.157", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T36
                # remote_prompt = handle_stelnet(conn, "10.26.22.158", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T37
                # remote_prompt = handle_stelnet(conn, "10.26.22.163", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ11T38
                # remote_prompt = handle_stelnet(conn, "10.26.22.164", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F07
                # remote_prompt = handle_stelnet(conn, "10.26.22.177", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F08
                # remote_prompt = handle_stelnet(conn, "10.26.22.178", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F09
                # remote_prompt = handle_stelnet(conn, "10.26.22.181", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F10
                # remote_prompt = handle_stelnet(conn, "10.26.22.182", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F11
                # remote_prompt = handle_stelnet(conn, "10.26.22.183", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F12
                # remote_prompt = handle_stelnet(conn, "10.26.22.184", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F13
                # remote_prompt = handle_stelnet(conn, "10.26.22.185", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F14
                # remote_prompt = handle_stelnet(conn, "10.26.22.186", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F15
                # remote_prompt = handle_stelnet(conn, "10.26.22.187", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F16
                # remote_prompt = handle_stelnet(conn, "10.26.22.188", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F17
                # remote_prompt = handle_stelnet(conn, "10.26.22.179", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZ12F18
                # remote_prompt = handle_stelnet(conn, "10.26.22.180", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZNCE01
                remote_prompt = handle_stelnet(conn, "10.26.22.123", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZNCE02
                # remote_prompt = handle_stelnet(conn, "10.26.22.124", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZNCE03
                # remote_prompt = handle_stelnet(conn, "10.26.22.121", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNHQSBTZNCE04
                # remote_prompt = handle_stelnet(conn, "10.26.22.122", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNRRSBTZ11T01
                # remote_prompt = handle_stelnet(conn, "10.26.23.194", "pccw2023", "P@ssw0rd")
                # Stelnet to target: ANPNRRSBTZ11T02
                # remote_prompt = handle_stelnet(conn, "10.26.23.195", "pccw2023", "P@ssw0rd")

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