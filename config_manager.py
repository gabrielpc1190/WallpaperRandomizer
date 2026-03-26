import json
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self):
        return {
            "auth": {
                "google_api_key": "",
                "google_cx": "",
                "brave_api_key": ""
            },
            "intervals": {
                "download_minutes": 60,
                "rotate_minutes": 15
            },
            "system": {
                "cleanup_days_old": 7
            },
            "paths": {
                "download_dir": "DownloadedWallpapers",
                "keywords_file": "search_keywords.txt"
            },
            "api_preference": "google" # or "brave"
        }

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self._deep_update(self.config, user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _deep_update(self, base_dict, update_dict):
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def get(self, key_path, default=None):
        keys = key_path.split('.')
        rv = self.config
        for key in keys:
            if isinstance(rv, dict) and key in rv:
                rv = rv[key]
            else:
                return default
        return rv
