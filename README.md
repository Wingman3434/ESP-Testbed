## Introduction

The ESP8266 is a low-cost Wi-Fi microcontroller with full TCP/IP stack. Packaged into modules the ESP8266 is especially useful in research and development projects, specifically in the area of home automation and the Internet of Things. The ESP-Testbed was created to solve the problem of scalability in these IoT research projects. The concept of the ESP-Testbed is a highly scalable, low-cost prototyping system which allows researchers to test ESP8266 protocols and firmware on a large scale. The system is designed for the ESP-01 module, an 8-pin scaled down version of the full ESP8266 microcontroller.

A Python-based tool to flash and communicate with ESP-01 test-beds.

## Software

The ESP-01 Test-bed is a prototype device built to power and flash (program) up to 15 ESP-01 modules. 

The management software (Link) runs on the programmer’s pc and controls the functions of each tower, this means the programmer isn’t required to log into each PI to flash the ESPs. 

The ESP-Tower controller runs the client software (Link) at boot up. Each Test-bed is controlled via a Raspberry Pi 3 Model B+ connected to the board via a 2 x 20 pin female header. These Raspberry Pis run Raspbian with some extras installed and some slight configuration changes, the wiki (Link) details how to set-up and configure a Raspberry PI for an ESP Test-bed.
