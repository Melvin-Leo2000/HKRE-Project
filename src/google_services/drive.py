"""
Google Drive Operations Module
Handles file uploads and folder creation in Google Drive
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .auth import _load_creds


def create_drive_folder(folder_name, parent_id=None):
    """
    Create a folder in Google Drive.
    
    Args:
        folder_name: Name of the folder to create
        parent_id: Optional parent folder ID
    
    Returns:
        Folder ID string
    """
    creds = _load_creds()
    drive = build("drive", "v3", credentials=creds)
    body = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        body["parents"] = [parent_id]
    folder = drive.files().create(body=body, fields="id").execute()
    return folder["id"]


def upload_file_to_gdrive(file_path, filename, drive_service, parent_folder_id=None):
    """
    Upload a file to Google Drive.
    
    Args:
        file_path: Local path to the file
        filename: Name for the file in Drive
        drive_service: Google Drive service object
        parent_folder_id: Optional parent folder ID
    """
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

