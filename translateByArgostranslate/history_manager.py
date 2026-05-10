import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, config_path, history_path):
        self.config_path = config_path
        self.history_path = history_path
        self.config = self.load_config()
        self.history = self.load_history()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"history_max_items": 3}

    def load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def add_history(self, source, translation, direction):
        max_items = self.config.get("history_max_items", 3)
        new_entry = {
            "id": datetime.now().isoformat(),
            "direction": direction,
            "source": source,
            "translation": translation
        }
        self.history.insert(0, new_entry)
        if len(self.history) > max_items:
            self.history = self.history[:max_items]
        self.save_history()

    def get_latest(self, n=None):
        if n is None:
            n = self.config.get("history_max_items", 3)
        return self.history[:n]

    def save_history(self):
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def clear_history(self):
        self.history = []
        self.save_history()
