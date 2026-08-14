# device-images

[![License: MIT](https://img.shields.io/github/license/adeleyemosh/device-images?color=blue)](LICENSE)
[![Brands](https://img.shields.io/badge/brands-39-blue)](brands.json)
[![Images](https://img.shields.io/badge/images-6%2C069-blue)](manifest.json)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](requirements.txt)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

A community-maintained collection of phone & foldable device product photos,
organized by brand and available in `jpg`, `png`, and `webp` formats — ready
to use as device-identification icons in apps, websites, or anywhere else
you need a quick visual reference for a specific phone model.

This repo was created to host device images that were previously bundled
directly inside the [Siro](https://moshlabs.org) app, in order to keep the
app's download size small while still letting Siro (and other projects)
fetch device photos on demand.

## Contents

- [Using these images in your project](#using-these-images-in-your-project)
- [Brand coverage](#brand-coverage)
- [Directory structure](#directory-structure)
- [Sourcing & licensing](#sourcing--licensing)
- [Updating the image set](#updating-the-image-set)
- [Adding a new brand](#adding-a-new-brand)
- [Contributing](#contributing)
- [Roadmap](#roadmap)

## Using these images in your project

The simplest way to consume images from this repo is via the
[jsDelivr](https://www.jsdelivr.com/) CDN, which serves any file from a
GitHub repo:

```
https://cdn.jsdelivr.net/gh/adeleyemosh/device-images@main/images/<brand>/webp/<filename>.webp
```

For example:

```
https://cdn.jsdelivr.net/gh/adeleyemosh/device-images@main/images/samsung/webp/samsung-galaxy-s24-ultra.webp
```

You can swap `webp` for `jpg` or `png` depending on your needs, and pin to a
specific commit/tag instead of `@main` for stability:

```
https://cdn.jsdelivr.net/gh/adeleyemosh/device-images@<commit-sha>/images/<brand>/png/<filename>.png
```

Every device photo has the same base filename across `jpg/`, `png/`, and
`webp/` — e.g. `samsung-galaxy-s24-ultra.{jpg,png,webp}` — so consumers can
pick whichever format suits them. [`manifest.json`](manifest.json) lists
every available `brand/filename` pair, and
[`device_marketing_names.json`](device_marketing_names.json) maps raw
Android model codes (e.g. `sm-s928b`) to marketing names (e.g.
`Galaxy S24 Ultra`) for the brands Google's Play device catalog covers.

## Brand coverage

39 brands, 6,069 device photos, refreshed by periodic GSMArena rescans.

| Brand | Photos | Brand | Photos | Brand | Photos |
|---|---:|---|---:|---|---:|
| Samsung | 549 | Infinix | 158 | Cubot | 70 |
| Vivo | 501 | Alcatel | 149 | TCL | 70 |
| Xiaomi | 420 | Lenovo | 148 | Umidigi | 66 |
| Motorola | 360 | Ulefone | 121 | Coolpad | 56 |
| ZTE | 349 | Sony | 109 | Philips | 56 |
| Oppo | 336 | Asus | 107 | Itel | 54 |
| Honor | 269 | Doogee | 105 | Apple | 53 |
| LG | 266 | Oukitel | 93 | Sharp | 45 |
| Realme | 248 | Blackview | 92 | Google | 44 |
| Huawei | 234 | Gionee | 89 | Oscal | 20 |
| HTC | 200 | Nokia | 88 | Nothing | 13 |
| Tecno | 185 | OnePlus | 84 | Fairphone | 5 |
| Micromax | 180 | Meizu | 74 | RugOne | 3 |

Full per-brand source config lives in [`brands.json`](brands.json); the
canonical, always-current counts are in [`manifest.json`](manifest.json).

## Directory structure

```
images/
├── samsung/
│   ├── jpg/
│   │   └── samsung-galaxy-s24-ultra.jpg
│   ├── png/
│   │   └── samsung-galaxy-s24-ultra.png
│   └── webp/
│       └── samsung-galaxy-s24-ultra.webp
├── apple/
│   ├── jpg/
│   ├── png/
│   └── webp/
├── ... (one folder per brand)
brands.json                    # brand registry: GSMArena source URL + title filters
manifest.json                  # generated catalog of every available brand/filename pair
device_marketing_names.json    # generated model-code -> marketing-name mapping
device-images.sh               # task runner: setup / update / scrape / convert / list
scripts/
├── scraper.py                 # fetches new device photos from GSMArena
├── converter.py                # converts jpg -> png/webp
├── generate_manifest.py        # regenerates manifest.json
├── fetch_marketing_names.py    # regenerates device_marketing_names.json
└── update.py                   # master CLI: scrape + convert + manifest + marketing names
```

## Sourcing & licensing

Images are sourced from [GSMArena](https://www.gsmarena.com/) device listing
pages (manufacturer press images). They are used here for device
identification purposes only. See [`LICENSE-IMAGES.md`](LICENSE-IMAGES.md)
for sourcing details and the takedown-request process. Code/scripts in this
repo are MIT licensed — see [`LICENSE`](LICENSE).

## Updating the image set

### Requirements

- Python 3.9+
- [Pillow](https://pillow.readthedocs.io/) for image conversion

### Quick start: `device-images.sh`

The included task runner manages a local `.venv` for you — no manual
`pip install`, no polluting your system Python:

```bash
./device-images.sh setup             # create .venv + install Pillow
./device-images.sh update            # scrape all brands, convert, regen manifest.json
./device-images.sh update-marketing  # same as update, plus refresh device_marketing_names.json
./device-images.sh scrape            # scrape only, skip conversion
./device-images.sh convert           # convert only, skip scraping
./device-images.sh brands samsung,apple,google   # update specific brands only
./device-images.sh list              # list configured brands + GSMArena source URLs
./device-images.sh help              # full command reference
```

`update`/`scrape`/`convert`/`brands` all print a per-brand summary
(downloaded / skipped / failed images, converted / already-up-to-date /
failed conversions) plus a final aggregate summary, and exit non-zero if
any brand had a failure — safe for CI/cron use.

### Calling the Python scripts directly

If you'd rather manage your own virtualenv:

```bash
pip install -r requirements.txt

# Scrape new device photos for every brand in brands.json, then convert
# any new jpgs to png/webp
python scripts/update.py --all

# Only update specific brands
python scripts/update.py --brands samsung,apple,google

# Skip scraping (e.g. you added jpgs manually) and only run conversion
python scripts/update.py --all --skip-scrape

# Skip conversion and only scrape new source jpgs
python scripts/update.py --all --skip-convert

# Also refresh device_marketing_names.json from Google's Play device catalog
python scripts/update.py --all --update-marketing-names

# List all configured brands and their status
python scripts/update.py --list
```

## Adding a new brand

1. Add an entry to [`brands.json`](brands.json):
   ```jsonc
   {
     "slug": "my-brand",
     "name": "My Brand",
     "gsmarena_url": "https://www.gsmarena.com/my-brand-phones-NN.php",
     "title_include": ["Android smartphone"],
     "title_exclude": []
   }
   ```
2. Create the brand's image folders:
   ```bash
   mkdir -p images/my-brand/{jpg,png,webp}
   ```
3. Run the updater for just that brand:
   ```bash
   ./device-images.sh brands my-brand
   ```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on adding/updating
brands, reporting issues with images, and code style for the scripts.

## Roadmap

- GitHub Actions workflow to run `./device-images.sh update` on a schedule
  and open a PR with any new device images.
