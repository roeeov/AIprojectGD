from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Authenticate using saved credentials
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Step 1: Check if "levels" folder already exists
file_list = drive.ListFile({
    'q': "title='levels' and mimeType='application/vnd.google-apps.folder' and trashed=false"
}).GetList()

if file_list:
    folder = file_list[0]
    print(f'📁 "levels" folder already exists: {folder["title"]} (ID: {folder["id"]})')
else:
    # Step 2: Create the folder
    folder_metadata = {
        'title': 'levels',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    print(f'✅ Created "levels" folder (ID: {folder["id"]})')
