import os
import pickle
import gspread
import yaml
import unidecode
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import utils

import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(CURRENT_DIR, 'config.yml'), 'r', encoding='utf8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    SPREAD_SHEET_URL = config["SPREAD_SHEET_URL"]
    SHEET_DATA = config["SHEET_DATA"]
    SCOPES = config["SCOPES"]
    SOCKETIO_PORT = config["SOCKETIO_PORT"]


class MyCredentials(object):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def refresh(self, http):
        self.access_token = self.readCredentials('credentials.json').token

    def readCredentials(self, file_name):
        ## Initialize Sheets API
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open(os.path.join(CURRENT_DIR, 'token.pickle'), 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(file_name, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(CURRENT_DIR, 'token.pickle'), 'wb') as token:
                pickle.dump(creds, token)
        return creds


class GSpreadUpdater:
    def __init__(self):
        self.__credentials = None
        self.__spreadsheet = None
        self.__conn = None
        self.__worksheet = None

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
            self.worksheet = self.spreadsheet.get_worksheet(sheet)
        elif isinstance(sheet, str):
            self.worksheet = self.spreadsheet.worksheet(sheet)

    # def get_stock_range(self):
    #     header_range = column_range[0] + str(initial_row) + ":" + column_range[-1] + str(initial_row)
    #     data_range = column_range[0] + str(initial_row + 1) + ":" + column_range[-1] + str(1000)
    #     headers = self.worksheet.range(header_range)
    #     header_values = list(map(lambda x: utils.clean_and_map_header(x.value, headers_mapping), headers))
    #     data = self.worksheet.range(data_range)
    #     json = {}
    #     for row in utils.chunks(data, len(utils.char_range(column_range))):
    #         row_values = list(map(lambda x: utils.remove_special_chars(x.value.strip()), row))
    #         if row_values[0] != '':
    #             row_values = utils.reasign_type(types_map, row_values)
    #             row_dict = dict(zip(header_values, row_values))
    #             row_dict["Localidad"] = self.worksheet.title
    #             json[row_values[0]] = (row_dict)
    #     return json

    def add_new_maker(self, table, values):
        # get first emtpy row
        self.change_sheet(table)
        range_len = len(utils.char_range(SHEET_DATA[self.worksheet.title]["STOCK_COLUMN_RANGE"]))
        assert len(values) == range_len, "Number of values must be %d but received %d" % (range_len, len(values))
        first_column_letter = SHEET_DATA[self.worksheet.title]["STOCK_COLUMN_RANGE"][0]
        column_index = utils.char_to_index(first_column_letter)
        index_first_empty = self.__next_available_row(column_index) +1
        row_range = utils.char_range(SHEET_DATA[self.worksheet.title]["STOCK_COLUMN_RANGE"], index_first_empty)
        self.worksheet.batch_update([{
            'range': row_range[0] + ":" + row_range[-1],
            'values': [values],
        }])
        # batch update
        pass

    def __next_available_row(self, index):
        str_list = filter(None, self.worksheet.col_values(index))
        return len(list(str_list)) + 1


if __name__ == '__main__':
    a = GSpreadUpdater()
    a.add_new_maker("Caceres", ["@pbustos", 10, 20, 32, "Cáceres (C/ La Roche Sur Yon)", "39.4606594", "-6.3695081"])
