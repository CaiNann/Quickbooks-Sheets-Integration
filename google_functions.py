from google.oauth2 import service_account
import googleapiclient.discovery
import config

googleCredentials = service_account.Credentials.from_service_account_file(config.google['service_account_file'], scopes=config.google['scopes'])
sheetsService = googleapiclient.discovery.build('sheets', 'v4', credentials=googleCredentials)

def get_sheet_values(id, range):
    sheet_values = sheetsService.spreadsheets().values().get(
        spreadsheetId=id,
        range=range,
        majorDimension='COLUMNS'
    ).execute()
    return sheet_values

def update_row(id, estimate_id, values):
    all_estimate_ids = get_sheet_values(id, config.google['data_lookup_range'])['values'][0]
    row = None
    for num in all_estimate_ids:
        if num == estimate_id:
            row = all_estimate_ids.index(num) + 1
            break
    if row == None:
        print("Could not find row with given value " + estimate_id)
        return 0
    sheet_response = sheetsService.spreadsheets().values().update(
        spreadsheetId=id,
        range=f'{config.google['sheet_name']}!A{row}',
        valueInputOption = 'USER_ENTERED',
        body={
            'values': [values]
        }
    ).execute()
    return sheet_response

def append_row(id, values):
    sheet_response = sheetsService.spreadsheets().values().append(
        spreadsheetId=id, 
        range=config.google['append_table_range'],
        valueInputOption = 'USER_ENTERED',
        body={
            'values': [values]
        }
    ).execute()
    return sheet_response

def delete_row(id, estimate_id):
    values = [' ', ' ', ' ', ' ', ' ', ' ']
    return update_row(id, estimate_id, values)