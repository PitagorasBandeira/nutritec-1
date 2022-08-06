from robust import MQTTClient
import re #regex para coletar os valores do form
import json
from machine import ADC, Pin, I2C, reset
from random import uniform
from time import sleep, time

try:
  import usocket as socket
except:
  import socket

#Funcoes para integarir via mqtt com o iothub
def create_mqtt_client(client_id, hostname, username, password, port=8883, keepalive=120, ssl=True):
    if not keepalive:
        keepalive = 120
    if not ssl:
        ssl = True
    c = MQTTClient(client_id=client_id, server=hostname, port=8883, user=username, password=password, keepalive=120, ssl=True)
    c.DEBUG = True
    return c


def get_telemetry_topic(device_id):
    return get_topic_base(device_id) + "/messages/events/"
    
def get_c2d_topic(device_id):
     return get_topic_base(device_id) + "/messages/devicebound/#"

def get_topic_base(device_id, module_id=None):
    if module_id:
        base_str = "devices/" + device_id + "/modules/" + module_id
    else:
        base_str = "devices/" + device_id
    return base_str

DELIMITER = ";"
VALUE_SEPARATOR = "="

def parse_connection(connection_string):
    cs_args = connection_string.split(DELIMITER)
    dictionary = dict(arg.split(VALUE_SEPARATOR, 1) for arg in cs_args)
    return dictionary


def save_json(dictValues):
    with open('vars.json', 'w') as sj: 
        json.dump(dictValues, sj)
    sj.close()
    print("Arquivo salvo!. Reiniciando")
    sleep(1)
    reset()

def open_json():
    with open('vars.json', 'r') as rj:
        survey_data = json.load(rj)
        survey_data['sas_token_str'] = survey_data['sas_token_str'].replace(" ","_")
    rj.close()
    return survey_data



##############################################
#Projeto das plantas

#BOMBA1
bomba1 = Pin(16, Pin.OUT)

#BOMBA2
bomba2 = Pin(17, Pin.OUT)
#bomba2.value(not bomba1.value())

#LED
fitaled1 = Pin(5, Pin.OUT)
#fitaled1.value(not fitaled1.value())

#BOIA1
boia1 = Pin(4, Pin.IN, Pin.PULL_UP)

#BOIA2
boia2 = Pin(15, Pin.IN, Pin.PULL_UP)

#v1
lux_param = 0
temp = 0.0
humid = 0.0
lux = 0.0
soil = 0.0
ph = 0.0
seg_bomba1 = 0
seg_bomba1end = 0
bomba1_val = 0
seg_bomba2 = 0
seg_bomba2end = 0
bomba2_val = 0
watts = 0.0
seg_watts = 0
seg_water = 0
total_water_seg_t = 0

def ph():
  x = uniform(7.0, 8.9)
  return float(x)

seg_watts = time()

def watts():
  watts = ((0.25 * 5) * ((time() - seg_watts)))/3600
  return float(watts)

def water():
  total_water_seg = 0
  total_water_seg = ((seg_bomba1 - seg_bomba1end) * 0.025) + ((seg_bomba2 - seg_bomba2end) * 0.025)
  total_water_seg_t = total_water_seg
  return float(total_water_seg_t)

def bomba1_on():
  print("bomba1_on")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(1)
  return bomba1.value()
  
def bomba1_off():
  print("bomba1_off")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(0)
  return bomba1.value()

def bomba2_on():
  print("bomba2_on")
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(1)
  return bomba2.value()

def bomba2_off():
  print("bomba2_off")
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(0)
  return bomba2.value()

def reles_on():
  print("reles_on")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(1)
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(1)
  fitaled1 = Pin(5, Pin.OUT)
  fitaled1.value(1)

def reles_off():
  print("reles_off")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(0)
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(0)
  fitaled1 = Pin(5, Pin.OUT)
  fitaled1.value(0)

def fitaled_on():
  print("fitaled_on")
  fitaled = Pin(5, Pin.OUT)
  fitaled.value(1)
  return fitaled.value()

def fitaled_off():
  print("fitaled_off")
  fitaled = Pin(5, Pin.OUT)
  fitaled.value(0)
  return fitaled.value()

def sensor_get_values():
  bomba1 = Pin(16, Pin.OUT)
  bomba2 = Pin(17, Pin.OUT)
  fitaled1 = Pin(5, Pin.OUT)
  boia1 = Pin(4, Pin.IN, Pin.PULL_UP)
  boia2 = Pin(15, Pin.IN, Pin.PULL_UP)
  #print('Sensors started')
  moisture2 = Pin(34, Pin.IN)     # create input pin on GPIO2
  moisture2_value = moisture2.value()
  rain = Pin(35, Pin.IN)     # create input pin on GPIO2
  rain_value = "Raining"
  boia1_value = "Water level full"
  boia2_value = "Water level full"
  if rain.value() == 1: rain_value = "Not raining"
  if boia1.value() == 0: boia1_value = "Water level critic"
  if boia2.value() == 0: boia2_value = "Water level critic"
  msg = {}
  msgfull = {}
  msg["sensorname"] = "BITPLANT"
  msg["sensortype"] = "mixed sensors"
  msg["version"] = " * v2"
  msg["humid_limit"] = float(moisture2_value)
  #msg["humid"] = float(humid)
  #msg["temp"] = float(temp)
  #msg["lux"] = float(lux)
  #msg["soil"] = float(soil)
  msg["rain"] = rain_value
  msg["float1"] = boia1_value
  msg["float2"] = boia2_value
  msg["ph"] = ph()
  msg["bomba1"] = bomba1.value()
  msg["bomba2"] = bomba2.value()
  msg["led"] = fitaled1.value()
  msg["watts_spend"] = watts()
  msg["water_spend"] = float(total_water_seg_t)
  msg["time"] = time()
  return json.dumps(msg)

