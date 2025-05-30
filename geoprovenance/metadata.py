import json
import os
from datetime import datetime
from .config import load_config

def load_metadata(metadata_file):
    """Loads metadata from the specified JSON file."""
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"Warning: Error decoding {metadata_file}. Starting with empty metadata."
                )
                return []
    else:
        return []


def save_metadata(metadata_file, data):
    """Saves metadata to the specified JSON file."""
    with open(metadata_file, "w") as f:
        json.dump(data, f, indent=4)


def add_record(url, downloaded_filename, data_name, tags):
    """Adds a new record to the metadata file."""
    config = load_config()  # Load the configuration
    metadata_file = os.path.join(config["download_directory"], "metadata.json")

    # Accept only lowercase names and tags
    data_name = data_name.lower()
    tags = [tag.lower() for tag in tags]

    # Ensure metadata.json exists
    if not os.path.exists(metadata_file):
        with open(metadata_file, "w") as f:
            json.dump([], f, indent=4)

    data = load_metadata(metadata_file)

    # Check if the URL already exists in the metadata
    existing_record = next(
        (record for record in data if record["source_url"] == url), None
    )

    if existing_record:
        # Overwrite the existing record
        existing_record.update(
            {
                "downloaded_filename": downloaded_filename,
                "data_name": data_name,
                "tags": tags,
                "download_timestamp": datetime.now().isoformat(),
            }
        )
        print(f"Metadata for URL {url} updated in {metadata_file}")
    else:
        # Check if the data_name has already been used
        if any(record["data_name"] == data_name for record in data):
            raise Exception(
                f"Error: The data name '{data_name}' already exists. Please choose a different name."
            )

        # Add a new record if URL does not exist
        new_record = {
            "id": len(data) + 1,  # Simple incrementing ID
            "source_url": url,
            "downloaded_filename": downloaded_filename,
            "data_name": data_name,
            "tags": tags,
            "download_timestamp": datetime.now().isoformat(),
        }
        data.append(new_record)
        print(f"Metadata recorded in {metadata_file} \n")

    save_metadata(metadata_file, data)
