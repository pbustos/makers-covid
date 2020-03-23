from __future__ import print_function
import pickle
import os.path
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

SAMPLE_SPREADSHEET_ID = '1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ'
SAMPLE_RANGE_NAME = 'Caceres!B5:F5'

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

    
class SpreadsheetCrawler:
    def __init__(self):
        # Persistence
        self.db = TinyDB('corona.json')
        self.makers = self.db.table('makers')
        self.consumers = self.db.table('consumers')
        self.query = Query()

        mycreds = MyCredentials()
        gc = gspread.authorize(mycreds)
        makers_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ/edit#gid=1653540701')
        caceres = makers_sheet.get_worksheet(9)
        print(caceres)

    # def update_stock(self):
    #     if self.sheet is not None:
    #         values = self.sheet.values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                                          ranges=["Caceres!B5:B100", "Caceres!C5:C100", "Caceres!D5:D100",
    #                                                  "Caceres!E5:E100", "Caceres!F5:F100"]).execute()

    #         if not values:
    #             print('No data found.')
    #         else:
    #             nombres = [item for sublist in values['valueRanges'][0]['values'] for item in sublist]
    #             capacidad = [item for sublist in values['valueRanges'][1]['values'] for item in sublist]
    #             stock = [item for sublist in values['valueRanges'][2]['values'] for item in sublist]
    #             entregadas = [item for sublist in values['valueRanges'][3]['values'] for item in sublist]
    #             direccion = [item for sublist in values['valueRanges'][4]['values'] for item in sublist]

    #         for n, c, s, e, d in it.zip_longest(nombres, capacidad, stock, entregadas, direccion):
    #             self.makers.upsert({'nombre': n, 'capacidad': c, 'stock': s, 'entregadas': e, 'direccion': d}, self.query.nombre == n)

    #         for r in self.makers.all():
    #             print(r)
    #         print("Total:", len(self.makers))


if __name__ == '__main__':
    crawl = SpreadsheetCrawler()
    #crawl.update_stock()
