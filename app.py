from flask import Flask
from flask import request
app = Flask(__name__)
import requests
import sys
@app.route('/')
def start():
    return 'Hello i am a Health Check Container!\n /ping <---- you can check! \n'

@app.route('/ping')
def do_ping():
    error = ' '
    response1 = ' '
    response2 = ' '
    response3 = ' '
    try:
        response1 = requests.get('http://member:4001/pong')
        
    except requests.exceptions.RequestException as e:
        print('Cannot reach the memeber container.\n', file=sys.stderr)
        error = requests.get('http://resource:4004/error?con=M')
        return 'M_ERROR\n'
    
    try:
        response2 = requests.get('http://product:4002/pong', file=sys.stderr)
        
    except requests.exceptions.RequestException as e:
        print('Cannot reach the product container.\n')
        error = requests.get('http://resource:4004/error?con=P')
        return 'P_ERROR\n'

    try:
        response3 = requests.get('http://inquiry:4003/pong', file=sys.stderr)
        
    except requests.exceptions.RequestException as e:
        print('Cannot reach the inquiry container.\n')
        error = requests.get('http://resource:4004/error?con=I')
        return 'I_ERROR\n'


    print('NO ERROR \n',file=sys.stderr)
    return 'NO_ERROR\n'
if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 4000, debug = True)