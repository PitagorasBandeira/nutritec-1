
from util import create_mqtt_client, get_telemetry_topic, get_c2d_topic, parse_connection, open_json, sensor_get_values, reles_on, reles_off, bomba1_on,bomba1_off, bomba2_on, bomba2_off, fitaled_on, fitaled_off
from time import sleep
import json
import gc
import senko
from machine import reset

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
 
def reset_mac():
  print("Reiniciando a pedido")
  reset()
  

#collect from topic
def pub_sub():
    global datadataset_dec_rep_j
    try:
        while True:
            print("Listening - ", str(localtime()))
            mqtt_client.reconnect()
            subscribe_topic = get_c2d_topic(survey_data['device_id'])
            mqtt_client.set_callback(callback_handler)
            mqtt_client.subscribe(topic=subscribe_topic)
            if True:
                mqtt_client.wait_msg()
                dataset = message_received
                dataset_dec = dataset.decode("utf-8")
                dataset_dec_rep = dataset_dec.replace("'","\"")
                datadataset_dec_rep_j = set = json.loads(dataset_dec_rep)
                try:
                    if datadataset_dec_rep_j['act'] == 'bomba1_off': 
                        bomba1_off()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                    elif datadataset_dec_rep_j['act'] == 'bomba1_on': 
                        bomba1_on()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                        sleep(60)
                        bomba1_off()
                    elif datadataset_dec_rep_j['act'] == 'bomba2_off': 
                        bomba2_off()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                    elif datadataset_dec_rep_j['act'] == 'bomba2_on': 
                        bomba2_on()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                        sleep(60)
                        bomba2_off()
                    elif datadataset_dec_rep_j['act'] == "reset": reset_mac()
                    elif datadataset_dec_rep_j['act'] == 'fitaled_off': 
                        fitaled_off()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data) 
                    elif datadataset_dec_rep_j['act'] == 'fitaled_on': 
                        fitaled_on() 
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)                     
                    elif datadataset_dec_rep_j['act'] == 'reles_off': 
                        reles_off()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                    elif datadataset_dec_rep_j['act'] == 'reles_on': 
                        reles_on()
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)                   
                    elif datadataset_dec_rep_j['act'] == "keepa": print("keepa")
                    elif datadataset_dec_rep_j['act'] == "getdata": 
                        data = sensor_get_values()
                        topic = get_telemetry_topic(survey_data['device_id'])
                        mqtt_client.publish(topic=topic, msg=data)
                    else: print("")
                except: 
                    print("erro - payload enviado: ",datadataset_dec_rep_j)
            else:
                mqtt_client.check_msg()
                sleep(1)
            mqtt_client.disconnect()
    except Exception as e: 
        print("Sub function error: ", e)
        mqtt_client.disconnect()


while True:
  pub_sub()

