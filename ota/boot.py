#-----------
#bibliotecas
#-----------
import esp
esp.osdebug(None)
#essa classe garante que toda memoria em desuso vai ser liberada
import gc


import network
from machine import reset
from time import sleep, localtime
from util import open_json


gc.collect() 

#-------------------
#Conectar com o wifi
#-------------------

#Coleta das de dados variaveis
survey_data = open_json()
ssid = survey_data['ssid']
password = survey_data['pwd']
device_id = survey_data['device_id']

#sistema que vai conectar a EPS ao wifi determnado em vars
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
sleep(5)


#Caso de tudo certo vai conectar e notificar
if station.isconnected() == True:
    print('Conectado com Sucesso ')
    print(station.ifconfig())
    print('Device ID', device_id, str(localtime()))

#---
#OTA
#---

# Usamos o protocolo OTA para atualizar nosso sistema remotamente, basta redefinir os dados presentes abaixo e n閼肩幈 mexer nunca no senko.py
from senko import Senko
OTA = Senko(user="Badprofusion", repo="nutritec", working_dir="ota", files=["boot.py", "main.py", "util.py"])
#OTA = Senko(user="rafaelbhcosta", repo="nutri_ota", working_dir="ota", files=["boot.py", "main.py"])

try:
    if OTA.update():
        import machine
        print("Updated to the latest version! Rebooting...")
        sleep(10)
        reset()
except Exception as e:
    print(e)
    print('Sem Att no momento')
    None
