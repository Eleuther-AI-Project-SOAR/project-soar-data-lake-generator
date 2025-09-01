import re
import gdown
import pandas as pd
from datetime import datetime
import json

from dotenv import load_dotenv
import os

load_dotenv()
os.makedirs("build", exist_ok=True)

URL = os.getenv("URL")
CSV_OUTPUT_FILENAME = f"build/{os.getenv('CSV_OUTPUT_FILENAME')}_{datetime.today().strftime('%Y-%m-%d')}.csv"
JSON_OUTPUT_FILENAME = f"build/{os.getenv('JSON_OUTPUT_FILENAME')}_{datetime.today().strftime('%Y-%m-%d')}.json"
JS_OUTPUT_FILENAME = f"build/{os.getenv('JS_OUTPUT_FILENAME')}.js"


def sheet_to_csv_url(sheet_url: str) -> pd.DataFrame:
    """
    Converts original Google Sheets link to match Sheets download API.
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
    df.columns = df.columns.str.strip()

    # Cleanup
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df = df.reset_index(drop=True)

    # Write
    records = []
    for _, row in df.iterrows():
        features = []

        if str(row.get("Research paper reading group?", "no")).lower() == "yes":
            features.append("Reading Group")
        if str(row.get("paper channel?", "no")).lower() == "yes":
            features.append("Paper Channel")
        if str(row.get("vc events,office/coworking hours,etc", "no")).lower() == "yes":
            features.append("VC events/Office Hours")
        if str(row.get("jobs board/opportunities/funding links", "no")).lower() == "yes":
            features.append("Jobs Board")
        if (str(row.get("company/github projects?", "no")).lower() == "yes" or
                str(row.get("community created projects", "no")).lower() == "yes"):
            features.append(
                "Company/Github Projects, Community Created Projects")

        record = {
            "name": row["name"],
            "rating": float(row["score"]) if pd.notnull(row["score"]) else None,
            "tag": row["Type of server"].capitalize() if pd.notnull(row["Type of server"]) else None,
            "overview": row.get("what specifcally", ""),
            "activityLevel": row["Activity"].title() if pd.notnull(row["Activity"]) else None,
            "language": row["language"].capitalize() if pd.notnull(row["language"]) else None,
            "location": row["location"].capitalize() if pd.notnull(row["location"]) else None,
            "governanceType": row["governance type"] if pd.notnull(row["governance type"]) else None,
            "links": row["links"] if pd.notnull(row["links"]) else None,
            "description": row["notes"] if pd.notnull(row["notes"]) else None,
            "features": features
        }

        records.append(record)

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"JSON saved to {json_filename}")


def json_to_js(json_filename: str, js_filename: str):
    """
    Reads a JSON file and writes it as a JS file with `export const servers = ...`
    """
    with open(json_filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(js_filename, "w", encoding="utf-8") as f:
        f.write("export const servers = ")
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write(";\n")

    print(f"JS module saved as {js_filename}")


gdown.download(sheet_to_csv_url(URL), CSV_OUTPUT_FILENAME, quiet=False)
csv_to_json(CSV_OUTPUT_FILENAME, JSON_OUTPUT_FILENAME)
json_to_js(JSON_OUTPUT_FILENAME, JS_OUTPUT_FILENAME)
