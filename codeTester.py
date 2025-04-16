from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from scripts.mapManager import map_manager
import os
import json

#map_manager.download_index()

# FILENAME = "00001.json"  # Change this to any level file you want to upload
# LOCAL_PATH = os.path.join("data", "maps", FILENAME)
# LEVELS_FOLDER_ID = "1rNiGJA27XI1kYgS5aLv2SmuamZvWvwOn"  # Replace this with your actual Drive folder ID

# # === AUTH ===
# gauth = GoogleAuth()
# gauth.LoadCredentialsFile("credentials.json")

# if not gauth.credentials or gauth.access_token_expired:
#     gauth.LocalWebserverAuth()
#     gauth.SaveCredentialsFile("credentials.json")

# drive = GoogleDrive(gauth)

# # === UPLOAD ===
# file_metadata = {
#     'title': FILENAME,
#     'parents': [{'id': LEVELS_FOLDER_ID}]
# }
# file_to_upload = drive.CreateFile(file_metadata)
# file_to_upload.SetContentFile(LOCAL_PATH)
# file_to_upload.Upload()

# print(f"✅ Uploaded {LOCAL_PATH} as {FILENAME} to Google Drive.")
# print(f"🔗 View online: https://drive.google.com/file/d/{file_to_upload['id']}/view")

