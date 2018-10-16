## Introduction

Despite decades of research, home automation has yet to make a significant impact on our everyday lives. Many researchers are developing protocols to remove the need for a central controller. These protocols are often developed for the ESP8266, a low-cost Wi-Fi microcontroller. It can be found on the ESP-01 development module, an 8-pin scaled down version of the full ESP8266 microcontroller. With a lack of an onboard serial controller and voltage regulator, the ESP-01 is difficult to program on a large scale. The ESP-Testbed was created to solve the problem of scalability in these IoT research projects. The concept of the ESP-Testbed is a highly scalable, low-cost prototyping system which allows researchers to test ESP8266 protocols and firmware on a large scale.

## Key Features

- Efficiently Flash many ESP-01 modules with any firmware
- Power a full tower of 15 devices
- Centrally manage a large number of ESP towers
- Test WiFi interference in 3 dimensions
- Communicate with a large number of ESP’s via serial

## Software

The ESP Testbed uses a client-server model via TCP sockets. The Raspberry Pi acts as the client, indefinitely attempting to connect to the server. The user starts the server, which accepts all client connection requests. The server imports data from the configuration file processes it and sends commands to the Raspberry Pi. The client is responsible for interfacing with the ESPs, it controls the Pi’s GPIO pins and serial communication. During programming, the Pi will send progress data back to the server, showing the user progress without the need to connect directly to the tower.

## Make or Buy

The ESP Testbed is a fully open source project, allowing you to download the required files and start building your own towers. This task can be a little daunting so the ESP Testbed team is happy to help. For a small fee, we can assemble, test and ship as many towers as you require.  