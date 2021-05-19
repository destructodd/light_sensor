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
token = "lifx_token_goes_here"
header = {"Authorization": "Bearer %s" % token,}
LIFXurl = "https://api.lifx.com/v1/lights/all/state"

#logical stuff
light_time = time.time()
on = False
#light level
a = 0
#required light level (set by potentiometer
c = 0
#number of readings to take
x = 30
#brightness variable
brightness = 0

#switch off json data
settings_off = {"power": "off"}

#setup spi
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

#set up analog in channel
channel0 = AnalogIn(mcp, MCP.P0)

#initialise light off with light off
requests.put(url=LIFXurl, data= settings_off, headers = header)

while True:
    try:
        #take x number of readings from analog light sensor over 3 second and return average
        a = 0
        for i in range(x+1):
            a = a + channel0.voltage
            time.sleep(1/x)
        a = a/x
        
        #read motion GPIO input (boolean output)
        b = GPIO.input(26)
          
        #read potentiometer to get light thgreshold setting
        channel1 = AnalogIn(mcp, MCP.P1)
        c = (channel1.voltage/30)
        #prevent light threshold measure from reaching zero
        if c == 0:
            c = 0.001
        
        #status reports
        if on == True:
            print("Time Until Switch Off: " + str(round((light_time - time.time())/60,1)) + " minutes")
        else:
            print("Light is Off")   
        print("Light Level:  " + str(round(a,4)))
        print("Light Threshold: " + str(round(c,4)))
        print("Movement:  " + str(b))
        print(" ")
        
        #detect if low light and movement and bulb is off
        if b == 1: 
            if on == False and a < c:
                #calcuate what starting brightness should be
                brightness = round(1-(a*(1/c)),2)
                #send api command to bulb to switch on
                settings_on = {"power": "on", "brightness": brightness, "fast": True}
                requests.put(url=LIFXurl, data= settings_on, headers = header)
                print("Light On: Brightness " + str(round(brightness*100)) +"%")
                light_time = time.time() + 1200
                on = True
            elif on == True: light_time = time.time() + 1200
            
        elif on == True:
            if time.time() > light_time:
                requests.put(url=LIFXurl, data= settings_off, headers = header)
                on = False
                print("Switched Off")
            elif a < c:
                brightness = brightness + 0.05
                if brightness > 1: brightness = 1
                settings_brightness = {"brightness": brightness}
                requests.put(url=LIFXurl, data= settings_brightness, headers = header)
                if brightness != 1: print("Brightness Up to " + str(round(brightness*100)) +"%")
            elif a > c:
                brightness = brightness - 0.05
                if brightness < 0.1: brightness = 0.1
                settings_brightness = {"brightness": brightness}
                requests.put(url=LIFXurl, data= settings_brightness, headers = header)
                if brightness != 0.1: print("Brightness Down to " + str(round(brightness*100)) +"%")
    except:
        print("an error occured")
