from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import pandas as pd

df = pd.DataFrame(columns=['Timestamp', 'Latitude', 'Longitude', 'csq'])
# df.loc[0] = [pd.Timestamp.now(), 'Sample data']

app = Flask(__name__, template_folder='templates')

app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883

# If your broker has enabled user authentication, you can input your Username and Password information into the configuration item.
# https://mqttx.app/docs/get-started#client-related-information
app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password

app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True
app.topic = "/gnss/864269067627410/up/nmea"

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(app.topic)
   else:
       print('Bad connection. Code:', rc)

@mqtt_client.on_message()  
def handle_mqtt_message(client, userdata, message):
  latitude = None
  longitude = None
  csq = None
  sentences = message.payload.decode().split("\r\n")
  
  if len(sentences) == 0:
    print("No message")
  else:
    for sentence in sentences:
      sentence = sentence.split(",")    
    
      if sentence[0] == "$GNRMC":
        lat = sentence[3]
        lon = sentence[5]
        if lat and lon: 
          latitude = float(lat)
          longitude = float(lon)
      if sentence[0].startswith("$csq"):
        csq_data = sentence[0]
        csq_data = csq_data[4:]
        print("csq_data: " + csq_data)
        csq = int(csq_data)

  timestamp_now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
  df.loc[len(df.index)] = [timestamp_now, latitude, longitude, csq]
  
@app.route('/')
def index():
  titles = ['Timestamp', 'Latitude', 'Longitude', 'rsrp']
  html = df.to_html(classes='data')  
  return render_template('index.html', tables=[html], titles=titles)

if __name__ == '__main__': 
   app.run(host='127.0.0.1', port=5000)


