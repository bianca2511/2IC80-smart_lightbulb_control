import telnetlib
import json
import nmap
import subprocess


class Command:
    def power(power: bool, duration: int = 200):
        power = "on" if power else "off"

        return {"id": 0, "method": "set_power", "params": [power, "smooth", duration]}

    def color_temperature(temperature: int):
        # ct 1700 - 6500

        assert temperature >= 1700
        assert temperature <= 6500

        return {"id": 0, "method": "set_ct_abx", "params": [temperature]}


command_list = [
    Command.power(True),
    Command.power(False),
    Command.power(True, 1000),
    Command.power(False, 1000),
    Command.color_temperature(1700),
    Command.color_temperature(6500),
]
# Client chooses the command from the list


def choose_command():
    print("Available commands:")
    for i, command in enumerate(command_list):
        print(f"{i}. {command}")
    selected_index = int(
        input("Choose a command (enter the corresponding number): "))

    if selected_index < 0 or selected_index >= len(command_list):
        print("Invalid choice. Please try again.")
    else:
        selected_command = command_list[selected_index]

    return selected_command


def connect_to_port(ip, port):
    try:
        # Connect to the IP and port
        telnet = telnetlib.Telnet(ip, port)
        print("Connected to " + str(ip) + " "+str(port))

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
    print("Sending...")
    json_command = json.dumps(command)
    print(json_command)
    # Send the JSON command
    telnet.write((json_command + '\r\n').encode('ascii'))


def receive_response(tn):
    # Read the response until a newline character is encountered
    response = tn.read_until(b'\n').decode('utf-8')

    # Convert the response from JSON string to Python object
    json_response = json.loads(response)
    return json_response


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


# Define the IP address you want to scan for an open port
# ip = input('What IP address do you want to use?\n')
ip = "192.168.178.140"
# Find an open port of the IP address using nmap
# open_port = find_open_port(ip)
open_port = 55443
if open_port:
    print("Open port found:" + str(open_port))
    # Define the port you want to connect to
    port = open_port

    # Call the connect_to_port function
    connect_to_port(ip, port)
else:
    print("No open port found for the specified IP address.")
