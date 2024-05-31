import argparse
import calendar
import matplotlib.pyplot as plt
import requests
import json
import os
import tempfile
import shutil
from collections import defaultdict
from datetime import datetime


def parse_date(date_string, current_year):
    if "-" in date_string:
        parts = [part.strip() for part in date_string.split("-")]

        if len(parts) == 2:
            # Check if the date range includes years
            if "/" in parts[0] and "/" in parts[1]:
                try:
                    # Split each part into month, day, year
                    start_month, start_day, start_year = map(int, parts[0].split("/"))
                    end_month, end_day, end_year = map(int, parts[1].split("/"))

                    start_date = datetime(start_year, start_month, start_day)
                    end_date = datetime(end_year, end_month, end_day)
                except ValueError:
                    # Handle the case where the date format is MM/DD
                    start_month, start_day = map(int, parts[0].split("/"))
                    end_month, end_day = map(int, parts[1].split("/"))

                    start_date = datetime(current_year, start_month, start_day)
                    end_year = (
                        current_year + 1 if end_month < start_month else current_year
                    )
                    end_date = datetime(end_year, end_month, end_day)
            else:
                # Month range format: October-November
                start_month = datetime.strptime(parts[0] + " 1", "%B %d").month
                end_month = datetime.strptime(parts[1] + " 1", "%B %d").month

                start_year = current_year
                end_year = current_year + 1 if end_month < start_month else current_year

                start_date = datetime(start_year, start_month, 1)
                end_date = datetime(
                    end_year, end_month, calendar.monthrange(end_year, end_month)[1]
                )
        else:
            # Single month format: Month name or MM/DD
            if "/" in date_string:
                month, day = map(int, date_string.split("/"))
                start_date = end_date = datetime(current_year, month, day)
            else:
                month = datetime.strptime(date_string.strip() + " 1", "%B %d").month
                start_date = datetime(current_year, month, 1)
                end_date = datetime(
                    current_year, month, calendar.monthrange(current_year, month)[1]
                )

    return start_date, end_date


def parse_date_better(date):
    # handle single name: ex. 'December', 'july'
    # handle single MM/DD: ex. '12/5', '07/02', '7/2'
    # handle single MM/DD/YYYY: '02/3/2023'
    # handle single MM/DD/YY: '2/03/23'
    # handle date range for name: ex. 'july-December', 'August-october'
    # handle date range for MM/DD-MM/DD: ex. '07/1-9/04'
    # handle date range for MM/DD/YYYY-MM/DD/YYYY: ex. '4/02/2023-07/4/2023'
    # handle date range for MM/DD/YY-MM/DD/YY: ex. '05/1/23-7/09/23'

    # split date by '-' to get start and end date
    pass


