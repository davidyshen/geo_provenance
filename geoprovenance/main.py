import argparse
import os
import requests
import json
from geoprovenance.config import load_config, update_config
from geoprovenance.metadata import add_record
from urllib.parse import urlparse
from tqdm import tqdm


def download_file(url, destination_folder):
    """Downloads a file from a URL to a specified folder."""
    
    # Check if the config download directory has been set
    if load_config()["download_directory"] == "":
        raise Exception(
            "Download directory not set. Please set it using \n\n'geoprovenance config --dir <path>'\n\n"
        )


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
                filename = "downloaded_file"

        destination_path = os.path.join(destination_folder, filename)

        # Get the total file size from headers
        total_size = int(response.headers.get('content-length', 0))

        # Make progress bar
        with open(destination_path, "wb") as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=filename
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


def main():
    parser = argparse.ArgumentParser(description="GeoProvenance CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest command
    parser_ingest = subparsers.add_parser(
        "ingest", help="Download a file and record metadata"
    )
    parser_ingest.add_argument("url", help="URL of the file to download")
    parser_ingest.add_argument("--name", required=True, help="Name of dataset")
    parser_ingest.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags associated with the download (space-separated)",
    )

    # Config command
    parser_config = subparsers.add_parser(
        "config", help="Print the current config file and specify data save directory"
    )
    parser_config.add_argument(
        "--dir", help="Specify the directory where data is saved", default=None
    )

    # List command
    parser_list = subparsers.add_parser(
        "list", help="List all dataset names and their associated tags"
    )

    # Search command
    parser_search = subparsers.add_parser(
        "search", help="Search for datasets by name in the metadata file"
    )
    parser_search.add_argument("query", help="String to search for in dataset names")

    args = parser.parse_args()

    config = load_config()  # Load config from ~/.geoprovenance/config.json

    if args.command == "ingest":
        downloaded_filename = download_file(args.url, config["download_directory"])

        if downloaded_filename:
            add_record(
                config=config,
                url=args.url,
                downloaded_filename=downloaded_filename,
                data_name=args.name,
                tags=args.tags,
            )
        else:
            print("Metadata recording skipped due to download failure.")

    elif args.command == "config":
        if args.dir:
            config["download_directory"] = os.path.abspath(os.path.expanduser(os.path.expandvars(args.dir)))
            print(f"Data save directory updated to: {args.dir}")
            update_config(config)

            # Ensure metadata.json exists in the new directory
            metadata_file = os.path.join(args.dir, "metadata.json")
            if not os.path.exists(args.dir):
                os.makedirs(args.dir, exist_ok=True)
                print(f"Created directory: {args.dir}")
            # Create metadata file if it doesn't exist
            if not os.path.exists(metadata_file):
                with open(metadata_file, "w") as f:
                    json.dump([], f, indent=4)
                print(f"Created metadata file at {metadata_file}")

        print("Current configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

    elif args.command == "list":
        if config["download_directory"]:
            metadata_file = os.path.join(config["download_directory"], "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    if metadata:
                        print("Datasets and their associated tags:")
                        for entry in metadata:
                            print(f"- {entry['data_name']}: {', '.join(entry['tags'])}")
                    else:
                        print("No datasets found in metadata.")
            else:
                print(f"Metadata file not found in {config['download_directory']}.")
        else:
            print("Download directory is not set. Please set it using 'geoprovenance config --dir'.")

    elif args.command == "search":
        if config["download_directory"]:
            metadata_file = os.path.join(config["download_directory"], "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    results = [
                        entry for entry in metadata 
                        if args.query.lower() in entry["data_name"].lower() or \
                           any(args.query.lower() in tag.lower() for tag in entry["tags"])
                    ]
                    if results:
                        print("Search results:")
                        for entry in results:
                            print(f"- {entry['data_name']}: {', '.join(entry['tags'])}")
                    else:
                        print("No matching datasets found.")
            else:
                print(f"Metadata file not found in {config['download_directory']}.")
        else:
            print("Download directory is not set. Please set it using 'geoprovenance config --dir'.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
 