import gspread
import pickle
import os.path
import itertools as it
import copy
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'mapas-271913-30a1383d8e1b.json'

#mycreds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
mycreds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)

def readCredentials(file_name):
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

class MyCredentials (object):
  def __init__ (self, access_token=None):
    self.access_token = access_token

  def refresh (self, http):
    self.access_token = readCredentials('credentials.json').token
    

#mycreds = MyCredentials()

gc = gspread.authorize(mycreds)
makers_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ/edit?ts=5e7b4100#gid=1873691210')
print(makers_sheet.worksheets())
caceres = makers_sheet.worksheet('Caceres')
print(caceres.get_all_values())


# stock = dict()

# stock_cols_names = ('B4','C4','D4','E4','F4')
# stock_cols_numbers = range(2,7)



# for c,n in it.zip_longest(stock_cols_names,stock_cols_numbers):
#     name = str(caceres.acell(c).value)
#     stock[name] = caceres.col_values(n)[4:-1]