# Fetch and save release data
def fetch_and_save_releases(repo, start_date, end_date, file_name, token):
    headers = {"Authorization": f"token {token}"} if token else {}
    release_data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/releases?page={page}&per_page=100"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Response Body:", response.text)
            break

        releases = response.json()
        if not releases:
            print("No more releases found.")
            break

        for release in releases:
            release_date = datetime.strptime(
                release["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            if release_date < start_date or release_date > end_date:
                continue

            release_data.append(
                {"name": release["name"], "date": release_date.strftime("%Y-%m-%d")}
            )

        page += 1

    with open(file_name, "w") as file:
        json.dump(release_data, file, indent=4)
        print(f"Saved data to {file_name}")


# Organize release data for each platform
def organize_platform_releases(file_path, platform):
    with open(file_path, "r") as file:
        data = json.load(file)

    organized_data = defaultdict(
        lambda: defaultdict(lambda: {"Release Count": 0, "Versions Released": []})
    )

    for release in data:
        # For iOS Focus, include releases with "Focus / Klar" in their name
        if (
            platform == "iOS"
            and "focus" in file_path.lower()
            and "Focus" not in release["name"]
        ):
            continue

        # For other releases, continue with existing categorization logic
        if platform == "Android":
            if "Android-Components" in release["name"]:
                continue
            elif "Focus" in release["name"]:
                category = "Focus"
            elif "Firefox Beta" in release["name"]:
                category = "Firefox Beta"
            elif "Firefox" in release["name"]:
                category = "Firefox"
            else:
                continue
        elif platform == "iOS":
            if "firefox" in file_path.lower():
                category = "Firefox"
            elif "focus" in file_path.lower():
                category = "Focus"
            else:
                continue

        month = datetime.strptime(release["date"], "%Y-%m-%d").strftime("%B")
        organized_data[category][month]["Release Count"] += 1
        organized_data[category][month]["Versions Released"].append(
            f"{release['name']} ({release['date']})"
        )

    return {platform: {cat: dict(months) for cat, months in organized_data.items()}}


def create_bar_chart(monthly_data):
    months = sorted(monthly_data.keys(), key=month_sorter)
    categories = sorted({cat for data in monthly_data.values() for cat in data})

    n_categories = len(categories)
    n_months = len(months)
    bar_width = 0.8 / n_categories  # Adjust bar width based on number of categories

    # Creating the bar chart
    fig, ax = plt.subplots()
    for i, category in enumerate(categories):
        monthly_counts = [monthly_data[month][category] for month in months]
        # Calculate position for each bar
        positions = [x + bar_width * i for x in range(len(months))]
        ax.bar(positions, monthly_counts, bar_width, label=category)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Releases")
    ax.set_title("Monthly Releases by Platform and Type")
    ax.set_xticks(
        [x + bar_width * (n_categories / 2) - bar_width / 2 for x in range(n_months)]
    )
    ax.set_xticklabels(months)
    ax.legend()

    plt.xticks(rotation=45)  # Rotate labels to improve readability
    plt.tight_layout()  # Adjust layout to fit everything nicely
    plt.savefig("bar_chart.png", dpi=300)
    plt.close()


def create_plot_graph(monthly_data):
    months = sorted(monthly_data.keys(), key=month_sorter)
    categories = sorted({cat for data in monthly_data.values() for cat in data})

    # Creating the plot graph
    plt.figure()
    for category in categories:
        monthly_counts = [monthly_data[month][category] for month in months]
        plt.plot(months, monthly_counts, marker="o", label=category)

    plt.xlabel("Month")
    plt.ylabel("Number of Releases")
    plt.title("Monthly Release Trends by Platform and Type")
    plt.legend()
    plt.savefig("plot_graph.png", dpi=300)
    plt.close()


def extract_data_for_graphs(combined_data):
    # Removing the summary for graphing purposes
    combined_data.pop("Summary", None)

    monthly_data = defaultdict(lambda: defaultdict(int))

    for platform, platform_data in combined_data.items():
        for release_type, releases in platform_data.items():
            for month, month_data in releases.items():
                monthly_data[month][f"{platform} - {release_type}"] += month_data[
                    "Release Count"
                ]

    return monthly_data


def month_sorter(month):
    """Custom sorter for months starting from July"""
    months_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    return months_order.index(month)


def print_summary(combined_data, start_date, end_date):
    # formatted_start_date = start_date.strftime("%B %d, %Y")
    # formatted_end_date = end_date.strftime("%B %d, %Y")

    print("***************************************")
    print("Mobile Release Summary:")

    for platform, release_info in combined_data["Summary"].items():
        print(f"\n    {platform} Releases:")

        for release_type, count in release_info.items():
            if release_type != "Total Releases":
                print(f"      {release_type}: {count['Total Releases']}")
        print(f"      TOTAL: {release_info['Total Releases']}\n")

    for platform, platform_data in combined_data.items():
        if (
            platform != "Summary" and platform_data
        ):  # Check if platform data is not empty
            print(f"  {platform}:\n")
            for release_type, releases in platform_data.items():
                print(f"    {release_type}:")
                for month, month_data in releases.items():
                    print(f"      {month}: {month_data['Release Count']} releases")
                print()  # Add a newline for separation between release types

    print(
        "***************************************", end=""
    )  # 'end=""' to avoid extra newline


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Mobile Releases Aggregator Tool",
        epilog="""
Example usage:
  python mobile_release_cli.py -repo mozilla-mobile/firefox-android
    -date_range 7/1/2023-12/5/2023 --save --summary --graph bar
  python mobile_release_cli.py -repo mozilla-mobile/firefox-android 
    -date_range July --summary --graph plot
  python mobile_release_cli.py -repo mozilla-mobile/firefox-android 
    -date_range 10/1-11/30 --summary
  python mobile_release_cli.py -repo mozilla-mobile/firefox-android 
    -date_range October-November --save
  python mobile_release_cli.py -repo mozilla-mobile/firefox-android 
    -date_range 10/5 --summary

Arguments:
  -repo: Specify one or more repositories to aggregate. Accepts a space-separated list.
  -date_range: Define the date range for fetching release data. Supports single 
    months (e.g., 'July'), month ranges (e.g., 'July-August'), specific date 
    ranges in MM/DD format (e.g., '7/1-12/5'), and date ranges with years in 
    MM/DD/YYYY format (e.g., '7/1/2023-12/5/2023').
  --save: Include this flag to save the fetched release data into JSON files.
  --summary: Include this flag to print a summary of the fetched release data.
  --graph: Specify the type of graph to generate. Accepts either 'bar' or 'plot'. 
    If omitted, no graph is generated.

Notes:
  - The date range is inclusive and will fetch releases up to the end of the 
    specified range.
  - The '--save' flag saves JSON files in the current directory.
  - The graph files ('bar_chart.png' and 'plot_graph.png') are saved in the 
    current directory when the corresponding graph type is requested.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-repo",
        nargs="+",
        help="List of repositories to aggregate. Example: firefox-android firefox-ios focus-ios",
    )
    parser.add_argument(
        "-date_range",
        type=str,
        help="Date range in format MM/DD/YYYY-MM/DD/YYYY or Month-Month",
    )
    parser.add_argument(
        "--save", action="store_true", help="Save the output data to JSON files"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print a summary of the data"
    )
    parser.add_argument(
        "--graph", choices=["bar", "plot"], help="Generate a graph (bar or plot)"
    )

    return parser.parse_args()


def process_repositories(
    repos, temp_dir, start_date, end_date, github_token, combined_data
):
    temp_file_paths = []
    for repo in repos:
        temp_file_name = os.path.join(
            temp_dir, f"{repo.replace('/', '_')}_releases.json"
        )
        fetch_and_save_releases(
            repo, start_date, end_date, temp_file_name, github_token
        )
        temp_file_paths.append(temp_file_name)
        platform = "iOS" if "ios" in repo else "Android"
        organized_data = organize_platform_releases(temp_file_name, platform)

        if platform == "Android":
            combined_data["Android"].update(organized_data["Android"])
        else:  # iOS
            for release_type, releases in organized_data["iOS"].items():
                for month, month_data in releases.items():
                    combined_ios_data = combined_data["iOS"]
                    combined_ios_data[release_type][month][
                        "Release Count"
                    ] += month_data["Release Count"]
                    combined_ios_data[release_type][month]["Versions Released"].extend(
                        month_data["Versions Released"]
                    )
    return temp_file_paths


def save_data_if_required(temp_file_paths, combined_data, save_flag):
    if save_flag:
        for temp_file_path in temp_file_paths:
            destination_file_path = os.path.join(
                os.getcwd(), os.path.basename(temp_file_path)
            )
            shutil.copy(temp_file_path, destination_file_path)
        with open("combined_releases.json", "w") as file:
            json.dump(combined_data, file, indent=4)


def generate_graphs_if_required(graph_type, combined_data):
    if graph_type:
        monthly_data = extract_data_for_graphs(combined_data)
        if graph_type == "bar":
            create_bar_chart(monthly_data)
        elif graph_type == "plot":
            create_plot_graph(monthly_data)


def main():
    args = parse_arguments()
    current_year = datetime.now().year
    start_date, end_date = parse_date(args.date_range, current_year)
    github_token = os.environ.get("GITHUB_TOKEN")

    combined_data = {
        "Android": {},
        "iOS": defaultdict(
            lambda: defaultdict(lambda: {"Release Count": 0, "Versions Released": []})
        ),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_paths = process_repositories(
            args.repo, temp_dir, start_date, end_date, github_token, combined_data
        )

        # Calculate summary
        summary = defaultdict(lambda: {"Total Releases": 0})
        for platform, platform_data in combined_data.items():
            for release_type, releases in platform_data.items():
                for month, month_data in releases.items():
                    summary[platform][release_type] = {
                        "Total Releases": summary[platform]
                        .get(release_type, {})
                        .get("Total Releases", 0)
                        + month_data["Release Count"]
                    }
                    summary[platform]["Total Releases"] += month_data["Release Count"]
        combined_data["Summary"] = dict(summary)

        save_data_if_required(temp_file_paths, combined_data, args.save)
        if args.summary:
            print_summary(combined_data, start_date, end_date)
        generate_graphs_if_required(args.graph, combined_data)


if __name__ == "__main__":
    main()
