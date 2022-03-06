import uos
import machine 
import ntptime
import time
import camera
from config import *
from umqtt.simple2 import MQTTClient

try:
    # configure pins
    led = machine.Pin(4, machine.Pin.OUT)

    # initialize camera
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)

    # initialize MQTT client
    c = MQTTClient(mqtt_config['client_id'], mqtt_config['server'], port=mqtt_config['port'])
    c.connect()

except Exception as e:
    print("Error ocurred: " + str(e))
    time.sleep_ms(5000)
    machine.reset()

error_counter = 0
loop = True
while loop:
    try:
        # get image
        led.value(1)
        buf = camera.capture()
        led.value(0)
        
        # publish image
        c.publish(mqtt_config['topic'], buf)

        # sleep
        time.sleep_ms(app_config['sleep-ms'])
    
    except KeyboardInterrupt:
        print("Stopped!")
        loop = False

    except Exception as e:
        print("Error ocurred: " + str(e))
        error_counter = error_counter + 1
        if error_counter > app_config['max-error']:
            machine.reset()