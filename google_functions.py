from google.oauth2 import service_account
import googleapiclient.discovery
import config

googleCredentials = service_account.Credentials.from_service_account_file(config.google['service_account_file'], scopes=config.google['scopes'])
sheetsService = googleapiclient.discovery.build('sheets', 'v4', credentials=googleCredentials)

def get_sheet_values(id, range, data_filter):
    data_filters = [
        {

        }
    ]
    sheet_values = sheetsService.spreadsheets().values().batchGetByDataFilter(
        spreadsheetId=id,
        body=request_body
    ).execute()
    return sheet_values

def update_sheet(id, range, values):
    sheet_response = sheetsService.spreadsheets().values().update(
        spreadsheetId=id,
        range=range,
        valueInputOption = 'USER_ENTERED',
        body={
            'values': [values]
        }
    ).execute()
    print(sheet_response)

def append_sheet(id, range, values):
    sheet_response = sheetsService.spreadsheets().values().append(
        spreadsheetId=id, 
        range=range,
        valueInputOption = 'USER_ENTERED',
        body={
            'values': [values]
        }
    ).execute()
    return sheet_response
