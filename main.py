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
JS_OUTPUT_FILENAME = f"build/{os.getenv('JS_OUTPUT_FILENAME')}_{datetime.today().strftime('%Y-%m-%d')}.json"


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


def safe_float(val, default=-1.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_str(val: object) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val)


def csv_to_json(csv_filename: str, json_filename: str):
    df = pd.read_csv(csv_filename)

    if "name" in df.columns:
        df = df[df["name"].notna() & (df["name"].astype(str).str.strip() != "")]
    else:
        print("Warning: 'name' column not found. Output will be empty.")
        df = pd.DataFrame(columns=df.columns)

    # Drop unnamed columns
    cols_to_drop = [f"Unnamed: {i}" for i in range(16, 23)]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Transformation rules
    transformed = []
    for _, row in df.iterrows():
        features = []
        if str(row.get("Research paper reading group?", "")).lower().startswith("yes"):
            features.append("Reading Group")
        if str(row.get("Other Reading group? (eg math)", "")).lower().startswith("yes"):
            features.append("Paper Channel")
        if str(row.get("Events/workshops etc", "")).lower().startswith("yes"):
            features.append("VC events/Office Hours")
        if str(row.get("Community projects?", "")).lower().startswith("yes"):
            features.append("Jobs Board")

        transformed.append({
            "name": safe_str(row.get("name")).strip(),
            "rating": safe_float(row.get("score (take this with a grain of salt)", -1)),
            "tag": safe_str(row.get("Type of server (research/general etc)")).strip().title(),
            "activityLevel": safe_str(row.get("Activity (va: multiple posts an hour, active: posts a few times a day or so; semi-active posts a week/ whenever someone asks something, mostly inactive, inactive) ;Not related to reading group etc activites.;If they have those things then they are probably active ; includes projects")).strip().title(),
            "language": safe_str(row.get("language")).replace(" language", "").strip().title(),
            "location": safe_str(row.get("location:")).strip().title(),
            "description": safe_str(row.get("notes")).strip(),
            "features": features
        })
    # Save to JSON
    pd.DataFrame(transformed).to_json(
        json_filename, orient="records", indent=2)
    print(f"Custom JSON saved as {json_filename}")


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
