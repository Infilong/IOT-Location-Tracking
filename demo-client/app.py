from flask import Flask, render_template, request, redirect, url_for
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, emit
import pandas as pd

df = pd.DataFrame(columns=['Line', 'Timestamp', 'Latitude', 'Longitude', 'csq'])

app = Flask(__name__, template_folder='templates')

# If your broker has enabled user authentication, you can input your Username and Password information into the configuration item.
# https://mqttx.app/docs/get-started#client-related-information

app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password

app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True
app.topic = "default"

mqtt_client = Mqtt(app)
socketio = SocketIO(app)  # Initialize SocketIO with the app

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(app.topic)
   else:
       print('Bad connection. Code:', rc)

@mqtt_client.on_message()  
def handle_mqtt_message(client, userdata, message):
  print("Received MQTT message:", message.payload)
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
        csq = int(csq_data)
        csq_with_description = ""
        if csq <= 10:
          csq_with_description = "{:2d}(Signal Weak)".format(csq)

        elif csq > 10 and csq <= 20:
          csq_with_description = "{:2d}(Signal Medium)".format(csq)
          
        else:
          csq_with_description = "{:2d}(Signal Strong)".format(csq)

  timestamp_now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
  df.loc[len(df.index)] = [len(df.index), timestamp_now, latitude, longitude, csq_with_description]
  
  # Every time the 'new_data' event is emitted and received by the client-side JavaScript(loading.js), 
  # the page will be redirected back to /topic, causing the template to be re-rendered with the updated GNSS data, 
  # providing real-time updates to the user.
  socketio.emit('new_data', df.to_dict(orient='records'))
  print("EMITING DATA")

@app.route('/topic')
def user_topic():
  print(df)
  # Pass the list of dictionaries to template topic.html
  table_data = df.to_dict(orient='records')
  return render_template('topic.html', tables=[table_data])  

@app.route('/subscribe', methods=['GET', 'POST'])
def subscription():
  if request.method == 'POST':
    mqtt_client.unsubscribe(app.topic)
    print("Unsubscribe old topic!")

    # Debug: Print the form data
    print(request.form)

    # Extract MQTT broker URL and port
    broker_url = request.form['mqtt-broker-url']
    broker_port = int(request.form['mqtt-broker-port'])
    app.topic = "/gnss/" + request.form['topic'] + "/up/nmea"
    
    # Debug: Print the extracted values
    print("MQTT Broker URL:", broker_url)
    print("MQTT Broker Port:", broker_port)
    print("topic:" + app.topic)

    # Initialize and start the MQTT client
    mqtt_client.init_app(app)
    mqtt_client.client.connect(host=broker_url,port=broker_port)

    mqtt_client.subscribe(app.topic)
    print("Subscribed new topic!")
    
    # Check if df is empty
    if df.empty:
        return redirect(url_for('loading_page'))
  
    return redirect(url_for('user_topic'))
  else:
    return render_template('subscribe.html')

@app.route('/loading')
def loading_page():
    return render_template('loading.html')

# The event name 'connect' is predefined by SocketIO itself.
@socketio.on('connect')
def on_connect():
    print('Client connected')

if __name__ == '__main__': 
   app.run(host='127.0.0.1', port=5000)
