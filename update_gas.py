import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from config import SCOPES

# Load environment variables
load_dotenv()
SCRIPT_ID = os.getenv('SCRIPT_ID')

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def update_script(script_id, new_code):
    creds = get_credentials()
    service = build('script', 'v1', credentials=creds)
    with open('appsscript.json', 'r') as manifest_file:
        manifest = manifest_file.read()
    request = {
        'files': [
            {
                'name': 'Code',
                'type': 'SERVER_JS',
                'source': new_code
            },
            {
                'name': 'appsscript',
                'type': 'JSON',
                'source': manifest
            }
        ]
    }
    response = service.projects().updateContent(
        body=request,
        scriptId=script_id
    ).execute()
    print('Script updated!')

if __name__ == '__main__':
    with open('gas_code.js', 'r') as f:
        new_code = f.read()
    update_script(SCRIPT_ID, new_code) 