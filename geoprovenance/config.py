import json
import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

# Define the directory for config within the user's home directory
APP_CONFIG_DIR = os.path.expanduser("~/.geoprovenance")
DEFAULT_CONFIG_PATH = os.path.join(APP_CONFIG_DIR, "config.json")
# Default values remain relative for the default config content
DEFAULT_DOWNLOAD_DIR = ""
DEFAULT_METADATA_FILE = "metadata.json"


def expand_path(path):
    """Expands relative paths like ~ to their absolute equivalents."""
    return os.path.expanduser(os.path.expandvars(path))


def load_config(config_path=DEFAULT_CONFIG_PATH, allow_unset=False):
    """Loads configuration from a JSON file in the user's home directory."""
    # Ensure the application config directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

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
            f"Configuration file {config_path} not found. Creating a new configuration file."
        )
        path = prompt(
            "Enter the path to the download directory: ", completer=PathCompleter()
        )
        path = os.path.abspath(path)  # Expand relative paths to absolute paths
        # Create a default config file with an empty download_directory
        config_data = {"download_directory": path}
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)

    # Ensure essential keys exist, using defaults if necessary
    config = {
        "download_directory": config_data.get(
            "download_directory", DEFAULT_DOWNLOAD_DIR
        ),
    }

    # Check if the download directory is set, unless explicitly allowed to be unset
    if config["download_directory"] == DEFAULT_DOWNLOAD_DIR and not allow_unset:
        raise ValueError(
            "Download directory is not set. Please set it using 'geoprovenance config --dir'."
        )

    # Ensure metadata.json exists in the download directory if the path is set
    if config["download_directory"]:
        metadata_file = os.path.join(config["download_directory"], "metadata.json")
        if not os.path.exists(metadata_file):
            os.makedirs(config["download_directory"], exist_ok=True)
            with open(metadata_file, "w") as f:
                json.dump([], f, indent=4)  # Initialize with an empty list
    # Ensure the tmp directory exists in the download directory 
    if config["download_directory"]:
        tmp_dir = os.path.join(config["download_directory"], "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)
            print(f"Temporary directory created at {tmp_dir}")

    return config


def get_default_config_content():
    """Returns the default configuration content as a JSON string."""
    default_config = {
        "download_directory": DEFAULT_DOWNLOAD_DIR,
        "metadata_file": DEFAULT_METADATA_FILE,
    }
    return json.dumps(default_config, indent=4)


def update_config(new_config, config_path=DEFAULT_CONFIG_PATH):
    """Updates the configuration file with new values."""
    # Load the existing configuration
    config = load_config(config_path, allow_unset=True)

    # Update the configuration with new values
    config.update(new_config)

    # Ensure the application config directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Write the updated configuration back to the file
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"Configuration updated and saved to {config_path}")


# Example of how to create a default config if needed elsewhere
# config_dir_to_check = os.path.expanduser("~/.geoprovenance")
# default_config_file_to_check = os.path.join(config_dir_to_check, "config.json")
# if not os.path.exists(default_config_file_to_check):
#     os.makedirs(config_dir_to_check, exist_ok=True) # Ensure directory exists
#     with open(default_config_file_to_check, 'w') as f:
#         f.write(get_default_config_content())
#     print(f"Created default configuration file: {default_config_file_to_check}")
