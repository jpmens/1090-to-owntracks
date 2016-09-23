#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import requests
import json
import time

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2016 Jan-Piet Mens'
__license__   = """GPL2"""

def get_aircraft():
    url = 'http://localhost:8080/data/aircraft.json'
    overhead = []

    r = requests.get(url)
    data = json.loads(r.text)

    if 'aircraft' in data:
        for craft in data['aircraft']:
        # {"hex":"4b9064","squawk":"3257","flight":"PGT6FT  ","lat":51.883633,"lon":8.310699,"nucp":7,"seen_pos":2.6,"altitude":35975,"vert_rate":0,"track":277,"speed":393,"category":"A0","messages":123,"seen":1.3,"rssi":-34.3}

            if 'flight' in craft and 'lat' in craft:
                overhead.append({
                        "_type"     : 'location',
                        "tst"       : int(time.time()),
                        "flight"    : craft['flight'].rstrip(),
                        "lat"       : craft['lat'],
                        "lon"       : craft['lon'],
                        "vel"       : int(craft.get('speed', 0) * 1.852),
                        "cog"       : craft.get('track', 0),
                        "alt"       : int(craft.get('altitude', 0) / 3.2808),
                        "roc"       : int(craft.get('vert_rate', 0) / 3.2808 / 60), # rate of climb m/s
                        "name"      : craft['flight'].rstrip(),
                    })

    return overhead

mqttc = paho.Client(client_id=None, clean_session=True, userdata=None, protocol=paho.MQTTv311)
mqttc.connect("test.mosquitto.org", 1883, 60)
mqttc.loop_start()

while True:
    overhead = get_aircraft()
    for aircraft in overhead:
        topic = 'ot/flights/%s' % aircraft['flight']

        aircraft['_geoprec']    = 2

        payload = json.dumps(aircraft)
        mqttc.publish(topic, payload, qos=1, retain=False)


    time.sleep(10)

