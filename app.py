import argparse
from flask import Flask, render_template, request, jsonify

from dev.client import chessbonClient

parser = argparse.ArgumentParser(description="flask client side for CHESSBON")
parser.add_argument("--user_id", "-u", help="CHESSBON user id of the client", type=str, default=None)
parser.add_argument("--debug", help="flask debug flag", action="store_true")
args = parser.parse_args()

client = chessbonClient(user_id=args.user_id)
app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')

# CHESSBON: CHESS Board ONline
@app.route('/chessbon', methods=['POST'])
def ping():
    if request.method == 'POST':
        req = request.get_json()['request']
        resp = client.ping(request=req)
        return jsonify({'response': resp}), 200

app.run(host='0.0.0.0', debug=args.debug)
