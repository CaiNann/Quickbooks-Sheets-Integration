from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


auth_client = AuthClient(
    'ABELy2kJPVjKIaWycZKD8B9rF1fPLpMyxq5Y5zhgOY8jd5l4Fj',
    '05EYhumz1oXvKQqiCOVsVYhCvUZ2OV4Pi688esWL',
    'https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl',
    'sandbox'
)

scopes = [
    Scopes.ACCOUNTING,
]

auth_url = auth_client.get_authorization_url(scopes)