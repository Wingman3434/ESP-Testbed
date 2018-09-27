import RPi.GPIO as GPIO
import time, subprocess, serial, os

#Pin Numbers
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
file_location = '/home/pi/esptool/test/images/SpamCount.bin'

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
    #print (command)
    os.system(command)
    #subprocess.call(['/home/pi/esptool/esptool.py', '--port', '/dev/serial0', 'write_flash', '0x0', '/home/pi/esptool/test/images/SpamCount.bin'], shell=True)
    #flash_command = subprocess.Popen([esptool_path,'--port',serial_port,'write_flash',flash_location,file_location], stdout=subprocess.PIPE)
    #output = flash_command.communicate()[0]
    #print output
    
    #Reset ESP to Boot Mode
    reset_esp(1)
    
    #Read ESP Serial for 10 Lines
    esp_serial = serial.Serial('/dev/serial0','115200')
    for x in range(1,11):
        try:
            print (esp_serial.readline())
        except SerialException:
            print ('port already open')
    esp_serial.close()

#Setup GPIO
GPIO_Setup()

#Default GPIO Values
GPIO_Default()

#Select, Reset, Flash & Read ESP
temp_flash(1, serial_port, flash_location, file_location)
temp_flash(7, serial_port, flash_location, file_location)
temp_flash(10, serial_port, flash_location, file_location)