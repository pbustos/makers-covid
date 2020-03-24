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
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send

import dictdiffer

import utils
from gspread_crawler import GSpreadCrawler
from xlsx_crawler import XLSXCrawler

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE = os.path.join(CURRENT_DIR ,"{0}/{1}.log").format("logs", "test.py")


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

@socketio.on('connect')
def handle_connection():
    with open(os.path.join(CURRENT_DIR,'data_Caceres.json'), 'f') as file:
        data = json.load(file)
        socketio.emit('connection_response', {'data': data})

def update(update):
    logging.info("Broadcasting update")
    socketio.emit('update', { "data" : update}, broadcast=True)


class CovidUpdater(threading.Thread):
    def __init__(self):
        # Persistence
        super().__init__()
        self.__current_jsons = defaultdict(dict)
        if config["crawler"] == "xlsx":
            self.__info_getter = XLSXCrawler()
        elif config["crawler"] == "gspread":
            self.__info_getter = GSpreadCrawler()
    def update_stock(self):
        stock_column_range = SHEET_DATA[self.sheet.title]["STOCK_COLUMN_RANGE"]
        stock_initial_column = SHEET_DATA[self.sheet.title]["STOCK_INITIAL_ROW"]
        stock_headers_map = SHEET_DATA[self.sheet.title]["STOCK_HEADERS_MAP"]
        stock_column_types = SHEET_DATA[self.sheet.title]["STOCK_COLUMN_TYPES"]
        return self.update_subtable(stock_column_range,stock_initial_column, stock_headers_map, stock_column_types)

    def update_demand(self):
        demand_column_range = SHEET_DATA[self.sheet.title]["DEMAND_COLUMN_RANGE"]
        demand_initial_column = SHEET_DATA[self.sheet.title]["DEMAND_INITIAL_ROW"]
        demand_headers_map = SHEET_DATA[self.sheet.title]["DEMAND_HEADERS_MAP"]
        demand_column_types = SHEET_DATA[self.sheet.title]["DEMAND_COLUMN_TYPES"]
        return self.update_subtable(demand_column_range, demand_initial_column, demand_headers_map, demand_column_types)


    def update_subtable(self, column_range, initial_row, headers_mapping, types_map):
        header_range = column_range[0]+str(initial_row)+":"+column_range[-1]+str(initial_row)
        data_range = column_range[0]+str(initial_row+1)+":"+column_range[-1]+str(1000)
        headers = self.sheet.range(header_range)
        header_values = list(map(lambda x: utils.clean_and_map_header(x.value, headers_mapping), headers))
        data = self.sheet.range(data_range)
        json = {}
        for row in utils.chunks(data,len(utils.char_range(column_range))):
            row_values = list(map(lambda x: utils.remove_special_chars(x.value.strip()), row))
            if row_values[0] != '':
                row_values = utils.reasign_type(types_map, row_values)
                row_dict = dict(zip(header_values,row_values))
                row_dict["Localidad"] = self.sheet.title
                json[row_values[0]]= (row_dict)
        return json
            
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
                with open(os.path.join(CURRENT_DIR,'last_update_'+table+'.json'), 'w') as outfile:
                    json.dump(list_diff_result, outfile, indent=4)

    def run(self):
        while(True):
            logging.info("compute")
            self.update_all()
            time.sleep(10)


if __name__ == '__main__':
    crawl = CovidUpdater()
    crawl.start()
    socketio.run(app, host='0.0.0.0', port=SOCKETIO_PORT, log_output=False, debug=False)

    # logging.info("despues")
    # crawl.change_sheet("Caceres")
    # final_json = {}
    # final_json["demand"] = crawl.update_demand()
    # final_json["makers"] = crawl.update_stock()
    # import json
    # with open('data.json', 'w') as fp:
    #     json.dump(final_json, fp)
    # plogging.info(final_json)
