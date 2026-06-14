"""GSMArena scraper for device-images.

Fetches device product photos for a single brand from GSMArena, filtered by
the brand's `title_include`/`title_exclude` rules from `brands.json`, and
saves them as JPEGs into `images/<slug>/jpg/`.
"""

from __future__ import annotations

import html
import io
import os
import re
import time
import urllib.request
from dataclasses import dataclass, field

from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

PHONE_PATTERN = re.compile(
    r'<li><a href="[^"]*"><img src=(https://fdn2\.gsmarena\.com/vv/bigpic/[^ ]+\.\w+) '
    r'title="([^"]*)"><strong><span>([^<]*)</span>',
    re.IGNORECASE,
)

NAV_PAGE_RE = re.compile(r'href="([a-z0-9\-]+-f-\d+-0-p)(\d+)\.php"')


@dataclass
class ScrapeResult:
    slug: str
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    failed_items: list[tuple[str, str, str]] = field(default_factory=list)
    skipped_reason: str | None = None


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def title_matches(title: str, include: list[str], exclude: list[str]) -> bool:
    return any(s in title for s in include) and not any(s in title for s in exclude)


def discover_pages(page1_url: str, content: str) -> list[str]:
    pages = [page1_url]
    matches = NAV_PAGE_RE.findall(content)
    if matches:
        prefix = matches[0][0]
        max_n = max(int(n) for _, n in matches)
        for n in range(2, max_n + 1):
            pages.append(f"https://www.gsmarena.com/{prefix}{n}.php")
    return pages


def parse_phones(content: str, include: list[str], exclude: list[str]) -> list[tuple[str, str, str]]:
    phones = []
    for url, title, name in PHONE_PATTERN.findall(content):
        title_unesc = html.unescape(title)
        name_unesc = html.unescape(name)
        if title_matches(title_unesc, include, exclude):
            fname = url.split("/")[-1]
            phones.append((name_unesc, fname, url))
    return phones


def existing_basenames(jpg_dir: str) -> set[str]:
    bases = set()
    if os.path.isdir(jpg_dir):
        for f in os.listdir(jpg_dir):
            base, _ext = os.path.splitext(f)
            bases.add(base.lower())
    return bases


def is_placeholder(fname: str, slug: str) -> bool:
    base = os.path.splitext(fname)[0].lower()
    return base in {"smartphone", slug.lower()}


def download_image(img_url: str, jpg_dir: str, fname_hint: str) -> tuple[str, int]:
    """Download `img_url` and save it into `jpg_dir` as a JPEG.

    Non-JPEG sources (e.g. GIF) are re-encoded to JPEG. Returns the saved
    filename (always `.jpg`) and the size in bytes of the file written.
    """
    req = urllib.request.Request(img_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    base = os.path.splitext(fname_hint)[0]
    out_name = f"{base}.jpg"
    dest_path = os.path.join(jpg_dir, out_name)

    with Image.open(io.BytesIO(data)) as img:
        if img.format == "JPEG":
            with open(dest_path, "wb") as f:
                f.write(data)
        else:
            img.convert("RGB").save(dest_path, "JPEG", quality=90)

    return out_name, os.path.getsize(dest_path)


def scrape_brand(brand: dict, images_root: str, verbose: bool = True) -> ScrapeResult:
    slug = brand["slug"]
    page1_url = brand.get("gsmarena_url")

    if not page1_url:
        if verbose:
            print(f"[{slug}] skipped - no gsmarena_url configured")
        return ScrapeResult(slug=slug, skipped_reason="no gsmarena_url configured")

    jpg_dir = os.path.join(images_root, slug, "jpg")
    os.makedirs(jpg_dir, exist_ok=True)

    include = brand.get("title_include", [])
    exclude = brand.get("title_exclude", [])

    if verbose:
        print(f"[{slug}] fetching page 1: {page1_url}")
    content = fetch(page1_url)
    pages = discover_pages(page1_url, content)
    if verbose:
        print(f"[{slug}] {len(pages)} page(s)")

    existing = existing_basenames(jpg_dir)
    seen_in_run: set[str] = set()
    result = ScrapeResult(slug=slug)

    for i, page_url in enumerate(pages):
        if i == 0:
            page_content = content
        else:
            time.sleep(1.5)
            try:
                page_content = fetch(page_url)
            except Exception as e:
                if verbose:
                    print(f"[{slug}]   failed to fetch {page_url}: {e}")
                continue

        for name, fname, img_url in parse_phones(page_content, include, exclude):
            base_lower = os.path.splitext(fname)[0].lower()

            if base_lower in existing or base_lower in seen_in_run:
                result.skipped += 1
                continue

            seen_in_run.add(base_lower)

            if is_placeholder(fname, slug):
                continue

            time.sleep(0.5)
            try:
                out_name, size = download_image(img_url, jpg_dir, fname)
                result.downloaded += 1
                if verbose:
                    print(f"[{slug}]   + {out_name} ({size} bytes) <- {name}")
            except Exception as e:
                result.failed += 1
                result.failed_items.append((name, fname, str(e)))
                if verbose:
                    print(f"[{slug}]   ! FAILED {fname}: {e}")

    return result
