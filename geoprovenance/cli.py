import argparse
import os
import requests
import json
from geoprovenance.config import load_config, update_config
from geoprovenance.metadata import add_record
from geoprovenance.find import find_dataset_path
from geoprovenance.download import download
from urllib.parse import urlparse
from tqdm import tqdm


def cli():
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

    # Find command
    parser_find = subparsers.add_parser(
        "find", help="Find the full path of a dataset by name in the metadata file"
    )
    parser_find.add_argument("dataset", help="Name of the dataset to find")

    args = parser.parse_args()

    if args.command == "config":
        config = load_config(
            allow_unset=True
        )  # Load config from ~/.geoprovenance/config.json
        if args.dir:
            config["download_directory"] = os.path.abspath(
                os.path.expanduser(os.path.expandvars(args.dir))
            )
            print(f"Data save directory updated to: {args.dir}")
            update_config(config)

        print("Current configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

    else:
        config = load_config()

        if args.command == "ingest":
            downloaded_filename = download(args.url, config["download_directory"])

            if downloaded_filename:
                add_record(
                    url=args.url,
                    downloaded_filename=downloaded_filename,
                    data_name=args.name,
                    tags=args.tags,
                )
            else:
                print("Metadata recording skipped due to download failure.")

        elif args.command == "list":
            metadata_file = os.path.join(config["download_directory"], "metadata.json")
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                if metadata:
                    print("Datasets and their associated tags:")
                    for entry in metadata:
                        print(f"- {entry['data_name']}: {', '.join(entry['tags'])}")
                else:
                    print("No datasets found in metadata.")

        elif args.command == "search":
            metadata_file = os.path.join(config["download_directory"], "metadata.json")
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                results = [
                    entry
                    for entry in metadata
                    if args.query.lower() in entry["data_name"].lower()
                    or any(args.query.lower() in tag.lower() for tag in entry["tags"])
                ]
                if results:
                    print("Search results:")
                    for entry in results:
                        print(f"- {entry['data_name']}: {', '.join(entry['tags'])}")
                else:
                    print("No matching datasets found.")

        elif args.command == "find":
            try:
                full_path = find_dataset_path(args.dataset, config)
                print(full_path)
            except ValueError as e:
                print(e)
            except FileNotFoundError as e:
                print(e)

        else:
            parser.print_help()


if __name__ == "__main__":
    cli()
