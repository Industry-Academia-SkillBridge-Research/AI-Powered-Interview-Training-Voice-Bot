#!/usr/bin/env python3
"""
Generate a CSV manifest from RAVDESS-style filenames in the `input` folder.
Saves a CSV with columns: file_path, file_name, emotion_code, emotion_label, intensity_code, actor_id

Usage:
    python scripts/generate_labels_from_filenames.py --input C:/Users/dilit/OneDrive - Sri Lanka Institute of Information Technology/Research/ai-powered-interview-training-voicebot/backend/app/inputs/dataset --output C:/Users/dilit/OneDrive - Sri Lanka Institute of Information Technology/Research/ai-powered-interview-training-voicebot/backend/app/inputs/labels_from_filenames.csv

"""
import argparse
import csv
import os
from pathlib import Path

EMOTION_MAP = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}


def parse_filename(file_path: str) -> dict:
    name = Path(file_path).name
    base = Path(name).stem
    tokens = base.split("-")
    parsed = {
        "file_name": name,
        "file_path": str(file_path),
        "emotion_code": "",
        "emotion_label": "",
        "intensity_code": "",
        "actor_id": "",
    }
    if len(tokens) >= 7:
        parsed.update({
            "modality": tokens[0],
            "channel": tokens[1],
            "emotion_code": tokens[2],
            "emotion_label": EMOTION_MAP.get(tokens[2], "UNKNOWN"),
            "intensity_code": tokens[3],
            "statement": tokens[4],
            "repetition": tokens[5],
            "actor_id": tokens[6],
        })
    else:
        # Try to handle other formats gracefully
        if len(tokens) >= 3:
            parsed["emotion_code"] = tokens[2]
            parsed["emotion_label"] = EMOTION_MAP.get(tokens[2], "UNKNOWN")
    return parsed


def collect_wav_files(base_dir: str):
    base = Path(base_dir)
    if not base.exists():
        raise FileNotFoundError(f"Input folder does not exist: {base_dir}")
    return sorted([str(p) for p in base.rglob("*.wav")])


def main(input_folder: str, output_csv: str):
    files = collect_wav_files(input_folder)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    fields = [
        "file_path",
        "file_name",
        "emotion_code",
        "emotion_label",
        "intensity_code",
        "actor_id",
        "modality",
        "channel",
        "statement",
        "repetition",
    ]

    written = 0
    with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for f in files:
            parsed = parse_filename(f)
            # Filter only entries that have a valid emotion code
            if parsed.get("emotion_code"):
                row = {k: parsed.get(k, "") for k in fields}
                writer.writerow(row)
                written += 1

    print(f"Wrote {written} rows to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CSV from RAVDESS-like filenames.")
    parser.add_argument("--input", required=True, help="Directory containing .wav files (recursive)")
    parser.add_argument("--output", default="data/labels_from_filenames.csv", help="Path to write CSV output")
    args = parser.parse_args()
    main(args.input, args.output)
