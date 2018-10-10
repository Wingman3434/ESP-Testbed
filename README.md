# ESP-Testbed

The ESP8266 is a low-cost Wi-Fi microcontroller with full TCP/IP stack. Packaged into modules the ESP8266 is espically usefull in research and development projects, specifically in the area of home automation and the internet of things. The ESP-Testbed project was created to solve a problem 
A Python based tool to flash and communicate with ESP-01 test-beds.

## Intro

The ESP-01 Test-bed is a protype device built to power and flash (program) up to 15 ESP-01 modules. 

The management software (Link) runs on the programmer’s pc and controls the functions of each tower, this means the programmer isn’t required to log into each PI to flash the ESPs. 

The ESP-Tower controller runs the client software (Link) at boot up. Each Test-bed is controlled via a Raspberry Pi 3 Model B+ connected to the board via a 2 x 20 pin female header. These Raspberry Pis run Raspbian with some extras installed and some slight configuration changes, the wiki (Link) details how to set-up and configure a Raspberry PI for an ESP Test-bed.
