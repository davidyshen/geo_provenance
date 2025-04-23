import os
import json
from .config import load_config


def find_dataset_path(dataset_name, config):
    """Finds the full path of a dataset by name in the metadata file."""
    metadata_file = os.path.join(config["download_directory"], "metadata.json")

    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found at {metadata_file}")

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    dataset = next(
        (entry for entry in metadata if entry["data_name"] == dataset_name),
        None,
    )

    if dataset:
        return os.path.join(
            config["download_directory"], dataset["downloaded_filename"]
        )

    raise ValueError(f"Dataset with name '{dataset_name}' not found in metadata.")


def find(dataset_name):
    """Returns the path of the data as stored and ingested based on the dataset name."""
    config = load_config()  # Load the configuration
    return find_dataset_path(dataset_name, config)
