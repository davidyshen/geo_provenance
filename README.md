# geoprovenance

A package ingesting and tracking geospatial data and its provenance.

## Installation

```bash
pip install geoprovenance@git+https://github.com/davidyshen/geo_provenance
```

## Usage

Ingesting and searching for data is done through the command line interface (CLI).

```bash
geoprovenance config --dir # Set the data download and storage directory

geoprovenance ingest URL --name DATANAME --tags TAG1 TAG2 TAG3

geoprovenance list # List all ingested data

geoprovenance search SEARCHTERMS # Search for ingested data by name or tags
```

To use data in your Python code, you can use the `load` function from the `geoprovenance` package. This function will return the path to the data file.

The `load` function allows you to load a dataset by its user-defined name, simplifying the process of accessing the data you need. The function will automatically handle the retrieval of the dataset, making it easy to work with geospatial data in your projects.

```python
import geoprovenance as geoprov

# Load the DATANAME data from the geoprovenance database
# This will return the path to the data file
filename = gp.load("DATANAME")
```

## License

`geoprovenance` was created by David Shen. It is licensed under the terms of the MIT license.
