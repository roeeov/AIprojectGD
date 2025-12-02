import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import hashlib
from scripts.tilemap import tile_map

class MapManager:

    def _initialize(self):

        self.editor_levels_json = {}
        self.ai_levels_json = {}
        self.current_map_id = ''

        self.LEVELS_FOLDER_ID = "1rNiGJA27XI1kYgS5aLv2SmuamZvWvwOn"
        self.drive = self.auth_drive()

        self.update_map_dict()
        self.download_index()

    def auth_drive(self):
        from pydrive2.auth import GoogleAuth
        from pydrive2.drive import GoogleDrive

        gauth = GoogleAuth()       # Auto-loads settings.yaml
        gauth.ServiceAuth()        # Uses service account from settings.yaml
        return GoogleDrive(gauth)

    def postMap(self, id):
        if not id.startswith("--"):
            # Upload a new level
            online_id = self.generateOnlineId()
            self.updateMapInfo(id=online_id)
            self.upload_level(online_id)

            new_id = '--' + online_id
            self.current_map_id = online_id
            self.updateMapInfo(id=new_id)

        else:
            # Update existing online level
            online_id = id[2:]  # Remove "--"
            staging_path = self.getMapPath(id)
            final_path = self.getMapPath(online_id)

            if not os.path.exists(staging_path):
                print(f"❌ Staging map {id} not found.")
                return

            # Load staging content
            with open(staging_path, "r", encoding="utf-8") as f:
                staging_data = json.load(f) 

            # If the final file doesn't exist, create it using staging data
            if os.path.exists(final_path):
                with open(final_path, "r", encoding="utf-8") as f:
                    final_data = json.load(f)
            else:
                final_data = {}

            # Copy all contents from staging → final, except 'id'
            final_data["info"] = staging_data.get("info", {})
            final_data["info"]["id"] = online_id  # Force correct ID
            final_data["tilemap"] = staging_data.get("tilemap", {})
            final_data["offgrid"] = staging_data.get("offgrid", [])

            # Save updated level
            with open(final_path, "w", encoding="utf-8") as f:
                json.dump(final_data, f, indent=4)

            print(f"🔁 Synced content from {id} → {online_id} (ID preserved)")
            self.upload_level(online_id)

    # needs to change
    def generateOnlineId(self):
        online_levels = self.list_online_levels()
        try:
            new_id = int(sorted(online_levels.keys(), reverse=True)[0]) + 1
        except IndexError:
            new_id = 1
        new_id = str(new_id).zfill(5)
        return new_id
    
    def update_map_dict(self):

        self.editor_levels_json = {}

        folder_path = "data/maps"
        for filename in sorted(os.listdir(folder_path), reverse=True):
            if filename.endswith(".json") and filename.startswith("-"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    map_id = data["info"]["id"]
                    self.editor_levels_json[map_id] = data
                    
    
    def update_ai_map_dict(self):

        self.ai_levels_json = {}

        folder_path = "data/ai_maps"
        for filename in sorted(os.listdir(folder_path), reverse=True):
            if filename.endswith(".json") and filename.startswith("AI"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    map_id = data["info"]["id"]
                    self.ai_levels_json[map_id] = data
                    


    def getEditorMapsDict(self):
        self.update_map_dict()
        return self.editor_levels_json
    
    def getAIMapsDict(self):
        self.update_ai_map_dict()
        return self.ai_levels_json
    
    def updateMapInfo(self, creator = None, name = None, difficulty = None, id = None):
        file_path = f'data/maps/{self.current_map_id}.json'

        with open(file_path, "r") as file:
            data = json.load(file)

        if creator: data["info"]["creator"] = creator
        if name: data["info"]["name"] = name
        if difficulty: data["info"]["difficulty"] = difficulty
        if id: 
            data["info"]["id"] = id
            new_file_path = self.getMapPath(id)
            os.rename(file_path, new_file_path)
            file_path = new_file_path
            self.current_map_id = ''

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4) 

        self.update_map_dict()

    # use more
    def getMapPath(self, id = None, isAi = False):
        map_id = self.current_map_id if id is None else id
        return f"data/ai_maps/{map_id}.json" if isAi else f"data/maps/{map_id}.json"

    def loadMap(self, isAi = False):
        map_path = self.getMapPath(isAi=isAi)
        tile_map.load(map_path)

    def createNewMap(self):
        new_map_id = self.generateEditorId()
        new_map_data = {
            "info": {
                "name": "unnamed",
                "creator": "not entered",
                "difficulty": "NA",
                "id": new_map_id
            },
            "tilemap": {},
            "offgrid": []
        }

        file_path = f'data/maps/{new_map_id}.json'
        with open(file_path, 'w') as f:
            json.dump(new_map_data, f, indent=4)  # indent=4 makes it pretty

        # self.update_map_dict()
        self.setMap(new_map_id)

    def generateEditorId(self):
        editorDict = self.getEditorMapsDict().keys()
        editorDict = filter(lambda x: not x.startswith('--'), editorDict)
        try:
            new_id = int(tuple(editorDict)[0][1:]) + 1
        except IndexError:
            new_id = 1
        new_id = '-' + str(new_id).zfill(5)
        return new_id

    def getMapInfo(self, id):
        if id[0] == '-':
            return self.editor_levels_json[id]["info"]
        else:
            with open("index.json", "r") as f:
                index = json.load(f)
            return index[id]
    
    def getAIMapInfo(self, id):
            return self.ai_levels_json[id]["info"]
        
    def setMap(self, id):
        self.current_map_id = id

    def download_index(self, local_path="index.json"):
        file_list = self.drive.ListFile({
            'q': "title='index.json' and trashed=false"
        }).GetList()

        if file_list:
            file = file_list[0]
            file.GetContentFile(local_path)
            print("✅ Downloaded index.json")
        else:
            print("❌ index.json not found on Drive.")

    def upload_level(self, map_id):

        level_path = self.getMapPath(map_id)

        # Upload level file
        file_metadata = {
            'title': f"{map_id}.json",
            'parents': [{'id': self.LEVELS_FOLDER_ID}]
        }
        file = self.drive.CreateFile(file_metadata)
        file.SetContentFile(level_path)
        file.Upload()
        print(f"✅ Uploaded level {map_id}")

        # Step 2: Download existing index.json
        self.download_index()

        # Step 3: Update it
        with open(level_path, "r") as f:
            level_data = json.load(f)
        with open("index.json", "r") as f:
            index = json.load(f)

        info = level_data.get("info", {})
        map_id = info.get("id")
        # Remove 'id' from the info dict before saving to index
        info_without_id = {k: v for k, v in info.items() if k != "id"}
        index[map_id] = info_without_id

        with open("index.json", "w") as f:
            json.dump(index, f, indent=2)

        # Step 4: Re-upload index.json to Drive
        self.upload_index()

    def upload_index(self):
        existing = self.drive.ListFile({
            'q': f"title='index.json' and '{self.LEVELS_FOLDER_ID}' in parents and trashed=false"
        }).GetList()

        if existing:
            file = existing[0]  # Update the existing file
            print("♻️ Updating existing index.json")
        else:
            file = self.drive.CreateFile({
                'title': 'index.json',
                'parents': [{'id': self.LEVELS_FOLDER_ID}]
            })
            print("📄 Uploading new index.json")

        file.SetContentFile("index.json")
        file.Upload()
        print("✅ index.json uploaded/updated on Drive")


    def download_level(self, map_id, local_folder="data/maps"):
        filename = f"{map_id}.json"

        # Search for the level file on Google Drive
        file_list = self.drive.ListFile({
            'q': f"title='{filename}' and trashed=false"
        }).GetList()

        if not file_list:
            print(f"❌ Level {map_id} not found on Drive.")
            return False

        # Make sure local folder exists
        os.makedirs(local_folder, exist_ok=True)

        # Download the file
        level_file = file_list[0]
        save_path = os.path.join(local_folder, filename)
        level_file.GetContentFile(save_path)

        print(f"✅ Downloaded level {map_id} to {save_path}")
        return True
    
    def delete_level(self, map_id):
        filename = f"{map_id}.json"
        file_list = self.drive.ListFile({
            'q': f"title='{filename}' and '{self.LEVELS_FOLDER_ID}' in parents and trashed=false"
        }).GetList()

        if not file_list:
            print(f"❌ Level {map_id} not found on Drive.")
            return

        file_list[0].Delete()
        print(f"🗑️ Deleted level {map_id} from Drive.")

        # Remove from index
        self.download_index()
        with open("index.json", "r") as f:
            index = json.load(f)
        if map_id in index:
            del index[map_id]
            with open("index.json", "w") as f:
                json.dump(index, f, indent=2)
            self.upload_index()
            print(f"🗑️ Removed {map_id} from index.json")
    
    def list_online_levels(self):
        self.download_index()
        with open("index.json", "r") as f:
            index = json.load(f)
        return index
    
    def hash_file(self, path):
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def sync_level(self, map_id, local_folder="data/maps"):
        filename = f"{map_id}.json"
        local_path = os.path.join(local_folder, filename)

        # Step 1: Check if file exists locally
        if not self.isMapLoaded(map_id):
            print(f"📥 Level {map_id} not found locally. Downloading...")
            return self.download_level(map_id)

        # Step 2: Look for the file on Drive
        file_list = self.drive.ListFile({
            'q': f"title='{filename}' and '{self.LEVELS_FOLDER_ID}' in parents and trashed=false"
        }).GetList()

        if not file_list:
            print(f"❌ Level {map_id} not found on Drive.")
            return False

        remote_file = file_list[0]

        # Step 3: Download Drive version to temp file
        temp_path = os.path.join(local_folder, f"__temp_{filename}")
        remote_file.GetContentFile(temp_path)

        # Step 4: Compare hashes
        local_hash = self.hash_file(local_path)
        remote_hash = self.hash_file(temp_path)

        if local_hash != remote_hash:
            print(f"🔄 Level {map_id} differs. Replacing local file...")
            os.replace(temp_path, local_path)
            return True
        else:
            print(f"✅ Level {map_id} is up to date.")
            os.remove(temp_path)
            return False
        
    def isMapLoaded(self, map_id):
        local_path = f'data/maps/{map_id}.json'
        return os.path.exists(local_path)


map_manager = MapManager()
