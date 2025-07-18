import os
import json
from pathlib import Path

# Define paths
HOME_DIR = Path.home()
PROJECT_ROOT = Path(__file__).parent.parent
GLOBAL_CONFIG_DIR = HOME_DIR / ".ai.cli"
PROJECT_CONFIG_DIR_NAME = ".ai.cli"

# Content directories
CONTENT_DIR = PROJECT_ROOT / "content"
RULES_DIR = CONTENT_DIR / "rules"
GLOBAL_RULES_DIR = CONTENT_DIR / "global"
PROJECT_RULES_DIR = CONTENT_DIR / "project"
AMAZONQ_PROFILES_DIR = CONTENT_DIR / "amazonq_profiles"
WINDSURF_WORKFLOWS_DIR = CONTENT_DIR / "windsurf_workflows"

# Resource directories (legacy, will be deprecated)
RESOURCE_DIRS = ["profiles", "rules", "mcps", "workflows"]

# Tool configuration directories
TOOL_CONFIGS = {
    "q-cli": {
        "rules_dir": AMAZONQ_PROFILES_DIR,
        "workflows_dir": WINDSURF_WORKFLOWS_DIR,
        "profiles_dir": AMAZONQ_PROFILES_DIR
    },
    "windsurf": {
        "rules_dir": GLOBAL_RULES_DIR,
        "workflows_dir": WINDSURF_WORKFLOWS_DIR,
        "profiles_dir": HOME / ".windsurf"
    },
    "gemini": {
        "rules_dir": GLOBAL_RULES_DIR,
        "workflows_dir": WINDSURF_WORKFLOWS_DIR,
        "profiles_dir": HOME / ".gemini"
    }
}

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

def ensure_directories():
    """Ensure all required directories exist."""
    # Create global config directory
    GLOBAL_CONFIG_DIR.mkdir(exist_ok=True)
    
    # Create content directories
    for directory in [
        CONTENT_DIR, RULES_DIR, GLOBAL_RULES_DIR, 
        PROJECT_RULES_DIR, AMAZONQ_PROFILES_DIR, WINDSURF_WORKFLOWS_DIR
    ]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create legacy resource directories (for backward compatibility)
    for resource_dir in RESOURCE_DIRS:
        (GLOBAL_CONFIG_DIR / resource_dir).mkdir(exist_ok=True)
    
    # Create backups directory
    (GLOBAL_CONFIG_DIR / "backups").mkdir(exist_ok=True)

# Initialize and create directories if they don't exist
def init_config():
    ensure_directories()
    
    # Create a default global config if it doesn't exist
    config_path = GLOBAL_CONFIG_DIR / "config.json"
    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump({
                "git_repo_url": "",
                "content_dirs": {
                    "rules": str(RULES_DIR),
                    "global_rules": str(GLOBAL_RULES_DIR),
                    "project_rules": str(PROJECT_RULES_DIR),
                    "amazonq_profiles": str(AMAZONQ_PROFILES_DIR),
                    "windsurf_workflows": str(WINDSURF_WORKFLOWS_DIR)
                }
            }, f, indent=4)

    return Config()

config = init_config()
