# Mobile Release Aggregator Tool

## Description
This tool is designed to aggregate release data from specified GitHub repositories, focusing particularly on Mozilla mobile applications. It fetches release information within a given date range and provides options to save data, print summaries, and generate graphical representations of the data.

## Features
- Fetch release data from specified GitHub repositories within a given date range.
- Save release data in JSON format.
- Print a summary of releases.
- Generate bar or plot graphs to visualize release data.

## Usage
To use the script, run it from the command line with the necessary arguments. Here are some example usages:

```bash
python mobile_release_cli.py -repo mozilla-mobile/firefox-android -date_range 7/1/2023-12/5/2023 --save --summary --graph bar
python mobile_release_cli.py -repo mozilla-mobile/firefox-android -date_range July --summary --graph plot
python mobile_release_cli.py -repo mozilla-mobile/firefox-android -date_range 10/1-11/30 --summary
python mobile_release_cli.py -repo mozilla-mobile/firefox-android -date_range October-November --save
python mobile_release_cli.py -repo mozilla-mobile/firefox-android -date_range 10/5 --summary
```

### Arguments
- `-repo`: Specify one or more GitHub repositories to aggregate. Accepts a space-separated list.
- `-date_range`: Define the date range for fetching release data. Supports single 
  months (e.g., 'July'), month ranges (e.g., 'July-August'), specific date 
  ranges in MM/DD format (e.g., '7/1-12/5'), and date ranges with years in 
  MM/DD/YYYY format (e.g., '7/1/2023-12/5/2023').
- `--save`: Include this flag to save the fetched release data into JSON files.
- `--summary`: Include this flag to print a summary of the fetched release data.
- `--graph`: Specify the type of graph to generate. Accepts either 'bar' or 'plot'. 
  If omitted, no graph is generated.

### Installation
To run the script, ensure you have Python installed on your system. Clone the repository and navigate to the script's directory in your terminal. The script can be run directly from the command line as shown in the usage examples.

### Dependencies
- Python 3.x
- Matplotlib (for graph generation)
- Requests (for fetching data from GitHub)

To install the required Python packages, run:
```bash
pip install matplotlib requests
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
