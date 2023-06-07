import telnetlib
import json
import nmap
import subprocess

class Command:
    def power(status: str, duration: int = 200):

        # power = "on" if power else "off"
        return {"id": 0, "method": "set_power", "params": [status, "smooth", duration]}

    def color(red: int, green: int, blue: int):
        return {"id": 0, "method": "set_rgb", "params": [red * 65536 + green * 256 + blue]}

    def brightness(brightness: int):
        assert brightness > 1 and brightness <= 100
        return {"id": 0, "method": "set_bright", "params": [brightness]}


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
    scanner = nmap.PortScanner()
    scanner.scan(ip, arguments='-T4 -p-')

    for host in scanner.all_hosts():
        if scanner[host].state() == 'up':
            for proto in scanner[host].all_tcp():
                port_list = scanner[host][proto].keys()
                for port in port_list:
                    if scanner[host][proto][port]['state'] == 'open':
                        return int(port)

    return None

def run_ipconfig():
    output = subprocess.check_output(['ipconfig']).decode('utf-8')
    print(output)

def discover_ips(wifi_ip):
    command = ['nmap', '-sn', wifi_ip[:12]+'*']
    output = subprocess.check_output(command).decode('utf-8')
    print(output + '\n')

run_ipconfig()
wifi_ip=input("What is the Wireless LAN adapter Wifi: IPv4 Address?\n")
discover_ips(wifi_ip)

# Define the IP address you want to scan for an open port
ip = input('What is the IP address of your lightbulb from the list above?\n')
# Find an open port of the IP address using nmap
open_port = find_open_port(ip)
if open_port:
    print("Open port found: " + str(open_port))
    # Define the port you want to connect to
    port = open_port

    # Call the connect_to_port function
    connect_to_port(ip, port)
else:
    print("No open port found for the specified IP address.")
