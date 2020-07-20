import time
import RPi.GPIO as GPIO
import requests
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

#set up input pin for motion sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(26,GPIO.IN)

#setup lifx api stuff
token = "c9695123ccb4310964664293fefbc311d18e24d1969e5d5dc6a5f470970df236"
header = {"Authorization": "Bearer %s" % token,}
LIFXurl = "https://api.lifx.com/v1/lights/all/state"
settings_off = {"power": "off"}
current_brightness = 0

#logical stuff
light_time = time.time()
on = False
a = 0
x = 30

#setup spi
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

#start with light off
requests.put(url=LIFXurl, data= settings_off, headers = header)

while True:
    #read light sensor analog input
    channel0 = AnalogIn(mcp, MCP.P0)
    
    #take x number of readings at a rate of 10 p/s
    a = 0
    for i in range(x+1):
        a = a + channel0.voltage
        time.sleep(x/10)
    a = a/x
    
    #read motion GPIO input
    b = GPIO.input(26)
    
    print("Light Level:  " + str(round(a,4)))
    #read potentiometer analog input to get light sensitivity
    channel1 = AnalogIn(mcp, MCP.P1)
    c = (channel1.voltage/30)
    print("Threshold: " + str(round(c,4)))
    print("Movement:  " + str(b))
    print("Time Until Switch Off: " + str(round(light_time - time.time())))
    print(" ")
    
    #prevent light sensitivity from reaching zero to avoid divide by zero error
    if c == 0:
        c = 0.001
    
    #calculate what current brightness % should be based on light level and threshold
    new_brightness = round(1-(a*(1/c)),2)
        
    #detect if light is below threshold and movement is occuring
    if a < c and b == 1:
        #jump to suitable brightness level when lamp first turns or, rather than incrementing to it
        if current_brightness == 0:
            current_brightness = new_brightness
            print("at zero")
        #if current brightness is below calculated brightness, increase by 2%
        elif new_brightness > current_brightness:
            current_brightness = current_brightness +0.02
            print("increase")
        #if current brightness is above calculated brightness, decrease by 2%
        elif new_brightness < current_brightness:
            current_brightness = current_brightness -0.02
            print("decrease")
        
        #prevent brightness from being increased higher than 100%
        if current_brightness > 1.0:
            current_brightness = 1.0
        
        #send command to lifx api, and set the time at which the light will go off as ten minutes from current time
        #if criteria are met to switch light on, but it is already on, the switchoff time will still be updated to ten minutes from now
        settings_on = {"power": "on", "brightness": current_brightness, "fast": True}
        requests.put(url=LIFXurl, data= settings_on, headers = header)
        print("Light On: Brightness " + str(round(current_brightness*100)) +"%")
        light_time = time.time() + 600
        on = True
     
    #check if time has run out to switch light off. If it has, send off command to api. Timer resets every 24 hours.
    elif time.time() >= light_time and on == True:
        requests.put(url=LIFXurl, data= settings_off, headers = header)
        on = False
        print("Switched Off")
    elif light_time > 86400:
        light_time == time.time()
