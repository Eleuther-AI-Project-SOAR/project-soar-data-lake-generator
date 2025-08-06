import re
import gdown
import pandas as pd
from datetime import datetime

URL = "https://docs.google.com/spreadsheets/d/1DlBT1pF8-zMECntRWXFsL46gZyvNp1BJlJ6LXGze4dA/edit?gid=0#gid=0"
CSV_OUTPUT_FILENAME = f"PROJECT_SOAR_DATASET_{datetime.today().strftime('%Y-%m-%d')}.csv"
JSON_OUTPUT_FILENAME = f"PROJECT_SOAR_DATASET_{datetime.today().strftime('%Y-%m-%d')}.json"


def sheet_to_csv_url(sheet_url: str) -> pd.DataFrame:
    """
    Converts a Google Sheets URL to a CSV expordf = pd.read_csv(csv_file)t URL.
    """

    # Extract file ID
    file_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
    file_id = file_id_match.group(1) if file_id_match else None

    # Extract gid
    gid_match = re.search(r"[?&]gid=(\d+)", sheet_url)
    gid = gid_match.group(1) if gid_match else "0"

    if not file_id:
        raise ValueError("Invalid Google Sheets URL!")

    # Build CSV export URL
    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"


def csv_to_json(csv_filename: str, json_filename: str):
    df = pd.read_csv(csv_filename)

    # Remove rows where 'name' is missing or empty
    if "name" in df.columns:
        df = df[df["name"].notna() & (df["name"].astype(str).str.strip() != "")]
    else:
        print("Warning: 'name' column not found. Output will be empty.")
        df = pd.DataFrame(columns=df.columns)  # empty

    # Remove Unnamed: xx columns
    cols_to_drop = [f"Unnamed: {i}" for i in range(16, 23)]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    df.to_json(json_filename, orient="records", indent=2)
    print(f"CSV converted to JSON and saved as {json_filename}")


gdown.download(sheet_to_csv_url(URL), CSV_OUTPUT_FILENAME, quiet=False)
csv_to_json(CSV_OUTPUT_FILENAME, JSON_OUTPUT_FILENAME)
