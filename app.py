import logging
import os
import time
from datetime import datetime

import requests
import schedule
from flask import Flask, request

SKIP_COUNT = 300
logger = logging.getLogger()
handler = logging.FileHandler('/tmp/health_check_logfile.log')
logger.addHandler(handler)
schedule.every().day.at("23:00").do(
    requests.get, "http://product:4002/sync")
app = Flask(__name__)


@app.route('/')
def start():
    return 'Hello i am a Health Check Container!\n /ping <---- you can check! \n'


@app.route('/startCheck')
def checkContainers():
    global schedule
    global SKIP_COUNT
    memberNoAckNum = 0
    productNoAckNum = 0
    gatewayNoAckNum = 0
    memberSkipCount = 0
    productSkipCount = 0
    gateWaySkipCount = 0

    while True:
        schedule.run_pending()

        if memberSkipCount < 1:
            try:
                response1 = requests.get(
                    'http://member:4001/register/ping', timeout=2)
                if response1.text != "OK":
                    memberNoAckNum += 1
            except requests.exceptions.RequestException as e:
                logging.warning(str(datetime.now())+'-> member: no response ')
                memberNoAckNum += 1
        else:
            memberSkipCount = memberSkipCount - 1

        if productSkipCount < 1:
            try:
                response2 = requests.get(
                    'http://product:4002/ping', timeout=2)
                if response2.text != "OK":
                    productNoAckNum += 1

            except requests.exceptions.RequestException as e:
                logging.warning(str(datetime.now())+': product: no response ')
                productNoAckNum += 1
        else:
            productSkipCount = productSkipCount - 1

        if gateWaySkipCount < 1:
            try:
                response3 = requests.get(
                    'http://gateway:8080/register/ping', timeout=2)
                if response3.text != "OK":
                    gatewayNoAckNum += 1

            except requests.exceptions.RequestException as e:
                logging.warning(str(datetime.now())+': gateway: no response ')
                gatewayNoAckNum += 1
        else:
            gateWaySkipCount = gateWaySkipCount - 1

        if memberNoAckNum > 3:
            logging.warning(str(datetime.now())+': restart member container')
            os.system("curl host.docker.internal:4050/error/member")
            memberSkipCount = SKIP_COUNT
            memberNoAckNum = 0

        if productNoAckNum > 3:
            logging.warning(str(datetime.now())+': restart product container')
            os.system("curl host.docker.internal:4050/error/product")
            productSkipCount = SKIP_COUNT
            productNoAckNum = 0

        if gatewayNoAckNum > 3:
            logging.warning(str(datetime.now())+': restart gateway container')
            os.system("curl host.docker.internal:4050/error/gateway")
            gateWaySkipCount = SKIP_COUNT
            gatewayNoAckNum = 0
        time.sleep(1.5)


@app.route('/test')
def test():
    global logger
    os.system("curl host.docker.internal:8080/v1/users/test")
    return 'test'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
