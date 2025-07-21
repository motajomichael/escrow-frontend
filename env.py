import os
import tomli

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')

with open(CONFIG_PATH, 'rb') as f:
    config = tomli.load(f)

active_env = config["env"]["active"]
API_BASE = config["api"][active_env]["url"]
