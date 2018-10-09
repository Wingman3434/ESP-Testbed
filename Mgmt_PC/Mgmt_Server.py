from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import yaml, select, logging, signal, time
from collections import OrderedDict

# Gets the IP of the device its running on. Mainly used for debugging
def get_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

#Sets up handling for incoming clients
def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Name?", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

#Handles a single client connection
def handle_client(client):  # Takes client socket as argument.
    name = client.recv(BUFSIZ).decode("utf8")
    tower=int(name[-1])-1 # Gives us Tower Index Number
    filename = 'SpamCount.bin'
    client.send(bytes('Filename', "utf8"))
    if client.recv(BUFSIZ).decode("utf8") == 'Send Filename':
        client.send(bytes(filename, "utf8"))
    client.send(bytes('File', "utf8"))
    if client.recv(BUFSIZ).decode("utf8") == 'Send File':
        with open(filename, 'rb') as filedata:
            client.sendfile(filedata, 0)

    msg = "%s has joined the chat!" % name
    print (msg)
    clients[client] = name

    while True:
        # Iterates through the tower_data array
        for esp in range(len(tower_data[tower])):
            # Creates a command to send to the tower
            command = 'Tower' + str(tower+1) + ' ' + str(esp) + ' ' + str(tower_data[tower][esp][1])
            print(command)
            # Broadcasts the command
            broadcast(bytes(command, "utf8"))
            # Waits for Pi to respond before sending next command
            done = False
            while done == False:
                if client.recv(BUFSIZ).decode("utf8") == 'Done':
                    done = True
                else:
                    continue

# Broadcasts a message to all the clients
def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

# Creates an array to select esps. Used on the Pis
def esp_selector(esp):
    esplog.info('esp_selector started')
    if int(esp) == 0:
        esp_binary = '0b0000'
    elif int(esp) == 1:
        esp_binary = '0b0001'
    elif int(esp) == 2:
        esp_binary = '0b0010'
    elif int(esp) == 3:
        esp_binary = '0b0011'
    elif int(esp) == 4:
        esp_binary = '0b0100'
    elif int(esp) == 5:
        esp_binary = '0b0101'
    elif int(esp) == 6:
        esp_binary = '0b0110'
    elif int(esp) == 7:
        esp_binary = '0b0111'
    else:
        esp_binary = bin(int(esp))
    return [esp_binary[5], esp_binary[4], esp_binary[3], esp_binary[2]]
    esplog.info('esp_selector complete')

# Imports the YAML Config File
def import_config(configfile):
    esplog.info('import_config started : ' + configfile)
    with open(configfile, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data
    stream.close
    esplog.info('import_config complete')
    esplog.info(data)

# Creates arrays from the YAML File, easier to iterate through
def get_tower_info():
    esplog.info('tower IPs and data array started')
    for header in config:
        if ('tower' in header.lower() and config[header] != None):
            tower_ips.append(config[header]['IP'])
            temp_list = []
            for key in config[header]:
                if (key.lower() !='ip' and config[header][key] != None):
                    temp_list.append([key, config[header][key]])
            tower_data.append(temp_list)

    esplog.info('tower ips : ' + str(tower_ips))
    esplog.info('tower data : ' + str(tower_data))

    for tower in tower_data:
        for esp in tower:
            print (esp[0])
            if ('all' in esp[0].lower()):
                print ('Make All ESPs Flash')
            elif ('odd' in esp[0].lower()):
                print ('Make All Odd ESPs Flash')
            elif ('even' in esp[0].lower()):
                print ('Make All Even ESPs Flash')

#def get_file_list():
 #   for filename in config['Files']
# create logger with 'ESP Logger'
esplog = logging.getLogger('ESP_Logger')
esplog.setLevel(logging.DEBUG)
# create file handler which logs everything
fh = logging.FileHandler('ESP_Tower.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
esplog.addHandler(fh)
esplog.addHandler(ch)

#Import config and build array
tower_ips = []
tower_data = []
config = import_config('config.yaml')
get_tower_info()

#Server Variables
clients = {}
addresses = {}

HOST = get_ip()
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

print ("Chat server started on port " + str(PORT))

SERVER.listen(5)
print("Waiting for connection...")
ACCEPT_THREAD = Thread(target=accept_incoming_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
SERVER.close()
