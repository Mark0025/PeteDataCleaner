import os
import sys
import pickle
from googleapiclient.discovery import build
from dotenv import load_dotenv
from config import SCOPES

load_dotenv()
DEPLOYMENT_ID = os.getenv('DEPLOYMENT_ID')  # Use this for API function execution

# Load credentials from token.pickle
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        raise Exception('token.pickle not found. Run update_gas.py to authenticate.')
    return creds

def run_function(deployment_id, function_name):
    creds = get_credentials()
    service = build('script', 'v1', credentials=creds)
    request = {
        "function": function_name
    }
    response = service.scripts().run(
        body=request,
        scriptId=deployment_id
    ).execute()
    print(f"Function '{function_name}' executed. Response: {response}")

if __name__ == "__main__":
    # Usage: uv run python run_gas_function.py [function_name]
    function_name = sys.argv[1] if len(sys.argv) > 1 else "sendTestEmail"
    run_function(DEPLOYMENT_ID, function_name) 