"""Master CLI for device-images: scrape new device photos and convert formats.

Usage:
    python scripts/update.py [--all] [--brands a,b,c] [--skip-scrape] [--skip-convert] [--list]

If neither --all nor --brands is given, --all is assumed.
Exits with status 1 if any brand had a download or conversion failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import converter
import scraper


def load_brands(brands_json_path: str) -> list[dict]:
    with open(brands_json_path) as f:
        data = json.load(f)
    return data["brands"]


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brands_json_path = os.path.join(repo_root, "brands.json")
    images_root = os.path.join(repo_root, "images")

    parser = argparse.ArgumentParser(
        description="Update device-images: scrape new photos and convert formats"
    )
    parser.add_argument("--all", action="store_true", help="Process all brands in brands.json")
    parser.add_argument("--brands", type=str, help="Comma-separated list of brand slugs to process")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip the GSMArena scrape step")
    parser.add_argument(
        "--skip-convert", action="store_true", help="Skip the jpg -> png/webp conversion step"
    )
    parser.add_argument("--list", action="store_true", help="List configured brands and exit")
    args = parser.parse_args()

    brands = load_brands(brands_json_path)

    if args.list:
        for brand in brands:
            url = brand.get("gsmarena_url") or "(no gsmarena_url configured)"
            print(f"{brand['slug']:12} {brand['name']:15} {url}")
        return 0

    if args.brands:
        wanted = {s.strip() for s in args.brands.split(",") if s.strip()}
        selected = [b for b in brands if b["slug"] in wanted]
        missing = wanted - {b["slug"] for b in selected}
        if missing:
            print(f"Unknown brand slug(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
    else:
        selected = brands

    had_failure = False
    total_downloaded = total_skipped = total_failed_scrape = 0
    total_converted = total_up_to_date = total_failed_convert = 0

    for brand in selected:
        slug = brand["slug"]

        if not args.skip_scrape:
            scrape_result = scraper.scrape_brand(brand, images_root, verbose=False)
            if scrape_result.skipped_reason:
                print(f"[{slug}] scrape skipped: {scrape_result.skipped_reason}")
            else:
                total_downloaded += scrape_result.downloaded
                total_skipped += scrape_result.skipped
                total_failed_scrape += scrape_result.failed
                if scrape_result.failed:
                    had_failure = True
                print(
                    f"[{slug}] scrape: downloaded={scrape_result.downloaded}, "
                    f"skipped={scrape_result.skipped}, failed={scrape_result.failed}"
                )

        if not args.skip_convert:
            convert_result = converter.convert_brand(slug, images_root, verbose=False)
            total_converted += convert_result.converted
            total_up_to_date += convert_result.up_to_date
            total_failed_convert += convert_result.failed
            if convert_result.failed:
                had_failure = True
            print(
                f"[{slug}] convert: converted={convert_result.converted}, "
                f"up_to_date={convert_result.up_to_date}, failed={convert_result.failed}"
            )

    print("\n=== TOTAL ===")
    if not args.skip_scrape:
        print(
            f"Scrape: downloaded={total_downloaded}, skipped={total_skipped}, "
            f"failed={total_failed_scrape}"
        )
    if not args.skip_convert:
        print(
            f"Convert: converted={total_converted}, up_to_date={total_up_to_date}, "
            f"failed={total_failed_convert}"
        )

    return 1 if had_failure else 0


if __name__ == "__main__":
    sys.exit(main())
