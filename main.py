from flask import Flask,render_template,url_for,request,redirect, make_response
import random
import math
from datetime import datetime
import json
import time
import os
import glob
from flask import Flask, Response, render_template, stream_with_context


os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

'''
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
'''

dir1 = f"{base_dir}28-0118762581ff/w1_slave"
dir2 = f"{base_dir}28-00000b3231c5/w1_slave"


def read_temp(dir):
    with open(dir,"r") as f:
        lines = f.readlines()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        with open(dir,"r") as f:
            lines = f.readlines()

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

app = Flask(__name__)

def getdata(n):
    if n == 1:
        return read_temp(dir1)
    elif n == 2:
        return read_temp(dir2)
    else:
        return -1

@app.route('/', methods=["GET", "POST"])
def main():
    temp1 = getdata(dir1)
    temp2 = getdata(dir2)
    return render_template('index.html', t1=temp1)



@app.route('/data')
def chart_data():
    def generate_random_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%H:%M:%S'), 'value': getdata(1),'value2': getdata(2)})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    response = Response(stream_with_context(generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80,debug=True, threaded=True)