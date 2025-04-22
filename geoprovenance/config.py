import json
import os

# Define the directory for config within the user's home directory
APP_CONFIG_DIR = os.path.expanduser("~/.geoprovenance")
DEFAULT_CONFIG_PATH = os.path.join(APP_CONFIG_DIR, "config.json")
# Default values remain relative for the default config content
DEFAULT_DOWNLOAD_DIR = "downloads"
DEFAULT_METADATA_FILE = "metadata.json"


def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Loads configuration from a JSON file in the user's home directory."""
    # Ensure the application config directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    config_dir = os.path.dirname(config_path)  # Get directory of config file

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                print(
                    f"Warning: Error decoding {config_path}. Using default configuration."
                )
                config_data = {}
    else:
        print(
            f"Warning: Configuration file {config_path} not found. Using default configuration."
        )
        # Optionally create a default config file here if it doesn't exist
        # with open(config_path, 'w') as f:
        #     f.write(get_default_config_content())
        # print(f"Created default configuration file: {config_path}")
        config_data = {}  # Start with empty if not creating default automatically

    # Resolve paths relative to the config file directory
    download_directory = os.path.join(
        config_dir, config_data.get("download_directory", DEFAULT_DOWNLOAD_DIR)
    )
    metadata_file = os.path.join(
        config_dir, config_data.get("metadata_file", DEFAULT_METADATA_FILE)
    )

    # Ensure essential keys exist, using defaults if necessary
    config = {
        "download_directory": download_directory,
        "metadata_file": metadata_file,
        "config_directory": config_dir,  # Store config dir for potential later use
    }

    # Create download directory if it doesn't exist
    os.makedirs(config["download_directory"], exist_ok=True)

    return config


def get_default_config_content():
    """Returns the default configuration content as a JSON string."""
    default_config = {
        "download_directory": DEFAULT_DOWNLOAD_DIR,
        "metadata_file": DEFAULT_METADATA_FILE,
    }
    return json.dumps(default_config, indent=4)


# Example of how to create a default config if needed elsewhere
# config_dir_to_check = os.path.expanduser("~/.geoprovenance")
# default_config_file_to_check = os.path.join(config_dir_to_check, "config.json")
# if not os.path.exists(default_config_file_to_check):
#     os.makedirs(config_dir_to_check, exist_ok=True) # Ensure directory exists
#     with open(default_config_file_to_check, 'w') as f:
#         f.write(get_default_config_content())
#     print(f"Created default configuration file: {default_config_file_to_check}")
