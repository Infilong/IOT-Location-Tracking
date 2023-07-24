from flask import Flask, render_template
from flask_mqtt import Mqtt
import pandas as pd

df = pd.DataFrame(columns=['Timestamp', 'Latitude', 'Longitude', 'rsrp'])
# df.loc[0] = [pd.Timestamp.now(), 'Sample data']

app = Flask(__name__, template_folder='templates')

app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True
topic = '/gnss/864269067627410/up/nmea'

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()  
def handle_mqtt_message(client, userdata, message):
  latitude = None
  longitude = None
  rsrp = None
  sentences = message.payload.decode().split("\r\n")
  
  for sentence in sentences:
    sentence = sentence.split(",")    
    
    if sentence[0] == "$GNRMC":
      lat = sentence[3]
      lon = sentence[5]
      if lat and lon: 
        latitude = float(lat)
        longitude = float(lon)
    if sentence[0].startswith("$rsrp"):
      rsrp_data = sentence[0]
      rsrp_data = rsrp_data[5:]
      print("rsrp_data: " + rsrp_data)
      rsrp = int(rsrp_data)
  
  print("the whole data")
  print(latitude, longitude, rsrp)
  df.loc[len(df.index)] = [pd.Timestamp.now(), latitude, longitude, rsrp]
  
@app.route('/')
def index():
  titles = ['Timestamp', 'Latitude', 'Longitude', 'rsrp']
  html = df.to_html(classes='data')  
  return render_template('index.html', tables=[html], titles=titles)

# @app.route('/')  
# def index():
#   html = df.to_html(classes='data')
  
#   return """
#   <html>
#     <body>
#       <h1>Sensor Data</h1>
#       {html}
#     </body>
#   </html>
#   """.format(html=html)

if __name__ == '__main__':
   app.run(host='127.0.0.1', port=5000)

