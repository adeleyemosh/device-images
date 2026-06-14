"""Fetch device_marketing_names.json: maps Android model codes to marketing
names, using Google's Play-certified device catalog.

Source: https://storage.googleapis.com/play_public/supported_devices.html
(an HTML table of Retail Branding / Marketing Name / Device / Model). Rows
are filtered down to the brands in brands.json and keyed by lowercased
Model, e.g. samsung/"sm-s928b" -> "Galaxy S24 Ultra".
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone

CATALOG_URL = "https://storage.googleapis.com/play_public/supported_devices.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

CELL_RE = re.compile(r"<td>(.*?)</td>")

# Retail Branding values in the catalog that don't match brands.json's
# `name` field exactly (Apple has no Android entries and is skipped).
RETAIL_BRANDING_ALIASES: dict[str, list[str]] = {
    "lg": ["LGE", "LG_Electronics"],
    "alcatel": ["TCT (Alcatel)"],
}


def fetch_catalog_rows() -> list[tuple[str, str, str, str]]:
    req = urllib.request.Request(CATALOG_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")

    cells = CELL_RE.findall(text)
    return [tuple(cells[i : i + 4]) for i in range(0, len(cells) - 3, 4)]


def generate_marketing_names(brands: list[dict]) -> dict:
    branding_to_slug: dict[str, str] = {}
    for brand in brands:
        slug = brand["slug"]
        for name in RETAIL_BRANDING_ALIASES.get(slug, [brand["name"]]):
            branding_to_slug[name.lower()] = slug

    manifest_brands: dict[str, dict[str, str]] = {}
    for branding, marketing, _device, model in fetch_catalog_rows():
        slug = branding_to_slug.get(branding.strip().lower())
        if slug is None:
            continue
        manifest_brands.setdefault(slug, {})[model.strip().lower()] = marketing.strip()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": CATALOG_URL,
        "brands": manifest_brands,
    }


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brands_json_path = os.path.join(repo_root, "brands.json")
    output_path = os.path.join(repo_root, "device_marketing_names.json")

    with open(brands_json_path) as f:
        brands = json.load(f)["brands"]

    data = generate_marketing_names(brands)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")

    total = sum(len(v) for v in data["brands"].values())
    print(f"device_marketing_names.json: {len(data['brands'])} brands, {total} models")


if __name__ == "__main__":
    main()
