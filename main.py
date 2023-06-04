import telnetlib
import json
import nmap
import subprocess

command_list = [
    {"id": 0, "method": "set_power", "params": ["on", "smooth", 200]},
    {"id": 0, "method": "set_power", "params": ["off", "smooth", 200]},
]

#Client chooses the command from the list
def choose_command():
    print("Available commands:")
    for index, obj in enumerate(command_list, start=1):
        print("{index}. {obj}")

    selected_index = int(
        input("Choose a command (enter the corresponding number): ")) - 1

    if selected_index < 0 or selected_index >= len(command_list):
        print("Invalid choice. Please try again.")
    else:
        selected_command = command_list[selected_index]
        
    return selected_command

def connect_to_port(ip, port):
    try:
        # Connect to the IP and port
        telnet = telnetlib.Telnet(ip, port)
        print("Connected to {ip}:{port}")

        # Send a command and receive the response
        command = choose_command()
        send_command(telnet, command)
        response = receive_response(telnet)
        print("Received response:\n", response)

        # # Close the Telnet connection
        # tn.close()
        # print("Telnet connection closed")

    except ConnectionRefusedError:
        print("Connection refused. Make sure the IP and port are correct.")
    except Exception as e:
        print("An error occurred:", str(e))


def send_command(telnet, command):
    # Convert the command to JSON string
    json_command = json.dumps(command)

    # Send the JSON command
    telnet.write(json_command.encode('utf-8') + b'\n')


def receive_response(tn):
    # Read the response until a newline character is encountered
    response = tn.read_until(b'\n').decode('utf-8')

    # Convert the response from JSON string to Python object
    json_response = json.loads(response)
    return json_response


def bettercap_command(command):
    try:
        # Run bettercap command and capture the output
        output = subprocess.check_output(['bettercap', '-eval', command])

        # Print the command output
        print(output.decode('utf-8'))

    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the bettercap command:", e)


def net_probe():
    print("Running net.probe...")
    bettercap_command('net.probe on')


def net_recon():
    print("Running net.recon...")
    bettercap_command('net.recon on')


def net_show():
    print("Running net.show...")
    bettercap_command('net.show')


def find_open_port(ip):
    scanner = nmap.PortScanner()
    scanner.scan(ip, arguments='-p-')

    for host in scanner.all_hosts():
        if scanner[host].state() == 'up':
            for proto in scanner[host].all_protocols():
                port_list = scanner[host][proto].keys()
                for port in port_list:
                    if scanner[host][proto][port]['state'] == 'open':
                        return int(port)

    return None


# Call the functions to run the bettercap commands
net_probe()
net_recon()
net_show()


# Define the IP address you want to scan for an open port
ip = input('What IP address do you want to use?\n')

# Find an open port of the IP address using nmap
open_port = find_open_port(ip)
if open_port:
    print("Open port found: {open_port}")
    # Define the port you want to connect to
    port = open_port

    # Call the connect_to_port function
    connect_to_port(ip, port)
else:
    print("No open port found for the specified IP address.")
