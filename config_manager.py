import json
import os

class ConfigManager:
    PLACEHOLDER_KEYS = ["YOUR_GOOGLE_API_KEY", "YOUR_GOOGLE_CX", "YOUR_BRAVE_API_KEY", ""]

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
            "api_preference": "google"
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

    def set(self, key_path, value):
        """Set a config value using dot-notation path (e.g. 'auth.google_api_key')."""
        keys = key_path.split('.')
        target = self.config
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value

    def is_first_run(self):
        """Returns True if API keys are still placeholders or empty."""
        google_key = self.get('auth.google_api_key', '')
        brave_key = self.get('auth.brave_api_key', '')
        return (google_key in self.PLACEHOLDER_KEYS and
                brave_key in self.PLACEHOLDER_KEYS)

    def get_keywords_list(self):
        """Read keywords from file and return as a list."""
        kw_file = self.get('paths.keywords_file', 'search_keywords.txt')
        if os.path.exists(kw_file):
            try:
                with open(kw_file, 'r') as f:
                    content = f.read()
                    return [k.strip() for k in content.split(',') if k.strip()]
            except Exception:
                pass
        return []

    def save_keywords_list(self, keywords):
        """Save a list of keywords to the keywords file."""
        kw_file = self.get('paths.keywords_file', 'search_keywords.txt')
        try:
            with open(kw_file, 'w') as f:
                f.write(','.join(keywords))
        except Exception as e:
            print(f"Error saving keywords: {e}")
