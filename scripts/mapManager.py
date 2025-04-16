import json
import os
from scripts.tilemap import tile_map

class MapManager:

    def __init__(self):

        self.online_levels_json = {}
        self.editor_levels_json = {}
        self.current_map_id = ''
        self.update_map_dict()

    def update_map_dict(self):

        self.online_levels_json = {}
        self.editor_levels_json = {}

        folder_path = "data/maps"
        for filename in sorted(os.listdir(folder_path), reverse=True):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    map_id = data["info"]["id"]
                    if map_id[0] == '-':
                        self.editor_levels_json[map_id] = data
                    else:
                        self.online_levels_json[map_id] = data

    def getMapPath(self):
        return f"data/maps/{self.current_map_id}.json"

    def getOnlineMapsDict(self):
        self.update_map_dict()
        return self.online_levels_json
    
    def getEditorMapsDict(self):
        self.update_map_dict()
        return self.editor_levels_json

    def setMap(self, id):
        self.current_map_id = id

    def getMapInfo(self, id):
        if id[0] == '-':
            return self.editor_levels_json[id]["info"]
        else:
            return self.online_levels_json[id]["info"]
        
    def updateMapInfo(self, creator = None, name = None, difficulty = None, id = None):
        file_path = f'data/maps/{self.current_map_id}.json'

        with open(file_path, "r") as file:
            data = json.load(file)

        if creator: data["info"]["creator"] = creator
        if name: data["info"]["name"] = name
        if difficulty: data["info"]["difficulty"] = difficulty
        if id: 
            data["info"]["id"] = id
            new_file_path = f'data/maps/{id}.json'
            os.rename(file_path, new_file_path)
            file_path = new_file_path
            self.current_map_id = ''

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4) 

        self.update_map_dict()


    def loadMap(self):
        map_path = self.getMapPath()
        tile_map.load(map_path)

    def generateEditorId(self):
        editorDict = self.getEditorMapsDict()
        try:
            new_id = int(tuple(editorDict.keys())[0][1:]) + 1
        except IndexError:
            new_id = 1
        new_id = '-' + str(new_id).zfill(5)
        return new_id

    def generateOnlineId(self):
        onlineDict = self.getOnlineMapsDict()
        try:
            new_id = int(tuple(onlineDict.keys())[0]) + 1
        except IndexError:
            new_id = 1
        new_id = str(new_id).zfill(5)
        return new_id

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
                

map_manager = MapManager()
