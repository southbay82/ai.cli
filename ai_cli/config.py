import os
import json
from pathlib import Path

# Define paths
HOME_DIR = Path.home()
GLOBAL_CONFIG_DIR = HOME_DIR / ".ai.cli"
PROJECT_CONFIG_DIR_NAME = ".ai.cli"

# Resource directories
RESOURCE_DIRS = ["profiles", "rules", "mcps", "workflows"]

class Config:
    def __init__(self):
        self.global_config_path = GLOBAL_CONFIG_DIR / "config.json"
        self.project_config_path = self._find_project_config()

        self.global_config = self._load_config(self.global_config_path)
        self.project_config = self._load_config(self.project_config_path)

    def _find_project_config(self):
        # Search for .ai.cli directory in parent directories
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / PROJECT_CONFIG_DIR_NAME).is_dir():
                return current_dir / PROJECT_CONFIG_DIR_NAME / "config.json"
            current_dir = current_dir.parent
        return None

    def _load_config(self, path):
        if path and path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def get(self, key, default=None):
        # Project config overrides global config
        return self.project_config.get(key, self.global_config.get(key, default))

# Initialize and create directories if they don't exist
def init_config():
    GLOBAL_CONFIG_DIR.mkdir(exist_ok=True)
    for resource_dir in RESOURCE_DIRS:
        (GLOBAL_CONFIG_DIR / resource_dir).mkdir(exist_ok=True)
    (GLOBAL_CONFIG_DIR / "backups").mkdir(exist_ok=True)

    # Create a default global config if it doesn't exist
    config_path = GLOBAL_CONFIG_DIR / "config.json"
    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump({"git_repo_url": ""}, f, indent=4)

    return Config()

config = init_config()
