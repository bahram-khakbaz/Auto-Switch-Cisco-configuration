import paramiko
import time
import getpass
import serial.tools.list_ports

def send_command(connection, command):
    connection.send((command + "\r\n").encode())
    time.sleep(0.5)

def select_connection_type():
    while True:
        connection_type = input("Select connection type (serial/ssh): ").lower()
        if connection_type == "serial" or connection_type == "ssh":
            return connection_type
        else:
            print("Invalid connection type. Please enter 'serial' or 'ssh'.")

def select_serial_port():
    # Get a list of available serial ports
    available_ports = list(serial.tools.list_ports.comports())

    # Display the list of available ports to the user
    print("Available serial ports:")
    for idx, port in enumerate(available_ports, start=1):
        print(f"{idx}. {port.device}")

    # Prompt the user to select the desired port
    selected_port_index = int(input("Select the serial port (enter the corresponding number): ")) - 1

    # Check if the selected port index is valid
    if 0 <= selected_port_index < len(available_ports):
        return available_ports[selected_port_index].device
    else:
        print("Invalid port selection.")
        exit(1)

def configure_switch_serial(serial_port, config_file):
    try:
        with serial.Serial(serial_port, baudrate=9600, timeout=10) as ser:
            # Send the "enable" command
            send_command(ser, "enable")
            
            # Wait for the password prompt and enter the password securely
            enable_password = getpass.getpass("Enter enable password: ")
            send_command(ser, enable_password)

            # Read the switch_commands.txt file and execute the commands
            with open(config_file) as f:
                commands = f.readlines()

            for command in commands:
                send_command(ser, command.strip())

            # Give some time for the switch to provide the output
            time.sleep(2)

            # Read and display the entire output
            output = ser.read_all().decode('latin-1')

            print("\nCommand output:\n")
            print(output)

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit(1)

def configure_switch_ssh(config_file):
    ip = input("Enter the switch IP address: ")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password)

        channel = client.invoke_shell()
        with open(config_file) as f:
            commands = f.readlines()

        for command in commands:
            send_command(channel, command.strip())

        time.sleep(2)
        output = channel.recv(65535).decode('utf-8')

        print("\nCommand output:\n")
        print(output)

        client.close()

    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication failed. Please check your username and password.")
        exit(1)
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"Could not connect to {ip}. Please check the IP address.")
        exit(1)
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")
        exit(1)

if __name__ == "__main__":
    connection_type = select_connection_type()
    config_file = 'switch_commands.txt'  # Replace this with the correct file path

    if connection_type == "serial":
        serial_port = select_serial_port()
        configure_switch_serial(serial_port, config_file)
    elif connection_type == "ssh":
        configure_switch_ssh(config_file)
