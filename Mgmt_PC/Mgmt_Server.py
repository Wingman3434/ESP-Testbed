from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import yaml, select, logging, signal, time, os, re, argparse
from collections import OrderedDict

# Gets the IP of the device its running on. Mainly used for debugging
def get_ip():
    mgmtlog.debug('get_ip() Started')
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
    mgmtlog.debug('get_ip(): ' + IP)

#Sets up handling for incoming clients
def accept_incoming_connections():
    while 1:
        mgmtlog.debug('accept_incoming_connections() Started')
        client, client_address = SERVER.accept() # Accept Client Connection Request
        mgmtlog.info("%s:%s has connected." % client_address)
        addresses[client] = client_address # Add client to addresses list
        Thread(target=handle_client, args=(client,)).start() # Start new thread

#Handles a single client connection
def handle_client(client):  # Takes client socket as argument.
    mgmtlog.debug('handle_client(client) Started')
    client.send(bytes("Name?", "utf8")) # Name Request
    name = client.recv(BUFSIZ).decode("utf8") # Name Response
    global completed_towers
    if name in completed_towers:
        client.close()
    else:
        completed_towers.append(name)
        logname = name + '.log'
        tower=int(re.search(r'\d+', name).group())-1 # Gives us Tower Index Number
        clients[client] = name # Add client to clients list
        # Transfer files listed in the configuration YAML
        for file in files:
            client.send(bytes('FILES!',"utf8")) # File Transfer Request
            filename = files[file]
            size = len(filename)
            size = bin(size)[2:].zfill(16) # encode filename size as 16 bit binary
            filesize = os.path.getsize(filename)
            filesize = bin(filesize)[2:].zfill(32) # encode filesize as 32 bit binary
            client.send(bytes(size,"utf8")) # Send Filename size
            client.send(bytes(filename,"utf8")) # Send Filename
            client.send(bytes(filesize,"utf8")) # Send File Size
            file_to_send = open(filename, 'rb')
            l = file_to_send.read()
            client.sendall(l) # Send File Data
            file_to_send.close()
            mgmtlog.info(file + ' Sent')
            done = False
            # Wait for transfer complete
            while done == False:
                if client.recv(BUFSIZ).decode("utf8") == 'Done':
                    done = True
                else:
                    continue # Transfer next file
        # Iterates through the tower_data array
        for esp in range(len(tower_data[tower])):
            # Creates a command to send to the tower
            command = 'Tower' + str(tower+1) + ' flash ' + str(esp)
            command += ' ' + str(files[tower_data[tower][esp][1]])
            mgmtlog.info(command)
            # Send Command to client
            client.send(bytes(command,"utf8"))
            # Waits for Pi to respond before sending next command
            result = 0 # 0=Flashing 1=Success 2=Failed
            while result == 0:
                reply = client.recv(BUFSIZ).decode("utf8")
                mgmtlog.info(reply)
                if "seconds (effective" in reply and result == 0:
                    line = "ESP " + str(esp) + ": Success"
                    writeline_file(logname, line)
                    result = 1
                elif reply == 'Done' and result == 0:
                    line = "ESP " + str(esp) + ": Failure - Check Device"
                    writeline_file(logname, line)
                    result = 2
                else:
                    continue
        client.close()

# Broadcasts a message to all the clients
def writeline_file(filename, data):
    if os.path.exists(filename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    file = open(filename,append_write)
    file.write(data + '\n')
    file.close()

def broadcast(msg, prefix=""):  # prefix is for name identification.
    mgmtlog.debug(msg + ' sent via broadcast()')
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

# Imports the YAML Config File
def import_config(configfile):
    mgmtlog.debug('import_config Started')
    with open(configfile, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            mgmtlog.info(exc)
    return data
    stream.close
    mgmtlog.debug('import_config complete')
    mgmtlog.debug(data)

# Creates arrays from the YAML File, easier to iterate through
def get_tower_info():
    mgmtlog.debug('tower IPs and data array started')
    for header in config:
        if ('tower' in header.lower() and config[header] != None):
            tower_ips.append(config[header]['IP'])
            temp_list = []
            for key in config[header]:
                if (key.lower() !='ip' and config[header][key] != None):
                    temp_list.append([key, config[header][key]])
            tower_data.append(temp_list)
    mgmtlog.debug('tower ips : ' + str(tower_ips))
    mgmtlog.debug('tower data : ' + str(tower_data))

    # Future Expansion - Add Keywords to Config File
##    for tower in tower_data:
##        for esp in tower:
##            print (esp[0])
##            if ('all' in esp[0].lower()):
##                print ('Make All ESPs Flash')
##            elif ('odd' in esp[0].lower()):
##                print ('Make All Odd ESPs Flash')
##            elif ('even' in esp[0].lower()):
##                print ('Make All Even ESPs Flash')

# create logger with 'ESP Logger'
mgmtlog = logging.getLogger('Mgmt_Logger')
mgmtlog.setLevel(logging.DEBUG)
# create file handler which logs everything
fh = logging.FileHandler('Mgmt_Server.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
mgmtlog.addHandler(fh)
mgmtlog.addHandler(ch)

#Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("config", help="YAML Configuration Filename")
args = parser.parse_args()

#Import config and build array
tower_ips = []
tower_data = []
completed_towers = []
config = import_config(args.config)
get_tower_info()
files = config['Files']

#Server Variables
clients = {}
addresses = {}
HOST = get_ip()
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

mgmtlog.info("Chat server started on port " + str(PORT))
SERVER.listen(5)
mgmtlog.info("Waiting for connection...")
ACCEPT_THREAD = Thread(target=accept_incoming_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
SERVER.close()
