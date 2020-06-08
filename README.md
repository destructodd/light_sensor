# light_sensor
Control a smart bulb with raspberry pi sensors.

The project uses a PIR sensor to detect movement and a photo transistor to measure ambient light. When movement and ambient light below the threshold set are deteced simultaneously, the bulb is switched on for 10 minutes. During that 10 minutes, if further movement is detected, the time until switch off will be pushed forward to ten minutes from that time. If no movement is detected for ten minutes the bulb is swtiched off.  

Initial brightness is determined by calculating the percentage by which the current light measurement is below the threshold, e.g. if the threshold is 0.05 and the measurement is 0.0375, the bulb will switch on with 25% brightness. After being switched on, each time the sensor detects further movement a new brightness will be calculated based on current ambient light levels. If the new brightness is higher/lower than the current brightness, the current brightness will be increased/decreased 2%. The incremental change is to prevent sudden large changing in brightness. 

The raspberry pi communicates with the bulb using the LIFX API (https://api.developer.lifx.com), though can potentially work with any smart bulb brand with a public api. 

The photo transistor output is analog. As the raspberry pi does not have any analog inputs as standard, a MCP3008 analog to digitial converter was used (https://learn.adafruit.com/mcp3008-spi-adc/python-circuitpython). An easier but more expensive solution would an Explorer Hat, which provides 4 analog input channels. 

Potential Improvements 
-Variable resistor to adjust light threshold
-adjust bulb colour based on a temperature sensor
