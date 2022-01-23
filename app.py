from flask import Flask, render_template
import signal
 
def handler(signum, frame):
    exit(0)
 
signal.signal(signal.SIGINT, handler)

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')

app.run(debug=True)