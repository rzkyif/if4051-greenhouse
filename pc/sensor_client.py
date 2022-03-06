import paho.mqtt.client as mqtt
import os

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("if4051-5-temperature")
    client.subscribe("if4051-5-humidity-ground")
    client.subscribe("if4051-5-humidity-air")
    client.subscribe("if4051-5-light")

def on_message(client, userdata, msg):
    print(f"Received '{msg.topic[9:]}' sensor data: '{msg.payload.decode('utf-8')}'")

def next_path(path_pattern):
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)
    return path_pattern % b

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()