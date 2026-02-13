#!/usr/bin/env python
from __future__ import annotations

import gzip
import hashlib
import shutil
import sys
from pathlib import Path
from urllib.request import urlretrieve

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "original"

BASE = "https://data.insideairbnb.com/spain/comunidad-de-madrid/madrid/2025-09-14"
URLS = {
    "listings.csv.gz": f"{BASE}/data/listings.csv.gz",
    "calendar.csv.gz": f"{BASE}/data/calendar.csv.gz",
    "reviews.csv.gz": f"{BASE}/data/reviews.csv.gz",
    "listings_summary.csv": f"{BASE}/visualisations/listings.csv",
    "reviews_summary.csv": f"{BASE}/visualisations/reviews.csv",
    "neighbourhoods.csv": f"{BASE}/visualisations/neighbourhoods.csv",
    "neighbourhoods.geojson": f"{BASE}/visualisations/neighbourhoods.geojson",
}

EXPECTED_CHECKSUMS_FILE = RAW_DIR / "checksums_expected.sha256"
GENERATED_CHECKSUMS_FILE = RAW_DIR / "checksums.sha256"


def sha256_of_file(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_gzip(src_gz: Path, dst_csv: Path) -> None:
    with gzip.open(src_gz, "rb") as src, dst_csv.open("wb") as dst:
        shutil.copyfileobj(src, dst)


def parse_manifest(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    if not path.exists():
        return checksums
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, filename = parts
        checksums[filename.strip()] = digest.strip()
    return checksums


def write_manifest(path: Path, filenames: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open("w", encoding="utf-8") as f:
        for name in filenames:
            digest = sha256_of_file(RAW_DIR / name)
            result[name] = digest
            f.write(f"{digest}  {name}\n")
    return result


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Download directory: {RAW_DIR}")
    for filename, url in URLS.items():
        target = RAW_DIR / filename
        print(f"[INFO] Downloading {filename}")
        urlretrieve(url, target)

    print("[INFO] Extracting compressed files")
    extract_gzip(RAW_DIR / "listings.csv.gz", RAW_DIR / "listings.csv")
    extract_gzip(RAW_DIR / "calendar.csv.gz", RAW_DIR / "calendar.csv")
    extract_gzip(RAW_DIR / "reviews.csv.gz", RAW_DIR / "reviews.csv")

    print("[INFO] Removing temporary .gz files")
    (RAW_DIR / "listings.csv.gz").unlink(missing_ok=True)
    (RAW_DIR / "calendar.csv.gz").unlink(missing_ok=True)
    (RAW_DIR / "reviews.csv.gz").unlink(missing_ok=True)

    expected_files = [
        "calendar.csv",
        "listings.csv",
        "listings_summary.csv",
        "neighbourhoods.csv",
        "neighbourhoods.geojson",
        "reviews.csv",
        "reviews_summary.csv",
    ]

    print(f"[INFO] Writing checksum manifest: {GENERATED_CHECKSUMS_FILE}")
    generated = write_manifest(GENERATED_CHECKSUMS_FILE, expected_files)

    expected = parse_manifest(EXPECTED_CHECKSUMS_FILE)
    if not expected:
        print("[WARNING] checksums_expected.sha256 not found: skipping checksum validation")
        print("[INFO] Download completed")
        return 0

    print("[INFO] Validating checksums against checksums_expected.sha256")
    mismatches: list[str] = []
    for name in expected_files:
        got = generated.get(name)
        exp = expected.get(name)
        if got != exp:
            mismatches.append(f"{name}: expected {exp}, got {got}")

    if mismatches:
        print("[ERROR] Checksum validation failed:")
        for row in mismatches:
            print(f"  - {row}")
        return 1

    print("[INFO] Checksum validation passed")
    print("[INFO] Download completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
