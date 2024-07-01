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

def update_sheet(id, purchase_order_num, values):
    all_purchase_order_nums = get_sheet_values(id, config.google['data_lookup_range'])['values'][0]
    for num in all_purchase_order_nums:
        if num == purchase_order_num:
            row = all_purchase_order_nums.index(num) + 1
            print(row)
            break
    sheet_response = sheetsService.spreadsheets().values().update(
        spreadsheetId=id,
        range=f'{config.google['sheet_name']}!A{row}',
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
