import argparse
import os
import requests
from geoprovenance.config import load_config
from geoprovenance.metadata import add_record
from urllib.parse import urlparse


def download_file(url, destination_folder):
    """Downloads a file from a URL to a specified folder."""
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

        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Successfully downloaded {url} to {destination_path}")
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

    args = parser.parse_args()

    config = load_config()  # Load config from ~/.geoprovenance/config.json

    if args.command == "ingest":
        print(f"Attempting to download from: {args.url}")
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
            config["download_directory"] = args.dir
            print(f"Data save directory updated to: {args.dir}")
        print("Current configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
