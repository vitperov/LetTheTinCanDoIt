import os
import json

SETTINGS_FILE = 'settings/settings.json'
REQUESTS_MAX_HISTORY = 10

class RequestHistoryModel:
    def __init__(self):
        pass

    def get_last_requests(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                return settings.get('requestHistory', [])
            except:
                return []
        return []

    def update_request_history(self, request_text):
        if not request_text:
            return
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
            except:
                settings = {}
        history = settings.get('requestHistory', [])
        if request_text in history:
            history.remove(request_text)
        history.insert(0, request_text)
        history = history[:REQUESTS_MAX_HISTORY]
        settings['requestHistory'] = history
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
