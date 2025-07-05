import serial
import time
import json
import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime

# === CONFIGURATION ===
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 9600
THINGSBOARD_ADDR = "192.168.112.131"
PORT = 1883
ACCESS_TOKEN = "YOUR_THINGSBOARD_ACCESS_TOKEN"

DB_CONFIG = {
    'host': 'localhost',
    'user': 'pi',
    'password': '',
    'database': 'assignment3'
}

# === INIT SERIAL, MQTT, DB ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_ADDR, PORT, 60)
client.loop_start()

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

def insert_into_db(table, value):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = f"INSERT INTO {table} (value, timestamp) VALUES (%s, %s)"
    cursor.execute(sql, (value, now))
    db.commit()

def analyze_and_publish(data):
    try:
        soil_raw, temp, light_raw, rain_raw, water_raw = map(float, data.strip().split(','))

        # Soil Moisture
        soil_percent = round((1023 - soil_raw) / 1023 * 100)
        insert_into_db('soil_moisture', soil_percent)

        # Temperature
        temp_c = round(temp, 2)
        insert_into_db('temperature', temp_c)

        # Sunlight Intensity
        sunlight_status = "Sunny" if light_raw < 400 else "Cloudy"
        insert_into_db('sunlight', sunlight_status)

        # Rain Intensity
        if rain_raw < 100:
            rain_status = "Heavy rain"
        elif rain_raw < 300:
            rain_status = "Slight rain"
        else:
            rain_status = "No rain"
        insert_into_db('rain', rain_status)

        # Water Level Condition
        if water_raw < 200:
            water_status = "Flooded"
        elif water_raw < 500:
            water_status = "High"
        else:
            water_status = "OK"
        insert_into_db('water_level', water_status)

        # Publish to MQTT
        payload = {
            "soil_moisture": soil_percent,
            "temperature": temp_c,
            "sunlight": sunlight_status,
            "rain": rain_status,
            "water_level": water_status
        }
        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"Published: {payload}")

    except Exception as e:
        print(f"Error processing data: {e}")

# === LOOP ===
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
    print("Shutting down gracefully...")
finally:
    ser.close()
    client.loop_stop()
    client.disconnect()
    cursor.close()
    db.close()