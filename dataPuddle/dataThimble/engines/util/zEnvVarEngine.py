# Last modified: 2025-04-01 08:38:39
# Version: 0.0.33

import os
from dotenv import dotenv_values, load_dotenv


def get_os_env_vars(ENV_DIR):
    loaded_vars = {}

    for filename in os.listdir(ENV_DIR):
        filepath = os.path.join(ENV_DIR, filename)
        if filename.startswith(".dotEnv") and os.path.isfile(filepath):
            load_dotenv(dotenv_path=filepath, override=True)  # mods the os.environ

            env_vars = dotenv_values(filepath)  # Doesn't modify os.environ
            loaded_vars.update(env_vars)

    # Show what was loaded
    for key, value in loaded_vars.items():
        print(f"{key} = {value}")
    return loaded_vars
