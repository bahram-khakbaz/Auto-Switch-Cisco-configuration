import os
import sys
import logging
import paramiko
import time
from getpass import getpass
import serial.tools.list_ports

logger = logging.getLogger('switch_config')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('switch_config.log')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)


def send_command(connection, command):
    connection.write((command + "\r\n").encode())
    time.sleep(0.5)


# Config file
config_file = '/home/bahram/Desktop/switch_commands.txt'

# Get connection type
connection_type = input("Select connection type (usb/ip): ")

if connection_type.lower() == "usb":
    connection_method = "USB"
    # Find available USB ports
    available_ports = list(serial.tools.list_ports.comports())

    if not available_ports:
        logger.error("No USB ports found.")
        sys.exit(1)

    # Connect to the first available USB port
    ser = None
    for port in available_ports:
        try:
            if 'USB' in port.device:
                ser = serial.Serial(port.device, baudrate=9600, timeout=1)
                if ser.isOpen():
                    break
                else:
                    logger.warning(f"Failed to open USB port: {port.device}")
                    ser.close()
        except serial.SerialException:
            continue
    else:
        logger.error("Unable to connect to any USB port.")
        sys.exit(1)

    with ser:
        # Send config
        with open(config_file) as f:
            commands = f.readlines()

        username = getpass("Enter your username: ")
        password = getpass("Enter your password: ")

        send_command(ser, "enable")
        send_command(ser, username)
        send_command(ser, password)

        for command in commands:
            send_command(ser, command.strip())

elif connection_type.lower() == "ip":
    connection_method = "IP"
    # IP connection code
    ip = input("Enter the switch IP address: ")
    username = getpass("Enter your username: ")
    password = getpass("Enter your password: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=password)

    channel = client.invoke_shell()
    with open(config_file) as f:
        commands = f.readlines()

    for command in commands:
        send_command(channel, command.strip())

    client.close()

else:
    logger.error("Invalid connection type")
    sys.exit(1)

logger.info("Configuration completed successfully!")
logger.info(f"Connection method: {connection_method}")
