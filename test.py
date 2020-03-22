from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import geocoder
import sys
from tinydb import TinyDB, Query
import itertools as it
import json


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1uWdmNRFeJNpwg0keMAodzf3xAXCL1cvz9mPFfdUcHmQ'
SAMPLE_RANGE_NAME = 'Caceres!B5:F5'

def main():

    # Persistence
    db = TinyDB('corona.json')
    makers = db.table('makers')
    consumers = db.table('consumers')
    query = Query();

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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    values = sheet.values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=["Caceres!B5:B100","Caceres!C5:C100","Caceres!D5:D100","Caceres!E5:E100","Caceres!F5:F100"]).execute()

    if not values:
        print('No data found.')
    else:
        nombres = [item for sublist in values['valueRanges'][0]['values'] for item in sublist]
        capacidad = [item for sublist in values['valueRanges'][1]['values'] for item in sublist]
        stock = [item for sublist in values['valueRanges'][2]['values'] for item in sublist]
        entregadas = [item for sublist in values['valueRanges'][3]['values'] for item in sublist]
        direccion = [item for sublist in values['valueRanges'][4]['values'] for item in sublist]
        
    for n,c,s,e,d in it.zip_longest(nombres,capacidad,stock,entregadas,direccion):
        makers.upsert({'nombre':n, 'capacidad':c, 'stock':s, 'entregadas':e, 'direccion':d}, query.nombre == n)
       
    for r in makers.all():
        print(r)
    print("Total:", len(makers))
    

            #g = geocoder.google(row[0], output="all", key="AIzaSyDh3w5epHrNhgdBhDa8Egt3Ydt1kLlocmE")
            #print(row[0], g.latlng)
        
if __name__ == '__main__':
    main()
