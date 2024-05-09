import pandas as pd
import requests
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle
import re

pd.options.mode.chained_assignment = None

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

ST_DRIVERS = [
    "nfoord@purdue.edu",
    "fan316@purdue.edu",
    "iclee@purdue.edu",
    "deng247@purdue.edu",
    "fong22@purdue.edu",
    "park1345@purdue.edu",
    "llwan@purdue.edu",
]

PICKUP_LOCATIONS = set(
    [
        "aspire",
        "chauncey hill mall",
        "chauncey square",
        "co-rec bus stop",
        "earhart bus stop",
        "ford bus stop",
        "fuse",
        "hawkins",
    ]
)


def read_data(SAMPLE_SPREADSHEET_ID_input):
    SAMPLE_RANGE_NAME = "A1:AA1000"

    global values_input, service
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result_input = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values_input = result_input.get("values", [])

    return values_input


def get_link_id(link):
    result = re.search(r"^https://docs\.google\.com/spreadsheets/d/(.*)/.*$", link)

    return result.group(1)


# change the range if needed
SAMPLE_RANGE_NAME = "A1:AA1000"


def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    # print(SCOPES)

    cred = None

    if os.path.exists("token_write.pickle"):
        with open("token_write.pickle", "rb") as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open("token_write.pickle", "wb") as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, "service created successfully")
        # return service
    except Exception as e:
        print(e)
        # return None


def Export_Data_To_Sheets(rides_sheet_id, df):
    response_date = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=rides_sheet_id,
            valueInputOption="RAW",
            range=SAMPLE_RANGE_NAME,
            body=dict(
                majorDimension="ROWS", values=df.T.reset_index().T.values.tolist()
            ),
        )
        .execute()
    )
    print("Sheet successfully Updated")


