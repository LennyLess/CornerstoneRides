import pandas as pd
import requests
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def read_data(SAMPLE_SPREADSHEET_ID_input):
    SAMPLE_RANGE_NAME = 'A1:AA1000'

    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])
    if not values_input and not values_expansion:
        print('No data found.')

    return values_input

def pos_lookup(address):
    sub = 'st$'
    pattern = sub + '(?!.*' + sub + ')'
    address = re.sub(pattern, "Street", address, 1, re.IGNORECASE)

    sub = 'dr$'
    pattern = sub + '(?!.*' + sub + ')'
    address = re.sub(pattern, "Drive", address, 1, re.IGNORECASE)

    sub = 'ave$'
    pattern = sub + '(?!.*' + sub + ')'
    address = re.sub(pattern, "Avenue", address, 1, re.IGNORECASE)

    sub = 'blvd$'
    pattern = sub + '(?!.*' + sub + ')'
    address = re.sub(pattern, "Boulevard", address, 1, re.IGNORECASE)

    api_key = "AIzaSyCjCxFY_-u8Ny5iI8A5cMIVoyRpP5jyxfQ"
    api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
    api_response_dict = api_response.json()

    if api_response_dict['status'] == 'OK':
        latitude = api_response_dict['results'][0]['geometry']['location']['lat']
        longitude = api_response_dict['results'][0]['geometry']['location']['lng']

    latitude = int(100000 * (latitude - 40.44651))
    longitude  = int(100000 * (longitude + 86.99134))

    return (latitude, longitude)

def location_pos(location):
    locations = {'aspire' : (-2253, 6660), 
                 'chauncey hill mall' : (-2261, 8357), 
                 'chauncey square' : (-2116, 8426), 
                 'co-rec bus stop' : (-1761, 6932), 
                 'earhart bus stop' : (-2061, 6627), 
                 'ford bus stop' : (-1421, 7200), 
                 'fuse' : (-1318, 7652), 
                 'hawkins' : (-2313, 7938),
                 'church' : (0,0),
                 'n/a' : (-1938, 7474)}

    if location in locations:
        return locations[location]

    else:
        return pos_lookup(location)

def pref_lookup(name):
    pref = {}

    if name in pref:
        return pref[name]
    else:
        return ''

if __name__ == '__main__':
    with open(r'..\download_upload.txt') as f:
        rides_sheet_id = f.readlines()[0].strip('\n')

    values_input = read_data(rides_sheet_id)

    rides_df = pd.DataFrame(values_input[1:], columns=values_input[0])

    rides_df = rides_df.rename(columns={'Name (First and Last)' : 'Name', 
                                                                    'Do you need a ride?' : 'Attendance',  
                                                                    'Can you drive others?' : 'Driver'})

    rides_df = rides_df[(rides_df['Attendance'] != 'no') | (rides_df['Driver'] != 'no')]
    rides_df = rides_df.drop(columns=['Attendance'])
    rides_df = rides_df.drop_duplicates(subset=['Purdue Email'])

    for (column_name, columnData) in rides_df.items():
        rides_df[column_name] = rides_df[column_name].str.lower()
        rides_df[column_name] = rides_df[column_name].str.strip()

    directory_sheet_id = '1KbVy8TNC_OCAGiApwRf3qL-BLndXq7nnz0LLq2n8gB4'

    values_input = read_data(directory_sheet_id)

    directory_df = pd.DataFrame(values_input[1:], columns=values_input[0])

    for (column_name, columnData) in directory_df.items():
        directory_df[column_name] = directory_df[column_name].str.lower()
        directory_df[column_name] = directory_df[column_name].str.strip()

    final_df = pd.DataFrame()

    final_df['Name'] = rides_df['Name']

    for (column_name, columnData) in final_df.items():
        final_df[column_name] = final_df[column_name].str.lower()
        final_df[column_name] = final_df[column_name].str.strip()

    purdue_emails = rides_df['Purdue Email'].values
    pickup_locations = []
    phone_numbers = []

    for email in purdue_emails:
        print(email)
        pickup_locations.append(directory_df.loc[directory_df['Purdue Email'] == email, 'Best Pickup Location'].iloc[0])
        phone_numbers.append(directory_df.loc[directory_df['Purdue Email'] == email, 'Phone number (Format: 123-456-7890)'].iloc[0])

    final_df['Pickup'] = pickup_locations
    final_df['Phone Number'] = phone_numbers

    drivers = rides_df['Name'].values
    seats = []

    for driver in drivers:
        print(driver)
        seat = directory_df.loc[directory_df['What is your name? (First and Last)'] == driver, 
                                'If the answer to the above question is yes / maybe, how many people can you drive (not including yourself)'].iloc[0]
        if seat == '':
            seat = 0
        seats.append(seat)

    final_df['Seats'] = seats

    long = []
    lat = []

    for location in pickup_locations:
        print(location)
        location = location.lower()

        coordinate = location_pos(location)
        lat.append(coordinate[0])
        long.append(coordinate[1])

    final_df['Lat'] = lat
    final_df['Long'] = long

    phone_numbers = final_df['Phone Number'].values

    pref = []

    for number in phone_numbers:
        pref.append(pref_lookup(number))

    final_df['Pref'] = pref
    
    final_df = final_df.sort_values(by=['Lat','Long'])

    with open(r'..\java\input.txt', 'w') as out_file:
        out_file.write(f"{str(len(final_df['Name']))},0,0\n")

    final_df.to_csv(r'..\java\input.txt',
                    header=None, index=None, sep=',', mode='a')
