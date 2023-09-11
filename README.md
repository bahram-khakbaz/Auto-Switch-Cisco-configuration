# Auto-Switch-Cisco-configuration
Auto-Switch-configuration with python script
The written codes are for configuring the Cisco switches through the network and through the serial cable, and for ease of work, you need to put the configurations in a text file and add the path to the text file in the script.
Note: You must install the required libraries.
libraries:
os
sys
logging
Paramiko
time
from getpass import getpass
serial.tools.list_ports


Note : Two files have been placed, which are due to the type of connection to the serial port in Linux and Windows, which you can use based on the OS ( windows or Linux ) you have installed so that the script will run without any problems.
