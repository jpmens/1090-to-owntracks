#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import requests
import json
import time
import argparse
import sys
import ssl

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2016 Jan-Piet Mens'
__license__   = """GPL2"""

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--url', 
                help='URL of feed (e.g. http://localhost/data/aircraft.json)', 
                dest='url', 
                default="http://localhost:8080/data/aircraft.json") 
        parser.add_argument('--mqtthost', 
                help='MQTT host (e.g. test.mosquitto.org)', 
                dest='mqtthost', 
                default="test.mosquitto.org") 
        parser.add_argument('--mqttport', 
                help='MQTT port (e.g. 1883)', 
                dest='mqttport', 
                default=1883) 
        parser.add_argument('--topic',
                help='MQTT topic (e.g. ot/flights)',
                dest='topic',
                default="ot/flights")
        parser.add_argument('--awsiot',
                action='store_true',
                help='Send to AWS IOT')
        parser.add_argument('--awshost',
                help='AWS host (e.g. data.iot.us-east-1.amazonaws.com)',
                dest='awshost',
                default="data.iot.us-east-1.amazonaws.com")
        parser.add_argument('--awsdir',
                help="AWS credentials directory (e.g $HOME/.aws/iot)",
                dest='awsdir')

        args = parser.parse_args()

    except IOError as e:
        print(e)
        sys.exit(1)


def get_aircraft():
    url = args.url
    overhead = []

    r = requests.get(url)
    try:
        data = json.loads(r.text)
    except:
        return overhead

    if 'aircraft' in data:
        for craft in data['aircraft']:
        # {"hex":"4b9064","squawk":"3257","flight":"PGT6FT  ","lat":51.883633,"lon":8.310699,"nucp":7,"seen_pos":2.6,"altitude":35975,"vert_rate":0,"track":277,"speed":393,"category":"A0","messages":123,"seen":1.3,"rssi":-34.3}

            if 'flight' in craft and 'lat' in craft:
                plane = {
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
                    }
                if 'squawk' in craft:
                    plane['squawk']     = craft.get('squawk')
                overhead.append(plane)

    return overhead

if args.awsiot:
    awsport = 8883
    # clientId = "myThingName"
    # thingName = "myThingName"
    caPath = "%s/aws-iot-rootCA.crt" % args.awsdir
    certPath = "%s/cert.pem" % args.awsdir
    keyPath = "%s/privatekey.pem" % args.awsdir

    mqttc = paho.Client()
    mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

    mqttc.connect(args.awshost, awsport, 60)
    mqttc.loop_start()
else:
    mqttc = paho.Client(client_id=None, clean_session=True, userdata=None, protocol=paho.MQTTv311)
    mqttc.connect(args.mqtthost, args.mqttport, 60)
    mqttc.loop_start()

while True:
    overhead = get_aircraft()
    for aircraft in overhead:
        topic = '%s/%s' % ( args.topic, aircraft['flight'] )

        aircraft['_geoprec']    = 2

        payload = json.dumps(aircraft)
        mqttc.publish(topic, payload, qos=1, retain=False)


    time.sleep(10)

