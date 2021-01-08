#%%
#!/usr/bin/env python
#
# sudo apt-get install libilmbase-dev
# sudo apt-get install libopenexr-dev
# sudo apt-get install libgstreamer1.0-dev
# sudo apt-get install python3-picamera

import os, sys, json, argparse, math
import cv2
import numpy as np
from flask import Flask, request, render_template, Response, jsonify
#from camera_pi import Camera
from camera_opencv import Camera
import serial
import serial.threaded
import time
#from flask_socketio import SocketIO

sys.path.insert(0, os.path.abspath(''))

parser = argparse.ArgumentParser()

parser.add_argument('-debug', action='store_true',help='Debug server')
parser.add_argument('-image_size', type=json.loads, default='[1080, 1920]', help='Training crop size [height, width]/  [90, 160],[120, 160], [144, 176],[288, 352], [240, 432],[480, 640],[576,1024],[720, 960], [720,1280],[1080, 1920]')
parser.add_argument('-image_depth', type=int, default=3, help='Number of input colors.  1 for grayscale, 3 for RGB') 
parser.add_argument('-network_port', type=int, default=5000, help='Network port') 
parser.add_argument('-serial_port', type=str, default='/dev/ttyUSB0', help='Serial port') 

FLAGS, unparsed = parser.parse_known_args()

config = {
      'input_shape': [FLAGS.image_size[0], FLAGS.image_size[1], FLAGS.image_depth],
      'area_filter_min': 250,
      'size_divisible': 32,
      'serial_port': FLAGS.serial_port,
      'network_port': FLAGS.network_port
      }

app = Flask(__name__)
#socketio = SocketIO(app)

global ser
ser = {}

def GetPort(port_name='/dev/ttyUSB0'):
    try:
        port = serial.Serial(port_name)  # open serial port
    except:
        port = None
        print ('serial port {} unavailable'.format(port))
    return port

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""

    while True:
        img = camera.get_frame()
        [height, width, depth] = img.shape

        # encode as a jpeg image and return it
        frame = cv2.imencode('.jpg', img)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/set',methods = ['POST'])
def set():
 
    return jsonify(isError= False,
                   message= "Success",
                   statusCode= 200,
                   data= 0), 200

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(config)), mimetype='multipart/x-mixed-replace; boundary=frame')

class PrintLines(serial.threaded.LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        self.write_line('hello world')

    def handle_line(self, data):
        values = data.split(',')
        # socketio.emit('sensors', {'temperature (C)':values[0], 'distance (cm)':values[1]})
        sys.stdout.write('{}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')


if __name__ == '__main__':
    FLAGS, unparsed = parser.parse_known_args()

    if FLAGS.debug:
        # https://code.visualstudio.com/docs/python/debugging#_remote-debugging
        # Launch applicaiton on remote computer: 
        # > python3 -m ptvsd --host 0.0.0.0 --port 3000 --wait predict_imdb.py
        import ptvsd
        # Allow other computers to attach to ptvsd at this IP address and port.
        ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)
        # Pause the program until a remote debugger is attached
        print("Wait for debugger attach")
        ptvsd.wait_for_attach()
        print("Debugger Attached")

    ser = GetPort(config['serial_port'])
    with serial.threaded.ReaderThread(ser, PrintLines) as protocol:
        #socketio.run(app, host='0.0.0.0', port=config['network_port'])
        app.run(host='0.0.0.0', port=config['network_port'], threaded=True)


    print('After app.run')
