from flask import Flask, render_template, request, jsonify
import pymysql
import paho.mqtt.publish as publish
from datetime import datetime
import serial
import time

app = Flask(__name__)

# # MQTT Setup
# MQTT_BROKER = "thingsboard.cloud"
# ACCESS_TOKEN = "YOUR_THINGSBOARD_ACCESS_TOKEN"
# Connect to Arduino
arduino = serial.Serial('/dev/ttyS0', 9600, timeout=1)
time.sleep(2)

# Database Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'pi',
    'password': '',
    'database': 'assignment3'
}
    


# API

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fan', methods=['POST'])
def control_fan():
    action = request.json.get('action') + '\n'
    # payload = {"fan": action}
    # publish.single("v1/devices/me/telemetry", payload=str(payload), hostname=MQTT_BROKER, auth={'username': ACCESS_TOKEN})
    arduino.write(action.encode())  # Send fan command

    return jsonify({"status": "sent", "action": action})

@app.route('/api/search', methods=['GET'])
def search_data():
    table = request.args.get('parameter')
    start = request.args.get('start')
    end = request.args.get('end')

    try:
        database = pymysql.connect(**DB_CONFIG)
        cursor = database.cursor()
        query = f"""
            SELECT value, timestamp 
            FROM {table}
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (start, end))
        results = cursor.fetchall()
        data = [{"value": row[0], "timestamp": row[1].strftime("%Y-%m-%d %H:%M:%S")} for row in results]
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        database.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)