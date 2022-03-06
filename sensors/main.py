import uos
import ntptime
import time

from dht import DHT11
from machine import Pin, I2C, ADC, reset
from config import *
from bh1750 import BH1750
from umqtt.simple2 import MQTTClient

try:
    # configure pins
    sensor_dht = DHT11(Pin(4))
    sensor_csms = ADC(Pin(34))
    try:
        sensor_light = BH1750(I2C(1,scl=Pin(22),sda=Pin(21)))
        sensor_light.on()
    except Exception as e:
        print('Light sensor not detected!')
        sensor_light = False

    # initialize mqtt client
    c = MQTTClient(mqtt_config['client_id'], mqtt_config['server'], port=mqtt_config['port'])
    c.connect()

except Exception as e:
    print("Error ocurred in initialization: " + str(e))
    time.sleep_ms(5000)
    reset()
    
time.sleep_ms(1000)

error_counter = 0
loop = True
while loop:
    try:
        # get data
        sensor_dht.measure()
        temperature = sensor_dht.temperature()
        humidity_air = sensor_dht.humidity()
        humidity_ground = sensor_csms.read_u16()
        if sensor_light != False:
            light = sensor_light.luminance(BH1750.ONCE_HIRES_2)
        
        # publish data
        c.publish(mqtt_config['topic_temperature'], str(temperature))
        c.publish(mqtt_config['topic_humidity_air'], str(humidity_air))
        c.publish(mqtt_config['topic_humidity_ground'], str(humidity_ground))
        if sensor_light != False:
            c.publish(mqtt_config['topic_light'], str(light))

        # sleep
        time.sleep_ms(app_config['sleep-ms'])
    
    except KeyboardInterrupt:
        print("Stopped!")
        loop = False

    except Exception as e:
        print("Error ocurred in loop: " + str(e))
        time.sleep_ms(1000)
        error_counter = error_counter + 1
        if error_counter > app_config['max-error']:
            reset()