# 1090-to-owntracks

This small program slurps the data from `aircraft.json` as produced by [tedsluis/dump1090](https://github.com/tedsluis/dump1090) which is a Mode S decoder for RTLSDR devices.

Data is published to the MQTT topic `ot/flights/<flightnumber>` in [OwnTracks-compatible JSON](http://owntracks.org/booklet/tech/json/):

```json
{
  "tst": 1474648272,
  "cog": 134,
  "lon": 6.658383,
  "_type": "location",
  "flight": "KLM1963",
  "roc": 0,
  "lat": 51.381042,
  "_geoprec": 2,
  "alt": 10058,
  "vel": 877,
  "name": "KLM1963"
}
```

## Hardware

* Start [from this](http://blog.wenzlaff.de/?p=4005). If you get stuck, read [this long English page](http://www.satsignal.eu/raspberry-pi/dump1090.html)
* Instead of the dump1090 git repo he recommends, use [tedsluis-dump1090](https://github.com/tedsluis/dump1090)

### My Rpi

I bought [this dongle](https://www.amazon.de/gp/product/B00JQX5HT6/) and simply plugged it in.

```
$ lsusb
Bus 001 Device 004: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T

$ cat /etc/modprobe.d/no-rtl.conf
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830

$ ./dump1090 --interactive --metric --net --net-beast --net-bind-address 0.0.0.0 --write-json /tmp/air/ --json-location-accuracy 2
```
