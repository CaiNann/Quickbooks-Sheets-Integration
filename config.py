quickbooks = {
    'client_id' : 'ABwblY4MTowT4spKu9ugot5tS7RmEbgjK80O6sRrVEgkdrMqbw',
    'client_secret' : 'efdHsrI7HCtwgXcbL6T5gDh9tjth732W8yjdcXeE',
    'redirect_uri' : 'https://uc5je1vv6h.execute-api.us-west-1.amazonaws.com/test/callback',
    'environment' : 'production',
    'realm_id' : '9341452557106265',
    'token_endpoint' : 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
    'authorization_endpoint' : 'https://appcenter.intuit.com/connect/oauth2',
    'production_base_url' : 'https://quickbooks.api.intuit.com',
    'sandbox_base_url' : 'https://sandbox-quickbooks.api.intuit.com',
    'webhooks_verifier' : '27b0daba-99c7-4e27-8188-d86c60c5cb48',
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
    'sheet_name': 'Open Order Report',
    'append_table_range': 'Open Order Report!A:F',
    'data_lookup_range': 'Open Order Report!A:A'
}