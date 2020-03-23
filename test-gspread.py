import gspread
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

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
    
mycreds = MyCredentials()
gc = gspread.authorize(mycreds)
makers_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ/edit#gid=1653540701')
#print(makers_sheet.worksheets())

caceres = makers_sheet.get_worksheet(9)
print(caceres)
stock = str(caceres.acell('B3').value)
#"{" + stock + ": { " + user + ":"}
user = caceres.acell('B4').value
capacidad = caceres.acell('C4').value
stock_actual = caceres.acell('D4').value
entregadas = capacidad = caceres.acell('E4').value
direccion = capacidad = caceres.acell('F4').value

capacidad = caceres.acell('B4').value









