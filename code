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
token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
header = {"Authorization": "Bearer %s" % token,}
LIFXurl = "https://api.lifx.com/v1/lights/all/state"
settings_off = {"power": "off"}
current_brightness = 0

#logical stuff
light_time = time.time()
on = False

#setup spi
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

#start with light off
requests.put(url=LIFXurl, data= settings_off, headers = header)

while True:
    #read light analog input
    channel = AnalogIn(mcp, MCP.P0)
    a = channel.voltage
    #read motion GPIO input
    b = GPIO.input(26)
    
    print("Light Level:  " + str(round(a,4)))
    print("Movement:  " + str(b))
    print("Time Until Switch Off: " + str(round(light_time - time.time())))
    print(" ")
    new_brightness = round(1-(a*20),2)
    
    #detect if low light and movement
    if a < 0.05 and b == 1:
        if current_brightness == 0:
            current_brightness = new_brightness
            print("at zero")
        elif new_brightness > current_brightness:
            current_brightness = current_brightness +0.02
            print("increase")
        elif new_brightness < current_brightness:
            current_brightness = current_brightness -0.02
            print("decrease")
        
        if current_brightness > 1.0:
            current_brightness = 1.0
        
        
        settings_on = {"power": "on", "brightness": current_brightness, "fast": True}
        requests.put(url=LIFXurl, data= settings_on, headers = header)
        print("Light On: Brightness " + str(round(current_brightness*100)) +"%")
        light_time = time.time() + 600
        on = True
     
    #check if time has run out to switch light off
    elif time.time() >= light_time and on == True:
        requests.put(url=LIFXurl, data= settings_off, headers = header)
        on = False
        print("Switched Off")
    elif light_time > 86400:
        light_time == time.time()
    
    #sleep for one second - seems to crash if not limited
    time.sleep(1)
