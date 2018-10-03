import platform
if platform.system() != 'Windows':
    import RPi.GPIO as GPIO
    import serial
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import time, os, sys, select, logging, argparse

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

#GPIO Functions

def GPIO_Setup():

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(S0,GPIO.OUT)
    GPIO.setup(S1,GPIO.OUT)
    GPIO.setup(S2,GPIO.OUT)
    GPIO.setup(S3,GPIO.OUT)

    GPIO.setup(GPIO0,GPIO.OUT)
    GPIO.setup(RST,GPIO.OUT)

def GPIO_Default():

    GPIO.output(S0,0)
    GPIO.output(S1,0)
    GPIO.output(S2,0)
    GPIO.output(S3,0)

    GPIO.output(GPIO0,1)
    GPIO.output(RST,1)

def reset_esp(bootmode):
    GPIO.output(GPIO0,bootmode)
    GPIO.output(RST,0)
    time.sleep(.5)
    GPIO.output(RST,1)
    time.sleep(.5)

def esp_selector(esp):
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

def select_esp(array):
    GPIO.output(S0,int(array[0]))
    GPIO.output(S1,int(array[1]))
    GPIO.output(S2,int(array[2]))
    GPIO.output(S3,int(array[3]))

def temp_flash(esp, port, location, file):
    print ('Flashing ESP: ' + str(esp))

    #Select ESP
    select_esp(esp_selector(esp))

    #Reset ESP to Program Mode
    reset_esp(0)

    #Flash ESP
    command = esptool_path + ' --port ' + port + ' write_flash ' + location + ' ' + file
    os.system(command)

    #Reset ESP to Boot Mode
    reset_esp(1)

    #Read ESP Serial for 10 Lines
    # esp_serial = serial.Serial('/dev/serial0','115200')
    # for x in range(1,11):
    #     try:
    #         print (esp_serial.readline())
    #     except SerialException:
    #         print ('port already open')
    # esp_serial.close()

#Comms Functions
def connect(ADDR,CONNECTED):
    while CONNECTED==False:
        try:
            client_socket.connect(ADDR)
            CONNECTED = True
        except:
            print ('No Server Found!')

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg == 'Name?':
                if platform.system() == 'Windows':
                    client_socket.send(bytes(my_name, "utf8"))
                else:
                    client_socket.send(my_name)
            elif my_name in msg:
                command = msg.split(' ')
                temp_flash(command[1], serial_port, flash_location, file_location)
                client_socket.send('Done!')
                print (command)
        except OSError:  # Possibly client has left the chat.
            break

def send(message):  #Send Message
    """Handles sending of messages."""
    client_socket.send(bytes(message, "utf8"))
    if message == "{quit}":
        client_socket.close()

## Variables

#Pin Numbers
my_name = platform.node()
S0 = 31
S1 = 33
S2 = 35
S3 = 37
GPIO0 = 38
RST = 40

#Other Variables
esptool_path = '/home/pi/esptool/esptool.py'
serial_port = '/dev/serial0'
flash_location = '0x0'
file_location = '/home/pi/SpamCount.bin'

if platform.system() != 'Windows':
    #Setup GPIO
    GPIO_Setup()

if platform.system() != 'Windows':
    #Default GPIO Values
    GPIO_Default()

#Select, Reset, Flash & Read ESP
#temp_flash(1, serial_port, flash_location, file_location)
#temp_flash(7, serial_port, flash_location, file_location)
#temp_flash(10, serial_port, flash_location, file_location)

if platform.system() != 'Windows':
    #Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP of the Mgmt PC")
    args = parser.parse_args()
    print(args.host)
    HOST = args.host
else:
    HOST = get_ip()
PORT = 5000
CONNECTED = False

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

connect_thread = Thread(target=connect(ADDR,CONNECTED))
connect_thread.start()

receive_thread = Thread(target=receive)
receive_thread.start()
