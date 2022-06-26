from robust import MQTTClient
import re #regex para coletar os valores do form
import json
from machine import ADC, Pin, I2C
import machine
import random
from time import sleep
import time
import utime


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


#Funcoes para interface web
def formValues(request):
  dictFields = {}
  try:
    listFields = ['hostname','device_id','sas_token_str','username','ssid','pwd']
    for fields in listFields: 
      dictFields[fields]=re.search(r''+fields+'=(.*?)&', request).group(1)
  except: pass
  return dictFields

def web_page(led):
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"

  survey_data = open_json()

  html = """<html><head><h1 style="text-align: center;">BlueShift IoT <img src="https://html-online.com/editor/tiny4_9_11/plugins/emoticons/img/smiley-tongue-out.gif" alt="tongue-out" /></h1>
  <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}h1{color: #0F3376; padding: 2vh;}p{font-size: 1.0rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;border-radius: 4px; color: white; padding: 8px 13; text-decoration: none; font-size: 10px; margin: 2px; cursor: pointer;}.button2{background-color: #4286f4; padding:5px 10px;}</style></head>
  <body><p style="text-align: center;">GPIO state: <strong>""" + gpio_state + """</strong></p><p style="text-align: center;"><a href="/?led=on"><button class="button">ON</button></a> &nbsp; <a href="/?led=off"><button class="button button2">OFF</button></a></p>
  <form action="" method="get" name="search">
  <p style="text-align: center;">hostname: <input name="hostname" value="""+ survey_data['hostname'] +""" type="text" /></p>
  <p style="text-align: center;">device_id: <input name="device_id" value="""+ survey_data['device_id'] +""" type="text" /></p>
  <p style="text-align: center;">sas_token_str: <input name="sas_token_str" value="""+ survey_data['sas_token_str'] +""" type="text" /></p>
  <p style="text-align: center;">username: <input name="username" /></p>
  <p style="text-align: center;">ssid: <input name="ssid" value="""+ survey_data['ssid'] +""" type="text" /></p>
  <p style="text-align: center;">pwd: <input name="pwd" value="""+ survey_data['pwd'] +""" type="text" /></p>
  <p style="text-align: center;">null: <input name="null" value="" type="text" /></p>
  <p style="text-align: center;"><input type="submit" value="Submit" /></p>
  </form></body></html>"""
  return html

def save_json(dictValues):
    with open('vars.json', 'w') as sj: 
        json.dump(dictValues, sj)
    sj.close()
    print("Arquivo salvo!. Reiniciando")
    utime.sleep(1)
    machine.reset()

def open_json():
    with open('vars.json', 'r') as rj:
        survey_data = json.load(rj)
        survey_data['sas_token_str'] = survey_data['sas_token_str'].replace(" ","_")
    rj.close()
    return survey_data

#Funcoes para quando o usuario nao esta com os dados preenchidos.
def web_register_uix():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('', 80))
  s.listen(5)
  led = Pin(2, Pin.OUT)
  while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    global request
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on == 6:
      print('LED ON')
      led.value(1)
    if led_off == 6:
      print('LED OFF')
      led.value(0)
    response = web_page(led)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
    global dictValues
    dictValues = formValues(request)
    if dictValues != {}:
      dictValues['sas_token_str'] = dictValues['sas_token_str'].replace("+"," ").replace("%3D","=").replace("%252F","%2F").replace("%26","&").replace("%253D","%3D")
      save_json(dictValues)




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

last_message_bomba = 0
last_message = 0
message_interval_bomba = 5
message_interval = 30
counter = 0


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
  x = random.uniform(7.0, 8.9)
  return float(x)

seg_watts = time.time()

def watts():
  watts = ((0.25 * 5) * ((time.time() - seg_watts)))/3600
  return float(watts)

def water():
  total_water_seg = 0
  total_water_seg = ((seg_bomba1 - seg_bomba1end) * 0.025) + ((seg_bomba2 - seg_bomba2end) * 0.025)
  total_water_seg_t = total_water_seg
  return float(total_water_seg_t)

def bomba1():
  print("bomba1")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(not bomba1.value())
  seg_bomba1 = time.time()
  bomba1_val = 1
  water()

def bomba2():
  print("bomba2")
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(not bomba2.value())
  seg_bomba2 = time.time()
  bomba2_val = 1
  water()

def reles():
  print("reles")
  bomba1 = Pin(16, Pin.OUT)
  bomba1.value(not bomba1.value())
  bomba2 = Pin(17, Pin.OUT)
  bomba2.value(not bomba2.value())
  fitaled1 = Pin(5, Pin.OUT)
  fitaled1.value(not fitaled1.value())

def sensor_get_values():
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
  msg["sensorname"] = "esp32_nplant"
  msg["sensortype"] = "mixed sensors"
  msg["humid_limit"] = float(moisture2_value)
  msg["humid"] = float(humid)
  msg["temp"] = float(temp)
  msg["lux"] = float(lux)
  msg["soil"] = float(soil)
  msg["rain"] = rain_value
  msg["float1"] = boia1_value
  msg["float2"] = boia2_value
  msg["ph"] = ph()
  msg["watts_spend"] = watts()
  msg["water_spend"] = float(total_water_seg_t)
  msg["time"] = time.time()
  return json.dumps(msg)








