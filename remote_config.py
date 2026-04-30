import json
import os

CONFIG_FILE = 'cfg.json'

def load_local_config():
    if os.path.exists(CONFIG_FILE):
        return True
    return False

def save_local_config(config_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    return True

# 屏蔽所有远程接口
def init_remote_config(server_url=None): return load_local_config()
def is_remote_config_loaded(): return True