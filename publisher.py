import serial
import time
import json
import paho.mqtt.client as mqtt
import pymysql
from datetime import datetime

# Configuration
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 9600
THINGSBOARD_ADDR = "192.168.112.131"
PORT = 1883
ACCESS_TOKEN = "zgrbpj5lm4bprcclwm2f"

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_ADDR, PORT, 60)
client.loop_start()

# Initialize database connection
database = pymysql.connect(
    host="localhost",
    user="pi",
    password="",
    database="assignment3"
)
cursor = database.cursor()

def insert_into_database(table, value):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = f"INSERT INTO {table} (value, timestamp) VALUES (%s, %s)"
    cursor.execute(query, (value, now))
    database.commit()

def analyze_and_publish(data):
    try:
        soil_value, temp, light_value, rain_value, water_value = map(float, data.strip().split(','))

        # Soil Moisture
        soil_percent = round((1023 - soil_value) / 1023 * 100)
        insert_into_database('soil_moisture', soil_percent)

        # Temperature
        temp = round(temp, 2)
        insert_into_database('temperature', temp)

        # Sunlight Intensity
        sunlight_status = "Sunny" if light_value < 400 else "Cloudy"
        insert_into_database('sunlight', sunlight_status)

        # Rain Intensity
        if rain_value < 400:
            rain_status = "Heavy rain"
        elif rain_value < 800:
            rain_status = "Slight rain"
        else:
            rain_status = "No rain"
        insert_into_database('rain', rain_status)

        # Water Level
        if water_value > 600:
            water_status = "Flooded"
        elif water_value > 500:
            water_status = "High"
        else:
            water_status = "OK"
        insert_into_database('water_level', water_status)

        # Publish
        payload = {
            "soil_moisture": soil_percent,
            "temperature": temp,
            "sunlight": sunlight_status,
            "rain": rain_status,
            "water_level": water_status
        }
        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"Published: {payload}")

    except Exception as e:
        print(f"Error processing data: {e}")

# Loop
try:
    print("Edge device is running...")
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Received: {line}")
                analyze_and_publish(line)
        time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down ...")
finally:
    ser.close()
    client.loop_stop()
    client.disconnect()
    cursor.close()
    database.close()