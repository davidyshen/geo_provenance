import os
import json
from .config import load_config


def load(dataset_name):
    """Returns the path of the data as stored and ingested based on the dataset name."""
    config = load_config()  # Load the configuration
    metadata_file = config["metadata_file"]

    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found at {metadata_file}")

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    for entry in metadata:
        if entry["data_name"] == dataset_name:
            return os.path.join(
                config["download_directory"], entry["downloaded_filename"]
            )

    raise ValueError(f"Dataset with name '{dataset_name}' not found in metadata.")
