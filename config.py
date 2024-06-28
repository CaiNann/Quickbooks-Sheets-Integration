quickbooks = {
    'client_id' : 'ABELy2kJPVjKIaWycZKD8B9rF1fPLpMyxq5Y5zhgOY8jd5l4Fj',
    'client_secret' : '05EYhumz1oXvKQqiCOVsVYhCvUZ2OV4Pi688esWL',
    'redirect_uri' : 'https://duckling-arriving-highly.ngrok-free.app/callback',
    'environment' : 'sandbox',
    'realm_id' : '9341452557106265',
    'token_endpoint' : 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
    'authorization_endpoint' : 'https://appcenter.intuit.com/connect/oauth2',
    'production_base_url' : 'https://quickbooks.api.intuit.com',
    'sandbox_base_url' : 'https://sandbox-quickbooks.api.intuit.com',
    'webhooks_verifier' : '0b3b3680-fd06-4141-be03-c506fee30b82',
    'scopes' : ['com.intuit.quickbooks.accounting'],
}

google = {
    'scopes' : ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file'],
    'service_account_file' : 'googleServiceAccount.json',
    'odfl_link': 'https://www.odfl.com/us/en/tools/trace-track-ltl-freight/trace.html?proNumbers=',
    'fedex_link': 'https://www.fedex.com/fedextrack/?tracknumbers=',
    'ups_link': 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=',
    'daylight_link': 'https://mydaylight.dylt.com/external/shipment?probill=',
    'spreadsheet_id': '1fRHggwg7dhvj7447InWxbL2qY7mQLcys13e0iTN2E0s',
    'sheet_id': '1342435178',
    'append_table_range': 'Open Order Report!A:E'
}