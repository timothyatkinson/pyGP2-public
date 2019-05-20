import json

global_configs = -1

class Config:
    def __init__(self, path):
        self.path = path

def load_configs():
    global global_configs
    if global_configs == -1:
        configs = []
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = dir_path + "/config.json"
        with open(config_path, "r") as read_file:
            data = json.load(read_file)
            config_arr = data["configs"]
            for conf in config_arr:
                gp2_dir = conf["gp2_directory"]
                configs.append(Config(gp2_dir))
        global_configs = configs
    return global_configs

def get_config(index):
    return load_configs()[index]
