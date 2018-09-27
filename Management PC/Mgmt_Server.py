import yaml, socket, select, logging, signal, time
from collections import OrderedDict

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

def print_menu():
    print (30 * '-')
    print ("   M A I N - M E N U")
    print (30 * '-')
    print ("1. Option 1")
    print ("2. Option 2")
    print ("3. Option 3")
    print (30 * '-')

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def get_ip():
    esplog.info('get_ip started')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    esplog.info('get_ip complete : ' + IP )
    return IP

def send_file(filename, buffer):
    esplog.info('send_file started')
    f = open(filename,'rb')
    while True:
        l = f.read(buffer)
        while (l):
            sock.send(l)
            l = f.read(buffer)
        if not l:
            f.close()
    esplog.info(filename + ' Sent!')

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

config = import_config('config.yaml')

esplog.info('tower IPs and data array started')
tower_ips = []
tower_data = []
for header in config:
    if ('tower' in header.lower() and config[header] != None):
        tower_ips.append(config[header]['IP'])
        temp_list = []
        for key in config[header]:
            if (key.lower() !='ip' and config[header][key] != None):
                #print (key)
                temp_list.append([key, config[header][key]])
        tower_data.append(temp_list)
    #elif ('Files' in key and config[key] != None):
        
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

for x in range(0,16):
    print (esp_selector(x))

# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 1024 # Advisable to keep it as an exponent of 2
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# this has no effect, why ?
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((get_ip(), PORT))
server_socket.listen(10)

# Add server socket to the list of readable connections
CONNECTION_LIST.append(server_socket)

print ("Chat server started on port " + str(PORT))

while 1:
    # Get the list sockets which are ready to be read through select
    # read_sockets,write_sockets,error_sockets = select.select([],CONNECTION_LIST,[])
    for sock in CONNECTION_LIST:
        #New connection
        if sock == server_socket:
            # Handle the case in which there is a new connection recieved through server_socket
            sockfd, addr = server_socket.accept()
            CONNECTION_LIST.append(sockfd)
            print ("Client (%s, %s) connected" % addr)
    #Some incoming message from a client
    else:
        # Send/recieve data to/from client
        try:
            data = sock.recv(RECV_BUFFER)
            print(data.decode())
            if data.decode()== "Hello, World!":
                message = "Hello, World!".encode()
                sock.send(message)
            else:
                message = "Goodbye, World!".encode()
                sock.send(message)
                sock.close()
                CONNECTION_LIST.remove(sock)
        except:
            #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
            print ("Client (%s, %s) is offline" % addr)
            sock.close()
            CONNECTION_LIST.remove(sock)

server_socket.close()

#find key with tower
#check if ip exists
#save ip to array

## FLASHING BREAKDOWN
# Generate Bash script for PI to return
# Send script to PI
# send command for PI to run script
# Listen for reply

##SCRIPT BREAKDOWN
# Select ESP
# Reset to Programming Mode
# Flash with ESP Flasher
