from __future__ import annotations

import csv
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "temperature_dataset_samples"
TIMEOUT = 60


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "temperature-dataset-check/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read()


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def parse_nasa_csv(text: str) -> dict:
    lines = [line for line in text.splitlines() if line.strip()]
    header_at = next(i for i, line in enumerate(lines) if line.startswith("Year,"))
    rows = list(csv.DictReader(lines[header_at:]))
    years = [int(row["Year"]) for row in rows if row.get("Year", "").isdigit()]
    return {
        "rows": len(rows),
        "start": min(years),
        "end": max(years),
        "columns": list(rows[0].keys()) if rows else [],
        "latest_annual_anomaly_c": rows[-1].get("J-D") if rows else None,
    }


def noaa_latest_url() -> str:
    index_url = "https://www.ncei.noaa.gov/data/noaa-global-surface-temperature/v6.1/access/timeseries/"
    html = fetch(index_url).decode("utf-8", errors="replace")
    names = re.findall(r'href="([^"]*aravg\.mon\.land_ocean\.90S\.90N\.v6\.1\.0\.\d+\.asc)"', html)
    if not names:
        names = re.findall(r"(aravg\.mon\.land_ocean\.90S\.90N\.v6\.1\.0\.\d+\.asc)", html)
    if not names:
        raise RuntimeError("NOAA directory was reachable, but the global land-ocean monthly file was not found.")
    return index_url + sorted(set(names))[-1]


def parse_noaa_asc(text: str) -> dict:
    data_rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
            data_rows.append(parts)
    dates = [(int(row[0]), int(row[1])) for row in data_rows]
    return {
        "rows": len(data_rows),
        "start": f"{dates[0][0]:04d}-{dates[0][1]:02d}" if dates else None,
        "end": f"{dates[-1][0]:04d}-{dates[-1][1]:02d}" if dates else None,
        "latest_anomaly_c": data_rows[-1][2] if data_rows else None,
    }


def parse_hadcrut_csv(text: str) -> dict:
    rows = list(csv.DictReader(text.splitlines()))
    date_field = "Time" if rows and "Time" in rows[0] else rows[0].keys().__iter__().__next__()
    anomaly_field = "Anomaly (deg C)" if rows and "Anomaly (deg C)" in rows[0] else None
    if anomaly_field is None and rows:
        anomaly_field = next((key for key in rows[0] if "anomaly" in key.lower()), None)
    dates = [row[date_field] for row in rows]
    return {
        "rows": len(rows),
        "start": dates[0] if dates else None,
        "end": dates[-1] if dates else None,
        "columns": list(rows[0].keys()) if rows else [],
        "latest_anomaly_c": rows[-1].get(anomaly_field) if rows and anomaly_field else None,
    }


def parse_berkeley_txt(text: str) -> dict:
    data_rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit():
            data_rows.append(parts)
    dates = [(int(row[0]), int(row[1])) for row in data_rows]
    return {
        "rows": len(data_rows),
        "start": f"{dates[0][0]:04d}-{dates[0][1]:02d}" if dates else None,
        "end": f"{dates[-1][0]:04d}-{dates[-1][1]:02d}" if dates else None,
        "latest_anomaly_c": data_rows[-1][2] if data_rows else None,
    }


def main() -> int:
    checks = [
        {
            "name": "NASA GISTEMP v4 global LOTI",
            "url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
            "path": DATA_DIR / "nasa_gistemp_global_loti.csv",
            "parser": parse_nasa_csv,
            "source": "https://data.giss.nasa.gov/gistemp/data_v4.html",
        },
        {
            "name": "NOAA GlobalTemp v6.1 global land-ocean",
            "url": noaa_latest_url,
            "path": DATA_DIR / "noaa_globaltemp_v6_1_land_ocean_global.asc",
            "parser": parse_noaa_asc,
            "source": "https://www.ncei.noaa.gov/products/land-based-station/noaa-global-temp",
        },
        {
            "name": "HadCRUT5 analysis global monthly",
            "url": "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.1.0.0/analysis/diagnostics/HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.csv",
            "path": DATA_DIR / "hadcrut5_5_1_global_monthly.csv",
            "parser": parse_hadcrut_csv,
            "source": "https://www.metoffice.gov.uk/hadobs/hadcrut5/",
        },
        {
            "name": "Berkeley Earth high-resolution global monthly",
            "url": "https://storage.googleapis.com/berkeley-earth-temperature-hr/global/Global_TAVG_monthly.txt",
            "path": DATA_DIR / "berkeley_earth_hr_global_monthly.txt",
            "parser": parse_berkeley_txt,
            "source": "https://berkeleyearth.org/data/",
        },
    ]

    results = []
    for check in checks:
        result = {
            "name": check["name"],
            "source_page": check["source"],
            "checked_at": dt.datetime.now(dt.UTC).isoformat(),
        }
        try:
            url = check["url"]() if callable(check["url"]) else check["url"]
            data = fetch(url)
            write_bytes(check["path"], data)
            parsed = check["parser"](data.decode("utf-8", errors="replace"))
            result.update(
                {
                    "status": "ok",
                    "url": url,
                    "saved_to": str(check["path"].relative_to(ROOT)),
                    "bytes": len(data),
                    **parsed,
                }
            )
        except (urllib.error.URLError, RuntimeError, ValueError, csv.Error, UnicodeDecodeError) as exc:
            result.update({"status": "failed", "error": str(exc)})
        results.append(result)

    report_path = ROOT / "temperature_dataset_check_results.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    for result in results:
        print(f"{result['status'].upper():6} {result['name']}")
        if result["status"] == "ok":
            print(f"       {result['start']} -> {result['end']} | rows={result['rows']} | saved={result['saved_to']}")
            print(f"       {result['url']}")
        else:
            print(f"       {result['error']}")
    print(f"\nWrote {report_path.name}")
    return 0 if all(result["status"] == "ok" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
