import os
import json
from mvn_scan.config.constants import (PATH_FOLDER, CONFIG_FILE, CONFIG_API_SONATYPE)


class config_helper:

    def __init__(self):
        self.config_path = self.get_config_path()
        self.config = self.initialize_config()


    def get_config_path(self):
        home = os.path.expanduser("~")
        config_dir = os.path.join(home, PATH_FOLDER)
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, CONFIG_FILE)


    def initialize_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(CONFIG_API_SONATYPE)
            return CONFIG_API_SONATYPE.copy()

        config = self.load_config()

        #Validar y completar campos faltantes
        updated = False
        for key, value in CONFIG_API_SONATYPE.items():
            if key not in config:
                config[key] = value
                updated = True

        #Validar tipos básicos
        if not isinstance(config.get("api_token"), str):
            config["api_token"] = CONFIG_API_SONATYPE["api_token"]
            updated = True

        #Guardar si hubo cambios
        if updated:
            self.save_config(config)

        return config


    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}


    def save_config(self, data: dict):
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=4)


    def get_api_token(self, cli_token=None):
        api_token = cli_token or self.config.get("api_token")

        if not api_token:
            raise ValueError(
                "No API key found. Use --api-token or configure with --set-api-token"
            )

        return api_token


    def update_config(self, new_data: dict):
        self.config.update(new_data)
        self.save_config(self.config)