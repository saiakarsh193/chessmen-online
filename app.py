from flask import Flask, render_template, request, jsonify
import sys
import random

from dev.client import pingServer

if(len(sys.argv) == 1):
    myuid = 'guest_' + str(int(random.random() * 1000))
else:
    myuid = sys.argv[1]

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/ping', methods=['POST'])
def ping():
    if request.method == 'POST':
        req = request.get_json()['request']
        resp = 'ok !'
        if(req == 'getmyuid'):
            resp = myuid
        else:
            resp = pingServer(myuid + ' : ' + req)
        return jsonify({'response': resp}), 200

app.run(host='0.0.0.0', debug=True)