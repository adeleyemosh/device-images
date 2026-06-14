"""Generate manifest.json: a catalog of all available device images.

Lists the base filenames (no extension) available under
images/<brand>/webp/ for each brand in brands.json. Consumers reconstruct
the full path as images/<brand>/webp/<filename>.webp.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


def generate_manifest(brands: list[dict], images_root: str) -> dict:
    manifest_brands = {}

    for brand in brands:
        slug = brand["slug"]
        webp_dir = os.path.join(images_root, slug, "webp")
        if not os.path.isdir(webp_dir):
            continue

        filenames = sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(webp_dir)
            if f.lower().endswith(".webp")
        )
        if filenames:
            manifest_brands[slug] = filenames

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "brands": manifest_brands,
    }


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brands_json_path = os.path.join(repo_root, "brands.json")
    images_root = os.path.join(repo_root, "images")
    manifest_path = os.path.join(repo_root, "manifest.json")

    with open(brands_json_path) as f:
        brands = json.load(f)["brands"]

    manifest = generate_manifest(brands, images_root)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    total = sum(len(v) for v in manifest["brands"].values())
    print(f"manifest.json: {len(manifest['brands'])} brands, {total} images")


if __name__ == "__main__":
    main()
