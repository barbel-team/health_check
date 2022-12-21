import logging
import os
import sys

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def start():
    return 'Hello i am a Health Check Container!\n /ping <---- you can check! \n'


@app.route('/startCheck')
def checkContainers():
    memberNoAckNum = 0
    productNoAckNum = 0
    gatewayNoAckNum = 0

    while True:
        try:
            response1 = requests.get('http://member:4001/ping')
        except requests.exceptions.RequestException as e:
            memberNoAckNum += 1

        try:
            response2 = requests.get(
                'http://product:4002/ping', file=sys.stderr)

        except requests.exceptions.RequestException as e:
            productNoAckNum += 1

        try:
            response3 = requests.get(
                'http://gateway:8080/ping', file=sys.stderr)

        except requests.exceptions.RequestException as e:
            gatewayNoAckNum += 1

        if memberNoAckNum > 3:
            logging.warning('restart member container')
            os.system("curl host.docker.internal:8080/error/member")
            memberNoAckNum = 0
        if productNoAckNum > 3:
            logging.warning('restart product container')
            os.system("curl host.docker.internal:8080/error/product")
            productNoAckNum = 0
        if gatewayNoAckNum > 3:
            logging.warning('restart gateway container')
            os.system("curl host.docker.internal:8080/error/gateway")
            gatewayNoAckNum = 0
        sleep(1)
        print('NO ERROR \n', file=sys.stderr)
        return 'NO_ERROR\n'


@app.route('/test')
def test():
    os.system("curl host.docker.internal:8080/v1/users/test")
    return 'test'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
