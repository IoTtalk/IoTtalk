from flask import Flask, redirect, request
import sys, os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

import ec_config

app = Flask(__name__)

'''
@app.route('/')
def index():
    return redirect('http://{}:9999/da/Remote_control'.format(request.host))
'''

@app.route('/rc')
def Remote_control_redirect():
    return redirect('http://{}:9999/da/Remote_control'.format(request.host))

@app.route('/')
def home_redirect():
    return redirect('http://{}:9999/'.format(request.host))

@app.route('/msg/')
def msg_redirect():
    return redirect('http://{}:9999/msg'.format(request.host))

app.run('0.0.0.0', port=int("82"),debug=True, threaded=True)
