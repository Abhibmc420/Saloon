import os
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

SCOPES = ['openid', 'email', 'profile']


def google_sign_in():
    """Runs the Google OAuth installed app flow and returns user info dict {email, name, sub} or None"""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise RuntimeError('GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment')

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    # Try to get userinfo
    resp = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'alt': 'json'},
        headers={'Authorization': f'Bearer {creds.token}'}
    )

    if resp.status_code != 200:
        return None

    data = resp.json()
    # data contains id, email, verified_email, name, given_name, family_name, picture, locale
    return {
        'email': data.get('email'),
        'full_name': data.get('name'),
        'google_id': data.get('id')
    }
