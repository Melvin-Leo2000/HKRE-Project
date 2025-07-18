import os, time
from dotenv import load_dotenv
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import base64
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow



load_dotenv()

MAX_RETRIES = 2

if "GOOGLE_CREDS_JSON" in os.environ:
        decoded_json = base64.b64decode(os.environ["GOOGLE_CREDS_JSON"])
        with open("service_account.json", "wb") as f:
            f.write(decoded_json)
        cred_path = "service_account.json"
else:
    raise EnvironmentError("GOOGLE_CREDS_JSON not found in environment variables")



def google_auth():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents'
    ]

    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)

    # Set up clients
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key("1zFijFdFYINqrNm3HJAPp8g86orQuOZuHxbPTNfPLZK8")
    docs = build('docs', 'v1', credentials=creds)

    return spreadsheet, docs


def get_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # Load credentials.json from base64 env
    if "GOOGLE_OAUTH_JSON" not in os.environ:
        raise EnvironmentError("GOOGLE_OAUTH_JSON not found in environment variables")

    decoded_json = base64.b64decode(os.environ["GOOGLE_OAUTH_JSON"])
    with open("oauth_credentials.json", "wb") as f:
        f.write(decoded_json)

    # Load token.pickle from env if not on disk
    if not os.path.exists("token.pickle") and "GOOGLE_TOKEN_PICKLE_B64" in os.environ:
        decoded_token = base64.b64decode(os.environ["GOOGLE_TOKEN_PICKLE_B64"])
        with open("token.pickle", "wb") as f:
            f.write(decoded_token)

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)




def get_devm(spreadsheet, version):

    # Check what version is it and open the sheet accordingly
    if version == "t18m":
        sheet = spreadsheet.worksheet("devm t18m")
    else:
        sheet = spreadsheet.worksheet("devm non-t18m")

    # Retrieve all values from devm
    values = sheet.get_all_values()
    df = pd.DataFrame(values)
    df = df.iloc[1:, 2:]
    return df, sheet 


def number_to_column_name(n):
    result = []
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result.append(chr(65 + remainder))  # 65 = 'A'
    return ''.join(reversed(result))


def insert_new_data(sheet, devm):   
    # Inserting a new row for new data 
    new_row = [""] * sheet.col_count  
    sheet.insert_row(new_row, 2)  

    # Inserting the new data from devm website
    # Attempt the update with retries

    row_data = list(devm.values())

    # For loop to catch errors 
    end_col_index = 3 + len(row_data) - 1
    end_col = number_to_column_name(end_col_index)
    sheet.update([row_data], f"C2:{end_col}2")

    # Insert the Date of last update and check if there is a duplicate
    sheet.update("A2", [["=COUNTIFS($C$1:$C, C2, $E$1:$E, E2, $F$1:$F, F2) > 1"]], value_input_option="USER_ENTERED")
    today_date = datetime.today().strftime('%d/%m/%Y') 
    sheet.update("B2", [[today_date]], value_input_option="USER_ENTERED")


def update_log(docs, text):
    
    # Document ID extracted from the provided link
    document_id = "1Exn8sDkWz_FPK_dlPZNJonNVTkojyoGHbK3yg5EX_WE"
    
    # Fetch the document to determine the end index
    document = docs.documents().get(documentId=document_id).execute()
    content = document.get('body', {}).get('content', [])

    # Find the end index of the document
    end_index = None
    if content:
        last_element = content[-1]
        end_index = last_element.get('endIndex', 1)  
    
    # Nothing was written in the logs yet
    if end_index is None:
        end_index = 2

    # Update content in the document
    requests = [
        {
            'insertText': {
                'location': {
                    'index': end_index - 1, 
                },
                'text': f"{text}"
            }
        }
    ]
    
    # Execute the batch update
    result = docs.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}
    ).execute()



def upload_file_to_gdrive(file_path, filename, drive_service, parent_folder_id=None):
    file_metadata = {'name': filename}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    media = MediaFileUpload(file_path, mimetype='application/pdf')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"Uploaded: {filename} (ID: {file.get('id')})")




def create_drive_folder(folder_name, parent_id=None):

    creds = Credentials.from_service_account_file(
        cred_path,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)

    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]

    folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()

    return folder['id']

