import os
import json
import requests
import zipfile
import shutil
from tqdm import tqdm
from .config import load_config
from .metadata import add_record
from urllib.parse import urlparse
from datetime import datetime

# The core download function
def download(url, destination_folder):
    """Downloads a file from a URL to a specified folder."""

    print(f"Attempting to download from: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:  # Handle cases where path ends in / or is just domain
            filename = (
                url.split("/")[-1] if "/" in url else url.split(":")[-1]
            )  # Basic fallback
            if not filename:  # Final fallback
                filename = f"downloaded_file{datetime.now().strftime('%Y%m%d%H%M%S')}"

        destination_path = os.path.join(destination_folder, filename)

        # Get the total file size from headers
        total_size = int(response.headers.get("content-length", 0))

        # Make progress bar
        with open(destination_path, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc=filename
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress_bar.update(len(chunk))

        print(f"Successfully downloaded {url} to {destination_path} \n")
        return filename  # Return the actual filename saved
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    except IOError as e:
        print(f"Error saving file to {destination_path}: {e}")
        return None

def ingest(url, name, tags):
    """Ingests a file from a URL and records its metadata."""
    config = load_config()  # Load the configuration

    # Download the file
    downloaded_filename = download_core(url, config["download_directory"])

    if downloaded_filename:
        add_record(
            config=config,
            url=url,
            downloaded_filename=downloaded_filename,
            data_name=name,
            tags=tags,
        )
    else:
        print("Metadata recording skipped due to download failure.")

def ingest_zip_single(url, file, name, tags):
    """Ingests a zip file from a URL and records its metadata."""
    config = load_config()  # Load the configuration
    tmp_out_dir = os.path.join(config["download_directory"], "tmp")

    # Download the file
    downloaded_filename = download(url, tmp_out_dir)

    with zipfile.ZipFile(
        os.path.join(tmp_out_dir, downloaded_filename), "r"
    ) as zip_ref:
        # Extract the specified file from the zip
        zip_ref.extract(file, config["download_directory"])

    if downloaded_filename:
        add_record(
            url=url,
            downloaded_filename=file,
            data_name=name,
            tags=tags,
        )
    else:
        print("Metadata recording skipped due to download failure.")
