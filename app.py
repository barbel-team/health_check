import logging
import os
import time
from datetime import datetime

import requests
import schedule
from flask import Flask, request

logger = logging.getLogger()
handler = logging.FileHandler('/tmp/health_check_logfile.log')
logger.addHandler(handler)
schedule.every().day.at("23:00").do(
    requests.get, "curl http://product:4002/sync")
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
            logging.warning(str(datetime.now())+'-> member: no response ')
            memberNoAckNum += 1

        try:
            response2 = requests.get(
                'http://product:4002/ping', timeout=2)
            if response2.text != "OK":
                productNoAckNum += 1
            print("product: ", response2.text)

        except requests.exceptions.RequestException as e:
            logging.warning(str(datetime.now())+': product: no response ')
            productNoAckNum += 1

        try:
            response3 = requests.get(
                'http://gateway:8080/ping', timeout=2)
            if response3.text != "OK":
                gatewayNoAckNum += 1
            print("gateway: ", response3.text)

        except requests.exceptions.RequestException as e:
            logging.warning(str(datetime.now())+': gateway: no response ')
            gatewayNoAckNum += 1

        if memberNoAckNum > 3:

            logging.warning(str(datetime.now())+': restart member container')
            os.system("curl host.docker.internal:4050/error/member")
            memberNoAckNum = 0
        if productNoAckNum > 3:
            logging.warning(str(datetime.now())+': restart product container')
            os.system("curl host.docker.internal:4050/error/product")
            productNoAckNum = 0
        if gatewayNoAckNum > 3:
            logging.warning(str(datetime.now())+': restart gateway container')
            os.system("curl host.docker.internal:4050/error/gateway")
            gatewayNoAckNum = 0
        time.sleep(1)


@app.route('/test')
def test():
    global logger
    os.system("curl host.docker.internal:8080/v1/users/test")
    return 'test'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
