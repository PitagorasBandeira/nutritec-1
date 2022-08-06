import machine
from machine import I2C, Pin
from util import create_mqtt_client, get_telemetry_topic, get_c2d_topic, parse_connection, open_json, sensor_get_values
import utime
import json
import gc
import time
import senko

gc.collect()
gc.enable()


survey_data = open_json()
username = survey_data['hostname'] + '/' + survey_data['device_id']
### Create UMQTT ROBUST or UMQTT SIMPLE CLIENT
mqtt_client = create_mqtt_client(client_id=survey_data['device_id'], hostname=survey_data['hostname'], username=username, password=survey_data['sas_token_str'].replace("_"," "), port=8883, keepalive=60, ssl=True)

def callback_handler(topic, message_receive):
    global message_received
    message_received = message_receive
    #print("Received message")
    #print(message_receive)


#collect from topic
def pub_sub():
    try:
        while True:
            print("Iniciando Thread")
            try:
                mqtt_client.reconnect()
                print("Mqtt Conectado")                  
                #if datadataset_dec_rep_j['act'] == "getdata":
                data = sensor_get_values()
                topic = get_telemetry_topic(survey_data['device_id'])
                mqtt_client.publish(topic=topic, msg=str(data))
                #else: print("")
                mqtt_client.disconnect()
                utime.sleep(60)
            except Exception as e:
                print(e)
                #mqtt_client.check_msg()
                mqtt_client.disconnect()
                utime.sleep(60)
    except Exception as e: 
        print("Sub function error: ", e)
        mqtt_client.disconnect()
        
  
while True:
    pub_sub()
#_thread.start_new_thread(pub, ())
#_thread.start_new_thread(sub, ())
#web_register_uix()
