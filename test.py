from __future__ import print_function

import logging
import os
import sys
import threading
import time
import json
from collections import defaultdict
from logging import handlers

import yaml
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send, join_room, leave_room

import dictdiffer

import utils
from gspread_crawler import GSpreadCrawler
from gspread_crawler2 import GSpreadCrawler2
from xlsx_crawler import XLSXCrawler

from persistence import Persistence

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE = os.path.join(CURRENT_DIR, "{0}/{1}.log").format("logs", "test.py")


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

fileHandler = handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=7)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


with open(os.path.join(CURRENT_DIR,'config.yml'), 'r', encoding='utf8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    SPREAD_SHEET_URL = config["SPREAD_SHEET_URL"]
    SHEET_DATA = config["SHEET_DATA"]
    SCOPES = config["SCOPES"]
    SOCKETIO_PORT = config["SOCKETIO_PORT"]


app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
clients = []

@socketio.on('connect')
def handle_connection():
    logging.info("Direct data petition connection")
    with open(os.path.join(CURRENT_DIR,'data_Caceres.json'), 'r') as file:
        
        #data = json.load(file)
        data = CovidUpdater.persistence.getLast()
        room = request.sid
        clients.append(room)
        join_room(room)

        try:
            socketio.emit('connection_response', {'data': data}, room=room)
        except Exception as e:
            logging.exception("Problem emitting socketio: connection_response")


@socketio.on('close')
def disconnect():
    logging.info("Client left")
    room = request.sid
    clients.remove(room)
    leave_room(room)

    


def update(update):
    logging.info("Broadcasting update")
    try:
        if len(clients) > 0:
            socketio.emit('update', { "data" : update}, broadcast=True)
    except Exception as e:
        logging.exception("Problem emitting socketio: update")


class CovidUpdater(threading.Thread):
    def __init__(self):
        # Persistence
        super().__init__()
        self.__current_jsons = defaultdict(dict)
        if config["crawler"] == "xlsx":
            self.__info_getter = XLSXCrawler()
        elif config["crawler"] == "gspread":
            self.__info_getter = GSpreadCrawler()
        elif config["crawler"] == "gspread2":
            self.__info_getter = GSpreadCrawler2()

        self.persistence = Persistence()

    def update_all(self):
        for table in SHEET_DATA.keys():
            final_json = self.__info_getter.get_worksheet_data(table)
            diff_result = dictdiffer.diff(self.__current_jsons[table], final_json, dot_notation=False)
            list_diff_result = list(diff_result)
            if len(list_diff_result) > 0:
                self.__current_jsons[table] = final_json
                with app.test_request_context():
                    update(list_diff_result)
                logging.info(list_diff_result)
                with open(os.path.join(CURRENT_DIR,'data_'+table+'.json'), 'w') as outfile:
                    json.dump(final_json, outfile, indent=4)
                    self.persistence.insert(final_json)
                with open(os.path.join(CURRENT_DIR,'last_update_'+table+'.json'), 'w') as outfile:
                    json.dump(list_diff_result, outfile, indent=4)

    def run(self):
        while(True):
            logging.info("compute")
            self.update_all()
            time.sleep(30)


if __name__ == '__main__':
    crawl = CovidUpdater()
    logging.info("Starting thread")
    crawl.start()
    try:
        socketio.run(app, host='0.0.0.0', port=SOCKETIO_PORT, log_output=False, debug=False)
    except Exception as e:
        logging.exception("Problem in socketio RUN: CLOSING")

    # logging.info("despues")
    # crawl.change_sheet("Caceres")
    # final_json = {}
    # final_json["demand"] = crawl.update_demand()
    # final_json["makers"] = crawl.update_stock()
    # import json
    # with open('data.json', 'w') as fp:
    #     json.dump(final_json, fp)
    # plogging.info(final_json)