if __name__ == "__main__":
    directory_sheet_id = "1KbVy8TNC_OCAGiApwRf3qL-BLndXq7nnz0LLq2n8gB4"
    directory_input = read_data(directory_sheet_id)

    directory_df = pd.DataFrame(directory_input[1:], columns=directory_input[0])
    directory_df = directory_df.apply(lambda x: x.astype(str).str.lower())
    directory_df = directory_df.apply(lambda x: x.astype(str).str.strip())

    sheets_link = input("Enter download spreadsheet link: ")
    sheet_id = get_link_id(sheets_link)

    download_input = read_data(sheet_id)

    download_df = pd.DataFrame(download_input[1:], columns=download_input[0])
    download_df = download_df.apply(lambda x: x.astype(str).str.lower())
    download_df = download_df.apply(lambda x: x.astype(str).str.strip())
    download_df = download_df.drop_duplicates(subset=["Purdue Email"], keep="last")

    passenger_df = pd.DataFrame(columns=["Name", "Phone #", "Pickup"])
    driver_df = pd.DataFrame(columns=["Name", "Phone #", "Pickup", "Seats"])
    rides_dict = {}
    location_df = pd.DataFrame(columns=["Location", "Passengers"])

    passenger_count = 0
    seat_total = 0

    for ind in download_df.index:
        name = download_df["Name (First and Last)"][ind]
        email = download_df["Purdue Email"][ind]

        if email in directory_df["Purdue Email"].unique():
            person_info = directory_df.loc[directory_df["Purdue Email"] == email]
            phone = person_info.iloc[0]["Phone number (Format: 123-456-7890)"]
            pickup = person_info.iloc[0]["Best Pickup Location"]

            if download_df["Do you need a ride?"][ind] == "yes":
                passenger_df.loc[len(passenger_df.index)] = [name, phone, pickup]
                passenger_count += 1
                if pickup in location_df["Location"].unique():
                    location_df.loc[
                        location_df["Location"] == pickup, "Passengers"
                    ] += 1
                else:
                    location_df.loc[len(location_df.index)] = [pickup, 1]

            elif download_df["Can you drive others?"][ind] == "yes":
                seats = int(
                    person_info.iloc[0][
                        "If the answer to the above question is yes / maybe, how many people can you drive (not including yourself)"
                    ]
                )
                driver_df.loc[len(driver_df.index)] = [name, phone, pickup, seats]
                seat_total += seats

        else:
            print("Email not found in directory")
            print(name, email)
            response = int(input("Email correction, manual input, or pass? (1/2/3): "))
            if response == 1:
                email = input("Enter correct email: ")
                email = email.strip().lower()

                person_info = directory_df.loc[directory_df["Purdue Email"] == email]
                phone = person_info.iloc[0]["Phone number (Format: 123-456-7890)"]
                pickup = person_info.iloc[0]["Best Pickup Location"]

                if download_df["Do you need a ride?"][ind] == "yes":
                    passenger_df.loc[len(passenger_df.index)] = [name, phone, pickup]
                    passenger_count += 1
                    if pickup in location_df["Location"].unique():
                        location_df.loc[
                            location_df["Location"] == pickup, "Passengers"
                        ] += 1
                    else:
                        location_df.loc[len(location_df.index)] = [pickup, 1]

                elif download_df["Can you drive others?"][ind] == "yes":
                    seats = int(
                        person_info.iloc[0][
                            "If the answer to the above question is yes / maybe, how many people can you drive (not including yourself)"
                        ]
                    )
                    driver_df.loc[len(driver_df.index)] = [
                        name,
                        phone,
                        pickup,
                        seats,
                    ]
                    seat_total += seats

            elif response == 2:
                phone = input("Enter phone number: ")
                pickup = input("Enter pickup location: ")

                option = int(input("Passenger or driver? (1/2): "))

                if option == 1:
                    passenger_df.loc[len(passenger_df.index)] = [name, phone, pickup]
                    passenger_count += 1
                    if pickup in location_df["Location"].unique():
                        location_df.loc[
                            location_df["Location"] == pickup, "Passengers"
                        ] += 1
                    else:
                        location_df.loc[len(location_df.index)] = [pickup, 1]
                else:
                    seats = int(input("Enter number of seats: "))
                    driver_df.loc[len(driver_df.index)] = [
                        name,
                        phone,
                        pickup,
                        seats,
                    ]
                    seat_total += seats

    while seat_total < passenger_count:
        email = ST_DRIVERS.pop(0)
        person_info = directory_df.loc[directory_df["Purdue Email"] == email]
        name = person_info.iloc[0]["What is your name? (First and Last)"]
        phone = person_info.iloc[0]["Phone number (Format: 123-456-7890)"]
        pickup = person_info.iloc[0]["Best Pickup Location"]
        seats = int(
            person_info.iloc[0][
                "If the answer to the above question is yes / maybe, how many people can you drive (not including yourself)"
            ]
        )
        driver_df.loc[len(driver_df.index)] = [name, phone, pickup, seats]

        seat_total += seats

    passenger_df = passenger_df.sort_values(by=["Pickup", "Name"])
    driver_df = driver_df.sort_values(by=["Seats", "Name"], ascending=False)
    location_df = location_df.sort_values(by=["Passengers"], ascending=False)

    for driver_ind in driver_df.index:
        driver_pickup = driver_df["Pickup"][driver_ind]
        driver_name = driver_df["Name"][driver_ind]
        driver_seats = driver_df["Seats"][driver_ind]

        if driver_pickup in PICKUP_LOCATIONS:
            for passenger_ind in passenger_df.index:
                passenger_pickup = passenger_df["Pickup"][passenger_ind]
                passenger_name = passenger_df["Name"][passenger_ind]
                passenger_phone = passenger_df["Phone #"][passenger_ind]

                if driver_pickup == passenger_pickup:
                    if driver_name in rides_dict:
                        rides_dict[driver_name].append(
                            (passenger_name, passenger_phone, passenger_pickup)
                        )
                    else:
                        rides_dict[driver_name] = [
                            (passenger_name, passenger_phone, passenger_pickup)
                        ]

                    passenger_df = passenger_df.drop([passenger_ind])
                    driver_seats -= 1

                    location_df.loc[
                        location_df["Location"] == driver_pickup, "Passengers"
                    ] -= 1

                    if driver_seats == 0:
                        driver_df = driver_df.drop([driver_ind])
                        break

                    driver_df["Seats"][driver_ind] = driver_seats

    passenger_df = passenger_df.sort_values(by=["Pickup", "Name"])
    driver_df = driver_df.sort_values(by=["Seats", "Name"], ascending=False)
    location_df = location_df.sort_values(by=["Passengers"], ascending=False)

    while location_df.empty == False:
        location_ind = location_df.index[0]
        location_name = location_df["Location"][location_ind]
        location_passengers = location_df["Passengers"][location_ind]

        driver_ind = driver_df.index[0]
        driver_name = driver_df["Name"][driver_ind]
        driver_seats = driver_df["Seats"][driver_ind]

        for passenger_ind in passenger_df.index:
            passenger_pickup = passenger_df["Pickup"][passenger_ind]
            passenger_name = passenger_df["Name"][passenger_ind]
            passenger_phone = passenger_df["Phone #"][passenger_ind]

            if passenger_pickup == location_name:
                if location_name in PICKUP_LOCATIONS:
                    if driver_name in rides_dict:
                        rides_dict[driver_name].append(
                            (passenger_name, passenger_phone, passenger_pickup)
                        )
                    else:
                        rides_dict[driver_name] = [
                            (passenger_name, passenger_phone, passenger_pickup)
                        ]

                    passenger_df = passenger_df.drop([passenger_ind])
                    driver_seats -= 1

                location_passengers -= 1

                location_df["Passengers"][location_ind] = location_passengers

                if driver_seats == 0:
                    driver_df = driver_df.drop([driver_ind])
                    break

                driver_df["Seats"][driver_ind] = driver_seats

        if location_passengers == 0:
            location_df = location_df.drop([location_ind])

        passenger_df = passenger_df.sort_values(by=["Pickup", "Name"])
        driver_df = driver_df.sort_values(by=["Seats", "Name"], ascending=False)
        location_df = location_df.sort_values(by=["Passengers"], ascending=False)

        print(passenger_df)
        print(driver_df)
        print(location_df)
        _ = input("ready for next iteration")

    print("Available Drivers")
    print(driver_df)
    print("\n")

    print("Leftover Passengers")
    print(passenger_df)
    print("\n")

    rides_keys = rides_dict.keys()

    upload_df = pd.DataFrame(columns=["Driver", "Passengers", "Address", "Phone #"])

    for key in rides_keys:
        passengers = rides_dict[key]
        driver_name = key
        for passenger in passengers:
            passenger_name = passenger[0]
            passenger_phone = passenger[1]
            passenger_pickup = passenger[2]

            upload_df.loc[len(upload_df.index)] = [
                driver_name,
                passenger_name,
                passenger_pickup,
                passenger_phone,
            ]

            driver_name = ""

        upload_df.loc[len(upload_df.index)] = ["", "", "", ""]

    _ = input("Please create a new sheet. Press enter when created: ")
    Create_Service(
        "credentials.json",
        "sheets",
        "v4",
        ["https://www.googleapis.com/auth/spreadsheets"],
    )

    Export_Data_To_Sheets(sheet_id, upload_df)

    _ = input("Hit enter when finished: ")
