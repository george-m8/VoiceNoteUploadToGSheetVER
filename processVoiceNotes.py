import requests
import os
import warnings
from io import StringIO

import pandas as pd
import numpy as np

from oauth2client.service_account import ServiceAccountCredentials
import gspread

def downloadCSV(login_url,sensetel_credentials,csv_url,csv_file_path):
    # Start a session
    session = requests.Session()

    # Attempt to login
    response = session.post(login_url, data=sensetel_credentials, allow_redirects=True)
    print(f"Response from login form: {response}")
    print(f"Response URL: {response.url}")

    # Check if login was successful
    if response.url.endswith('/admin') and response.status_code == 200:
        print("Logged in successfully.")
    else:
        print("Failed to log in. Status code:", response.status_code)
        print("Final URL: ", response.url)
        return False

    # Download the CSV file
    csv_response = session.get(csv_url)

    # Check if download was successful
    if csv_response.status_code == 200:
        # Ensure the directory exists
        directory = os.path.dirname(csv_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save the CSV file
        with open(csv_file_path, 'wb') as file:
            file.write(csv_response.content)
        print(f"File downloaded successfully at {csv_file_path}")
        return True
    else:
        print("Failed to download file.")
        return False

def uploadCSVtoGsheet(path_to_credentials,sheet_name,csv_file_path):
    try:
        warnings.filterwarnings("ignore")
        
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']

        # Add service account file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_credentials, scope)

        print("Authorizing Oauth Credentials...")
        client = gspread.authorize(credentials)

        print("Opening Google Sheet...")
        sheet = client.open(sheet_name).sheet1

        with open(csv_file_path, 'r', encoding='UTF-8', errors='replace') as file:
            file_content = file.read()

        # Replace smart quotes and other problematic characters
        file_content = file_content.replace('“', '"').replace('”', '"')
        file_content = file_content.replace("‘", "'").replace("’", "'")

        print("Loading CSV into Pandas DataFrame...")
        data = pd.read_csv(StringIO(file_content))

        print("Replacing overflowing and values...")
        # Replace inf and -inf with the maximum and minimum float values respectively
        data = data.replace([np.inf, -np.inf], [np.finfo(np.float64).max, np.finfo(np.float64).min])

        print("Replacing NaN values with string...")
        # Replace NaN with a string
        data = data.fillna('NaN')

        print("Importing CSV to Google Sheet...")
        sheet.update([data.columns.values.tolist()] + data.values.tolist())
        
        print("Script ran successfully...")
        return True

    except Exception as ex:
        print("An error occurred:")
        print(type(ex).__name__)
        print(ex)
        return False

def main():
    login_url = 'https://portal.sensetel.uk/site/login'
    
    sensetel_credentials = {
        'Username': os.environ.get('SENSETEL_USERNAME'),
        'Password': os.environ.get('SENSETEL_PASSWORD')
    }

    csv_url = 'https://portal.sensetel.uk/admin/voice_note_export' # Website download link
    csv_file_path = 'voicenotes/voice_notes.csv' # Server csv save path

    path_to_credentials = 'meta-aura-391914-6efae5df6f97.json' # Gsheet service account json
    sheet_name = "Recent Voice Notes - portal.verenigma.com" # Name of Gsheet
    
    # Execute download and then upload if download was successful
    if downloadCSV(login_url,sensetel_credentials,csv_url,csv_file_path):
        uploadCSVtoGsheet(path_to_credentials,sheet_name,csv_file_path)

if __name__ == '__main__':
    main()