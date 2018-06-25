# -*- coding: utf-8 -*-
#
#     Author : Suphakit Annoppornchai
#     Date   : Apr 5 2017
#
#          https://saixiii.ddns.net
# 
# Copyright (C) 2017  Suphakit Annoppornchai
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.

from __future__ import unicode_literals

import sys
import os
import json
import errno
import tempfile
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter
from time import strftime
from argparse import ArgumentParser
from kafka import KafkaProducer
from kafka.errors import KafkaError

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

app = Flask(__name__)

#-------------------------------------------------------------------------------
#     G L O B A L    V A R I A B L E S
#-------------------------------------------------------------------------------

botname = 'Saixiii'

# get channel_secret and channel_access_token from your environment variable
channel_secret = 'a4830b56ff9e5d85c3ff4a67f2360ee1'
channel_access_token = 'jibJtKouOP8/0UYtTRtlXcB70zzJlfKtBnCXH7m4OwgsEwRKezyI8/E8frwhWSUNtJ5efliVvp4eOCFyNksfrGCXAcsvVq7O8idF7dy1fesLrsrN0Nm4RGR1vkYxGSphrwhAHSFlm9kX7FYZmkxFTwdB04t89/1O/w1cDnyilFU='

# Log file configuration
log_file = os.path.join(os.path.dirname(__file__), 'log', botname) + '.log'
log_size = 1024 * 1024 * 10
log_backup = 50
log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
log_mode = logging.DEBUG

# Kafka configuration
kafka_topic = 'line-saixiii'
kafka_ip = 'saixiii.ddns.net'
kafka_port = '9092'

#-------------------------------------------------------------------------------
#     I N I T I A L    P R O G R A M
#-------------------------------------------------------------------------------

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

#-------------------------------------------------------------------------------
#     F U N C T I O N S
#-------------------------------------------------------------------------------
            
# Kafka - fuction producer create messages to topic
def kafka_producer(json_body):
    # create kafka producer instance
    producer = KafkaProducer(bootstrap_servers=[kafka_ip + ':' + kafka_port],value_serializer=lambda v: json.dumps(v).encode('utf-8'),retries=5)
    
    # push message asynchronous
    producer.send(kafka_topic, json_body)
    producer.flush()


@app.before_first_request
def setup_logging():
    # add log handler
    loghandler = RotatingFileHandler(log_file, maxBytes=log_size, backupCount=log_backup)
    loghandler.setFormatter(Formatter(log_format))
    loghandler.setLevel(log_mode)

    app.logger.addHandler(loghandler)
    app.logger.setLevel(log_mode)
    
    
    
@app.route("/callback", methods=['POST'])
def callback():
    
    # get request body as text
    body = request.get_data(as_text=True)
    kafka_producer(json.loads(body))
    app.logger.debug("Request body: " + body)
    
    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    
    app.run(debug=options.debug, port=options.port)