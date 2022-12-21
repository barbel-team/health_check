import logging
import os
import sys
import time
from sched import scheduler

import requests
from flask import Flask, request

scheduler.every().day.at("23:00").do(requests.get('http://product:4002/sync'))
app = Flask(__name__)


@app.route('/')
def start():
    return 'Hello i am a Health Check Container!\n /ping <---- you can check! \n'


@app.route('/startCheck')
def checkContainers():
    global schedule
    memberNoAckNum = 0
    productNoAckNum = 0
    gatewayNoAckNum = 0

    while True:
        schedule.run_pending()
        try:
            response1 = requests.get('http://member:4001/ping', timeout=2)
            if response1.text != "OK":
                memberNoAckNum += 1
            print("member: ", response1.text)
        except requests.exceptions.RequestException as e:
            memberNoAckNum += 1

        try:
            response2 = requests.get(
                'http://product:4002/ping', timeout=2)
            if response2.text != "OK":
                productNoAckNum += 1
            print("product: ", response2.text)

        except requests.exceptions.RequestException as e:
            productNoAckNum += 1

        try:
            response3 = requests.get(
                'http://gateway:8080/ping', timeout=2)
            if response3.text != "OK":
                gatewayNoAckNum += 1
            print("gateway: ", response3.text)

        except requests.exceptions.RequestException as e:
            gatewayNoAckNum += 1

        if memberNoAckNum > 3:
            logging.warning('restart member container')
            os.system("curl host.docker.internal:4050/error/member")
            memberNoAckNum = 0
        if productNoAckNum > 3:
            logging.warning('restart product container')
            os.system("curl host.docker.internal:4050/error/product")
            productNoAckNum = 0
        if gatewayNoAckNum > 3:
            logging.warning('restart gateway container')
            os.system("curl host.docker.internal:4050/error/gateway")
            gatewayNoAckNum = 0
        time.sleep(1)


@app.route('/test')
def test():
    os.system("curl host.docker.internal:8080/v1/users/test")
    return 'test'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
