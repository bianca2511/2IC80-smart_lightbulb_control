import telnetlib
import json
import nmap
import subprocess


class Command:
    def power(status: str, duration: int = 200):
        return {"id": 0, "method": "set_power", "params": [status, "smooth", duration]}

    def color(red: int, green: int, blue: int):
        return {"id": 0, "method": "set_rgb", "params": [red * 65536 + green * 256 + blue]}

    def brightness(brightness: int):
        assert brightness > 1 and brightness <= 100
        return {"id": 0, "method": "set_bright", "params": [brightness]}
    
    def temperature(temperature: int):
        return {"id": 0, "method": "set_ct_abx", "params": [temperature]}


# Client chooses the setting to control from the list
settings = ["Power", "Color", "Brightness", "Temperature"]


def choose_setting():
    print("Available settings:")
    for i, setting in enumerate(settings):
        print(f"{i}. {setting}")
    selected_index = int(
        input("Choose a setting you want to change (enter the number): "))

    if selected_index < 0 or selected_index >= len(settings):
        print("Invalid choice. Please try again.")
    else:
        selected_setting = settings[selected_index]
    return selected_setting


def map_setting_to_command(setting):
    if(setting == 'Power'):
        power = input('Do you want to turn the light on or off? ')
        return Command.power(power)
    elif(setting == 'Color'):
        print('Choose a value between 0 and 255 for each color \n')
        r = int(input('red: '))
        g = int(input('green: '))
        b = int(input('blue: '))
        return Command.color(r, g, b)
    elif(setting == 'Brightness'):
        bright = int(input('Choose a brightnes level between 1 and 100: '))
        return Command.brightness(bright)
    elif(setting == 'Temperature'):
        temp = int(input("Choose a color temperature between 1700 and 6500: "))
        return Command.temperature(temp)


def connect_to_port(ip, port):
    try:
        # Connect to the IP and port
        telnet = telnetlib.Telnet(ip, port)
        print("Connected to " + str(ip) + " "+str(port))

    except ConnectionRefusedError:
        print("Connection refused. Make sure the IP and port are correct.")
    except Exception as e:
        print("An error occurred:", str(e))

    more = 'y'

    while(more != 'n'):
        command = map_setting_to_command(choose_setting())
        send_command(telnet, command)
        response = receive_response(telnet)
        print("Received response: ", response)
        more = input('Another command? (y/n) ')

    # Close the Telnet connection
    telnet.close()
    print("Telnet connection closed")


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
    command = ['nmap', '-p', 'T:10000-65535', '--open', ip]
    output = subprocess.check_output(command).decode('utf-8')

    lines = output.split('\n')
    for line in lines:
        if line.startswith('Host:') or line.startswith('Nmap scan report'):
            continue
        elif 'Ports:' in line:
            port_line = line.split(':')[1].strip()
            ports = port_line.split(',')
            for port in ports:
                if 'open' in port and 'tcp' in port:
                    open = int(port.split('/')[0])

    return open


def run_ipconfig():
    output = subprocess.check_output(['ipconfig']).decode('utf-8')
    print(output)


def discover_ips(wifi_ip):
    split = wifi_ip.rsplit(".", 1)

# The first part will contain the IP address without the last segment
    wifi_ip = split[0]

    command = ['nmap', '-sn', wifi_ip + ".*"]
    output = subprocess.check_output(command).decode('utf-8')
    print(output + '\n')


run_ipconfig()
wifi_ip = input("What is the Wireless LAN adapter Wifi: IPv4 Address?\n")
discover_ips(wifi_ip)

# Define the IP address you want to scan for an open port
ip = input('What is the IP address of your lightbulb from the list above?\n')
# Find an open port of the IP address using nmap
# open_port = find_open_port(ip)
open_port = 55443
if open_port:
    print("Open port found: " + str(open_port))
    # Define the port you want to connect to
    port = open_port

    # Call the connect_to_port function
    connect_to_port(ip, port)
else:
    print("No open port found for the specified IP address.")
