from __future__ import print_function
import os.path
import pickle
import threading
import time
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import gspread
import dictdiffer
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.

SPREAD_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ/edit#gid=1653540701"

SHEET_DATA = {
    "Caceres": {
        "STOCK_INITIAL_ROW": 4,
        "STOCK_COLUMN_RANGE": ['B','F'],
        "STOCK_HEADERS_MAP": {"Usuario Telegram": "usuario"},
        "DEMAND_INITIAL_ROW": 4,
        "DEMAND_COLUMN_RANGE": ['H','K'],
        "DEMAND_HEADERS_MAP": {"Organización": "usuario"}
    }
}

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connection():
    with open('data.json') as file:
        data = json.load(file)
        socketio.emit('connection_response', {'data': data})

def update(update):
    print("Broadcasting update")
    socketio.emit('update', { "data" : update}, broadcast=True)

class MyCredentials (object):
    def __init__ (self, access_token=None):
        self.access_token = access_token

    def refresh (self, http):
        self.access_token = self.readCredentials('credentials.json').token

    def readCredentials(self, file_name):
        ## Initialize Sheets API
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(file_name, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

def char_range(from_to, row=None):
    c1 = from_to[0]
    c2 = from_to[1]
    char_range = []
    for c in range(ord(c1), ord(c2)+1):
        if row is not None:
            char_range.append(chr(c)+str(row))
        else:
            char_range.append(chr(c))
    return char_range

def char_to_index(char):
    char = char.upper()
    index = ord(char)-ord('A')+1
    return index

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def clean_and_map_header(header, map):
    new_header = header.strip()
    if new_header in map:
        new_header = map[new_header]
    return new_header.lower()

class SpreadsheetCrawler(threading.Thread):
    def __init__(self):
        # Persistence
        super().__init__()
        self.__credentials = None
        self.__spreadsheet = None
        self.__conn = None
        self.__current_json = {}

    @property
    def spreadsheet(self):
        if self.__spreadsheet is None:
            self.__init_spreadsheet()
        return self.__spreadsheet

    def __init_spreadsheet(self):
        if self.__conn is None:
            self.__init_conn()
        if self.__spreadsheet is None:
            self.__spreadsheet = self.__conn.open_by_url(SPREAD_SHEET_URL)

    def __init_conn(self):
        mycreds = MyCredentials()
        self.__conn = gspread.authorize(mycreds)

    def change_sheet(self, sheet):
        if isinstance(sheet,int):
            self.sheet =self.spreadsheet.get_worksheet(sheet)
        elif isinstance(sheet, str):
            self.sheet = self.spreadsheet.worksheet(sheet)

    def update_stock(self):
        stock_column_range = SHEET_DATA[self.sheet.title]["STOCK_COLUMN_RANGE"]
        stock_initial_column = SHEET_DATA[self.sheet.title]["STOCK_INITIAL_ROW"]
        stock_headers_map = SHEET_DATA[self.sheet.title]["STOCK_HEADERS_MAP"]
        return self.update_subtable(stock_column_range,stock_initial_column, stock_headers_map)

    def update_demand(self):
        demand_column_range = SHEET_DATA[self.sheet.title]["DEMAND_COLUMN_RANGE"]
        demand_initial_column = SHEET_DATA[self.sheet.title]["DEMAND_INITIAL_ROW"]
        demand_headers_map = SHEET_DATA[self.sheet.title]["DEMAND_HEADERS_MAP"]
        return self.update_subtable(demand_column_range, demand_initial_column, demand_headers_map)


    def update_subtable(self, column_range, initial_row, headers_mapping):
        header_range = column_range[0]+str(initial_row)+":"+column_range[-1]+str(initial_row)
        data_range = column_range[0]+str(initial_row+1)+":"+column_range[-1]+str(1000)
        headers = self.sheet.range(header_range)
        header_values = list(map(lambda x: clean_and_map_header(x.value, headers_mapping), headers))
        data = self.sheet.range(data_range)
        json = {}
        for row in chunks(data,len(char_range(column_range))):
            row_values = list(map(lambda x: x.value.strip(), row))
            if row_values[0] != '':
                row_dict = dict(zip(header_values,row_values))
                row_dict["Localidad"] = self.sheet.title
                row_dict["lat"] = ""
                row_dict["long"] = ""
                json[row_values[0]]= (row_dict)
        return json
            
    def update_all(self):
        for table in SHEET_DATA.keys():
            self.change_sheet(table)
            final_json = {}
            final_json["demand"] = self.update_demand()
            final_json["makers"] = self.update_stock()
            diff_result = dictdiffer.diff(self.__current_json, final_json, dot_notation=False)
            list_diff_result = list(diff_result)
            if len(list_diff_result) > 0:
                self.__current_json = final_json
                print("send update")
                print(list_diff_result)
                with open('data.json', 'w') as outfile:
                    json.dump(final_json, outfile, indent=4)
                with open('last_update.json', 'w') as outfile:
                    json.dump(list_diff_result, outfile, indent=4)

    def run(self):
        while(True):
            print("compute")
            self.update_all()
            with app.test_request_context(): 
                update("Envía por aquí lo que necesites")
            time.sleep(10)


if __name__ == '__main__':
    crawl = SpreadsheetCrawler()
    crawl.start()
    socketio.run(app, port=8000, log_output=False, debug=False)

    # print("despues")
    # crawl.change_sheet("Caceres")
    # final_json = {}
    # final_json["demand"] = crawl.update_demand()
    # final_json["makers"] = crawl.update_stock()
    # import json
    # with open('data.json', 'w') as fp:
    #     json.dump(final_json, fp)
    # pprint(final_json)
