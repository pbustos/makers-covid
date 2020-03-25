import os
import pickle
import gspread
import yaml
import unidecode
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import utils

import os
CURRENT_DIR =os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(CURRENT_DIR,'config.yml'), 'r' ,encoding='utf8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    SPREAD_SHEET_URL = config["SPREAD_SHEET_URL"]
    SHEET_DATA = config["SHEET_DATA"]
    SCOPES = config["SCOPES"]
    SOCKETIO_PORT = config["SOCKETIO_PORT"]

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

class GSpreadCrawler:
    def __init__(self):
        self.__credentials = None
        self.__spreadsheet = None
        self.__conn = None
        self.sheet = None

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
        if isinstance(sheet, int):
            self.sheet = self.spreadsheet.get_worksheet(sheet)
        elif isinstance(sheet, str):
            self.sheet = self.spreadsheet.worksheet(sheet)

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

    def get_worksheet_data(self, worksheet):
        self.change_sheet(worksheet)
        final_json = {}
        final_json["demand"] = self.update_demand()
        final_json["makers"] = self.update_stock()
        return final_json