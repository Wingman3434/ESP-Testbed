import platform
import RPi.GPIO as GPIO
import serial
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import time, os, sys, select, logging, argparse, subprocess

#GPIO Functions
def GPIO_Setup():
    towerlog.debug('GPIO_Setup Started')
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(S0,GPIO.OUT)
    GPIO.setup(S1,GPIO.OUT)
    GPIO.setup(S2,GPIO.OUT)
    GPIO.setup(S3,GPIO.OUT)
    GPIO.setup(GPIO0,GPIO.OUT)
    GPIO.setup(RST,GPIO.OUT)
    towerlog.debug('GPIO_Setup Complete')
    
def GPIO_Default():
    towerlog.debug('GPIO_Default Started')
    GPIO.output(S0,0)
    GPIO.output(S1,0)
    GPIO.output(S2,0)
    GPIO.output(S3,0)
    GPIO.output(GPIO0,1)
    GPIO.output(RST,1)
    towerlog.debug('GPIO_Default Complete')
    
def esp_selector(esp):
    towerlog.debug('esp_selector Started')
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
    towerlog.debug('esp_selector Complete')
      
def select_esp(array):
    towerlog.debug('select_esp Started')
    GPIO.output(S0,int(array[0]))
    GPIO.output(S1,int(array[1]))
    GPIO.output(S2,int(array[2]))
    GPIO.output(S3,int(array[3]))
    towerlog.debug('select_esp Complete')

def reset_esp(esp, bootmode):
    towerlog.debug('reset_esp Started')
    #Select ESP
    select_esp(esp_selector(esp))
    #Set GPIO Bootmode
    GPIO.output(GPIO0,bootmode)
    #Set RST LOW
    GPIO.output(RST,0)
    time.sleep(1)
    #Set RST HIGH
    GPIO.output(RST,1)
    time.sleep(1)
    towerlog.debug('reset_esp Complete')
    
def flash_esp(esp, port, location, file):
    towerlog.info('Flashing ESP: ' + str(esp))
    #Reset ESP to Program Mode
    reset_esp(esp,0)
    #Build command to call esptool.py
    command = []
    command.append(esptool_path)
    command.append('--port')
    command.append(port)
    command.append('write_flash')
    command.append(location)
    command.append(file)
    #Create subprocess
    flash_shell = subprocess.Popen(command,stdout=subprocess.PIPE)
    while True: #Check output, log and send to server
        cmd_output = flash_shell.stdout.readline().rstrip()
        if cmd_output == '' and flash_shell.poll() is not None:
            break
        else:
            towerlog.info(cmd_output)
            client_socket.send(cmd_output)
    #Reset ESP to Boot Mode
    reset_esp(esp,1)
            
def receive():
    global connected
    try:
        msg = client_socket.recv(BUFSIZ).decode("utf8")
        if msg == 'Name?': # Name Request
            client_socket.send(my_name) # Name Response
        elif msg == 'FILES!': # File Transfer Request
            size = client_socket.recv(16) # Filename Size
            if not size:
                towerlog.info('File Transfer Error!')
            size = int(size, 2)
            filename = client_socket.recv(size) # Filename
            filesize = client_socket.recv(32) # File Size
            filesize = int(filesize, 2)
            file_to_write = open(filename, 'wb')
            chunksize = 4096
            # Recieve File data
            while filesize > 0:
                if filesize < chunksize:
                    chunksize = filesize
                data = client_socket.recv(chunksize)
                file_to_write.write(data)
                filesize -= len(data)
            file_to_write.close() # Write Data to new file
            client_socket.send('Done') # File Transfered
        elif msg == 'Flash':
            size = client_socket.recv(32) # Command Size
            if not size:
                towerlog.info('Flash Command Transfer Error!')
            size = int(size, 2)
            command = client_socket.recv(size) # Command
            command = command.split(' ')
            flash_esp(command[2], serial_port, flash_location, command[3])
            time.sleep(2)
            client_socket.send('Done')
    except: # Connection Error
        connected = False
        client_socket.close()
        time.sleep(2)

def send(message):  #Send Message
    client_socket.send(bytes(message, "utf8"))
    if message == "{quit}":
        client_socket.close()

##Logging
# create logger with 'ESP Logger'
towerlog = logging.getLogger('Tower_Logger')
towerlog.setLevel(logging.DEBUG)
# create file handler which logs everything
fh = logging.FileHandler('Tower_Log.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
towerlog.addHandler(fh)
towerlog.addHandler(ch)

## Variables

#Pin Numbers
my_name = platform.node()
S0 = 31
S1 = 33
S2 = 35
S3 = 37
GPIO0 = 38
RST = 40

#Env Variables
esptool_path = '/home/pi/esptool/esptool.py'
serial_port = '/dev/serial0'
flash_location = '0x0'

#Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("host", help="IP of the Mgmt PC")
args = parser.parse_args()

#Socket Variables
connected = False
HOST = args.host
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)

#Setup GPIO
GPIO_Setup()

#Default GPIO Values
GPIO_Default()

# Main Connection Loop
while True:
    while not connected: # Remake socket and try to connect
        try:
            client_socket = socket(AF_INET, SOCK_STREAM)
            towerlog.info('Attemting to connect to server')
            client_socket.connect(ADDR)
            connected = True
            towerlog.info('Connected to host!')
        except:
            towerlog.info('Connection Timeout')
            connected = False
            time.sleep(2)
    while connected: # When connected call recieve()
        receive()
