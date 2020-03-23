from __future__ import print_function

import operator
import pickle
import os.path
from collections import defaultdict
from pprint import pprint

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# import geocoder
import sys
from tinydb import TinyDB, Query
import itertools as it
import json
import gspread

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.

SPREAD_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ/edit#gid=1653540701"
STOCK_INITIAL_ROW = 4
STOCK_COLUMN_RANGE = ['B','F']

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

    
class SpreadsheetCrawler:
    def __init__(self):
        # Persistence
        self.db = TinyDB('corona.json')
        self.makers = self.db.table('makers')
        self.consumers = self.db.table('consumers')
        self.__credentials = None
        self.query = Query()
        self.__spreadsheet = None
        self.__conn = None


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
        stock_cols_names = char_range(STOCK_COLUMN_RANGE,STOCK_INITIAL_ROW)
        stock_cols_numbers = map(char_to_index, char_range(STOCK_COLUMN_RANGE))
        stock = defaultdict(list)
        for c, n in it.zip_longest(stock_cols_names, stock_cols_numbers):
            name = str(self.sheet.acell(c).value)
            print(c, n)
            stock[name] = self.sheet.col_values(n)[STOCK_INITIAL_ROW:-1]
        pprint(stock)



if __name__ == '__main__':
    crawl = SpreadsheetCrawler()
    crawl.change_sheet("Caceres")
    crawl.update_stock()
