import requests
import os
import subprocess

#from memory_profiler import profile

import pandas as pd

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

def countCSVRows(csv_file_path):    
    result = subprocess.run(['wc', '-l', csv_file_path], stdout=subprocess.PIPE)
    total_csv_rows = int(result.stdout.decode().split()[0])
    print(f"Total rows in CSV file: {total_csv_rows}")
    return total_csv_rows


def find_last_filled_row(sheet, column='A'):
    chunk_size = 5000  # Define a suitable chunk size based on expected data size
    current_check = 1
    last_non_empty = 0  # To keep track of the last non-empty cell found

    while True:
        range_end = current_check + chunk_size - 1
        cell_list = sheet.range(f'{column}{current_check}:{column}{range_end}')
        # Track the index of the last non-empty cell in this chunk
        last_in_chunk = 0

        for i, cell in enumerate(cell_list):
            if cell.value.strip() != '':
                last_in_chunk = i + 1

        if last_in_chunk > 0:
            # Update last_non_empty based on the most recent non-empty cell found
            last_non_empty = current_check + last_in_chunk - 1
            current_check += chunk_size
        else:
            # If no non-empty cells were found in this chunk, and we have previously found non-empty cells
            break

    return last_non_empty

def uploadCSVtoGsheet(path_to_credentials, sheet_name, csv_file_path):
    try:
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        # Add service account file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_credentials, scope)

        print("Authorizing Oauth Credentials...")
        client = gspread.authorize(credentials)

        print("Opening Google Sheet...")
        sheet = client.open(sheet_name).sheet1
        print("Opened sheet before kill.")

        # Find the last row with data in the Google Sheet
        print("Determining the last row with data...")
        last_row = find_last_filled_row(sheet)
        #last_row = len(sheet.get_all_values())
        print(f"Starting import from row of GoogleSheet, {last_row + 1} in the CSV...")

        # Define chunk size and placeholders
        chunk_size = 5000
        na_values = ['-', '']  # Treat dashes and empty strings as NaN

        # Create an iterator to read the CSV in chunks starting from the specified row
        reader = pd.read_csv(csv_file_path, skiprows=range(1, last_row), chunksize=chunk_size,
                            na_values=na_values, keep_default_na=True, encoding='utf-8')
        
        print("Chunked CSV to reader...")

        for chunk in reader:
            chunk.fillna('NaN', inplace=True)  # Replace NaNs with 'NaN' string
            # Upload each processed chunk to the Google Sheet
            data_to_upload = chunk.values.tolist()
            sheet.append_rows(data_to_upload)
            print(f"Uploaded {len(data_to_upload)} rows to the Google Sheet.")

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
        countCSVRows(csv_file_path)
        uploadCSVtoGsheet(path_to_credentials,sheet_name,csv_file_path)

if __name__ == '__main__':
    main()