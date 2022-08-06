#-----------
#bibliotecas
#-----------
import esp
esp.osdebug(None)
#essa classe garante que toda memoria em desuso vai ser liberada
import gc
gc.collect() 
import network
import time
from util import open_json, web_register_uix
import _thread

#-------------------
#Conectar com o wifi
#-------------------

#Coleta das de dados variaveis
survey_data = open_json()
ssid = survey_data['ssid']
password = survey_data['pwd']

#sistema que vai conectar a EPS ao wifi determnado em vars
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
time.sleep(5)

#reset
def resetboot():
    try:
        while True:
            time.sleep(60)
            print('Reiniciando após 60 segundos')
            machine.reset()
    except Exception as e:
        print(e)


#Caso de tudo certo vai conectar e notificar
if station.isconnected() == True:
    print('Conectado com Sucesso ')
    print(station.ifconfig())
#Se der errado ela vai gerar uma rede propria, nessa rede vai ser possivel atualizar qualquer dado
else:
    ap = network.WLAN(network.AP_IF)     
    ap.active(True)                      
    ap.config(essid='lilygo-BlueShift',password=b"Be@Loved", channel=11, authmode=network.AUTH_WPA_WPA2_PSK)
    print('Falha ao se conectar\nAcesse a Rede IP e reconfigure a nova rede')
    ap.ifconfig(('192.168.15.6', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
    print('http://192.168.15.6')
    _thread.start_new_thread(resetboot, ())
    web_register_uix()
    #Sitema que ativa a pagina web para atualizar os dados

#---
#OTA
#---

# Usamos o protocolo OTA para atualizar nosso sistema remotamente, basta redefinir os dados presentes abaixo e n閼肩幈 mexer nunca no senko.py
from senko import Senko
OTA = Senko(user="Badprofusion", repo="nutritec", working_dir="ota2", files=["boot.py", "vars.json", "main.py", "util.py"])

try:
    if OTA.update():
        import machine
        print("Updated to the latest version! Rebooting...")
        time.sleep(10)
        machine.reset()
except Exception as e:
    print(e)
    print('Sem Att no momento')
    None

