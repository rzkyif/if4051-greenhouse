from config import wifi_config
import network
import utime
import ntptime

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    start = utime.time()
    timed_out = False

    print('Connecting to WIFI...')

    sta_if.active(True)
    sta_if.connect(wifi_config["ssid"], wifi_config["password"])

    while not sta_if.isconnected() and not timed_out:        
        if utime.time() - start >= 20:
            timed_out = True
        else:
            pass

    if sta_if.isconnected():
        ntptime.settime()
        print('Connected!')
        print('Network config:', sta_if.ifconfig())
    else: 
        print('WIFI connection failed! Restart the device!')

do_connect()