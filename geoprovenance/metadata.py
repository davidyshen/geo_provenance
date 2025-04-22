import json
import os
from datetime import datetime


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


def add_record(config, url, downloaded_filename, data_name, tags):
    """Adds a new record to the metadata file."""
    metadata_file = config["metadata_file"]
    data = load_metadata(metadata_file)

    new_record = {
        "id": len(data) + 1,  # Simple incrementing ID
        "source_url": url,
        "downloaded_filename": downloaded_filename,
        "data_name": data_name,
        "tags": tags,
        "download_timestamp": datetime.now().isoformat(),
    }
    data.append(new_record)
    save_metadata(metadata_file, data)
    print(f"Metadata recorded in {metadata_file}")
