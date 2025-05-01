import json
import os

SETTINGS_FILE = 'settings/settings.json'
PROJECTS_MAX_HISTORY = 5

class HistoryModel:
    def __init__(self):
        pass

    def get_last_projects(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                return settings.get('lastProjects', [])
            except:
                return []
        return []

    def update_last_project(self, directory):
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
            except:
                settings = {}
        settings['last_project_dir'] = directory
        last_projects = settings.get('lastProjects', [])
        if directory in last_projects:
            last_projects.remove(directory)
        last_projects.insert(0, directory)
        settings['lastProjects'] = last_projects[:PROJECTS_MAX_HISTORY]
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def get_last_project_directory(self):
        home_directory = os.path.expanduser('~')
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                return settings.get('last_project_dir', home_directory)
            except:
                return home_directory
        return home_directory
