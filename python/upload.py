import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle

#change the range if needed
SAMPLE_RANGE_NAME = 'A1:AA1000'

def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        #return service
    except Exception as e:
        print(e)
        #return None
    
def Export_Data_To_Sheets(rides_sheet_id, df):
    response_date = service.spreadsheets().values().update(
        spreadsheetId=rides_sheet_id,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()
    print('Sheet successfully Updated')

if __name__ == '__main__':
    
    df = pd.DataFrame()
    
    with open(r'.\output.txt', 'r') as in_file:
        lines = in_file.readlines()
        drivers = lines[0].strip().split(',')
        passengers = lines[1].strip().split(',')
        address = lines[2].strip().split(',')
        phone = lines[3].strip().split(',')

        df['Drivers'] = drivers[:-1]
        df['Passengers'] = passengers
        df['Address'] = address
        df['Phone'] = phone

    with open(r'..\download_upload.txt') as f:
        rides_sheet_id = f.readlines()[1].strip('\n')
    
    Create_Service('credentials.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])

    Export_Data_To_Sheets(rides_sheet_id, df)