import uos
import ntptime
import time

from dht import DHT11
from machine import Pin, I2C, ADC, reset
from config import *
from bh1750 import BH1750
from umqtt.simple2 import MQTTClient

PIN_DHT = 4
PIN_CSMS = 32
PIN_LIGHT_SCL = 18
PIN_LIGHT_SDA = 19
PIN_TDS = 33

PIN_HUMIDIFIER = 27
PIN_PUMP = 26

THRESHOLD_AIR_HUMIDITY = 75
THRESHOLD_GROUND_HUMIDITY = 65535

try:
    print("Starting initialization phase...")

    # configure DHT sensor
    try:
        sensor_dht = DHT11(Pin(PIN_DHT))
    except:
        print('DHT sensor not detected!')
        sensor_dht = False

    # configure CSMS sensor
    try:
        sensor_csms = ADC(Pin(PIN_CSMS))
    except:
        print('CSMS sensor not detected!')
        sensor_csms = False


    # configure light sensor
    try:
        sensor_light = BH1750(I2C(1,scl=Pin(PIN_LIGHT_SCL),sda=Pin(PIN_LIGHT_SDA)))
        sensor_light.on()
    except:
        print('Light sensor not detected!')
        sensor_light = False

    # configure TDS sensor
    try:
        sensor_tds = ADC(Pin(PIN_TDS))
    except:
        sensor_tds = False

    # configure actuators
    actuator_humidifier = Pin(PIN_HUMIDIFIER, Pin.OUT, value=1)
    actuator_pump = Pin(PIN_PUMP, Pin.OUT, value=1)

    # initialize mqtt client
    c = MQTTClient(mqtt_config['client_id'], mqtt_config['server'], port=mqtt_config['port'])
    c.connect()

    print("Initialization phase complete!")

except Exception as e:
    print("Error ocurred in initialization: " + str(e))
    time.sleep_ms(5000)
    reset()
    
time.sleep_ms(1000)

print("Starting infinite loop...")
error_counter = 0
loop = True
while loop:
    try:
        # get current time
        current_time = time.gmtime()
        timestamp = f"{current_time[0]}|{current_time[1]}|{current_time[2]}|{current_time[3]}|{current_time[4]}|{current_time[5]}"

        # check DHT sensor
        if sensor_dht != False:
            try:
                # get data
                sensor_dht.measure()
                temperature = sensor_dht.temperature()
                humidity_air = sensor_dht.humidity()
                
                # action
                print(f"humidity_air: {humidity_air}")
                if (humidity_air < THRESHOLD_AIR_HUMIDITY):
                    actuator_humidifier.off()
                else:
                    actuator_humidifier.on()

                # publish
                c.publish(mqtt_config['topic_temperature'], f"{timestamp}|{temperature}")
                c.publish(mqtt_config['topic_humidity_air'], f"{timestamp}|{humidity_air}")

            except Exception as e:
                print(f"DHT sensor failure: {e}")

        # check CSMS sensor
        if sensor_csms != False:
            try:
                # get data
                humidity_ground = sensor_csms.read_u16()

                # action
                print(f"humidity_ground: {humidity_ground}")
                if actuator_pump.value() == 0:
                    actuator_pump.on()
                elif humidity_ground >= THRESHOLD_GROUND_HUMIDITY:
                    actuator_pump.off()

                # publish
                c.publish(mqtt_config['topic_humidity_ground'], f"{timestamp}|{humidity_ground}")

            except Exception as e:
                print(f"DHT sensor failure: {e}")

        # check light sensor
        if sensor_light != False:
            try:
                # get data
                light = sensor_light.luminance(BH1750.ONCE_HIRES_2)

                # publish
                c.publish(mqtt_config['topic_light'], f"{timestamp}|{light}")

            except Exception as e:
                print(f"Light sensor failure: {e}")
        
        # check TDS sensor
        if sensor_tds != False:
            try:
                # get data
                tds = (sensor_tds.read() * 3.3 / 4096)
                tds2 = tds*tds
                tds3 = tds2*tds
                tds = (133.42 * tds3 + 255.86 * tds2 + 857.39 * tds) * 0.5

                # publish
                c.publish(mqtt_config['topic_tds'], f"{timestamp}|{tds}")

            except Exception as e:
                print(f"Light sensor failure: {e}")

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