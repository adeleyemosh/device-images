# device-images

A community-maintained collection of phone & foldable device product photos,
organized by brand and available in `jpg`, `png`, and `webp` formats — ready
to use as device-identification icons in apps, websites, or anywhere else
you need a quick visual reference for a specific phone model.

This repo was created to host device images that were previously bundled
directly inside the [Siro](https://moshlabs.org) app, in order to keep the
app's download size small while still letting Siro (and other projects)
fetch device photos on demand.

## Sourcing & licensing

Images are sourced from [GSMArena](https://www.gsmarena.com/) device listing
pages (manufacturer press images). They are used here for device
identification purposes only. See [`LICENSE-IMAGES.md`](LICENSE-IMAGES.md)
for sourcing details and the takedown-request process. Code/scripts in this
repo are MIT licensed — see [`LICENSE`](LICENSE).

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
brands.json       # brand registry: GSMArena source URL + title filters
scripts/
├── scraper.py    # fetches new device photos from GSMArena
├── converter.py  # converts jpg -> png/webp
└── update.py     # master CLI: scrape + convert
```

Every device photo has the same base filename across `jpg/`, `png/`, and
`webp/` — e.g. `samsung-galaxy-s24-ultra.{jpg,png,webp}` — so consumers can
pick whichever format suits them.

## Using these images in your project

The simplest way to consume images from this repo is via the
[jsDelivr](https://www.jsdelivr.com/) CDN, which serves any file from a
GitHub repo:

```
https://cdn.jsdelivr.net/gh/<your-github-username>/device-images@main/images/<brand>/webp/<filename>.webp
```

For example:

```
https://cdn.jsdelivr.net/gh/<your-github-username>/device-images@main/images/samsung/webp/samsung-galaxy-s24-ultra.webp
```

You can swap `webp` for `jpg` or `png` depending on your needs, and pin to a
specific commit/tag instead of `@main` for stability:

```
https://cdn.jsdelivr.net/gh/<your-github-username>/device-images@<commit-sha>/images/<brand>/png/<filename>.png
```

> Replace `<your-github-username>` with the actual GitHub username/org this
> repo is published under once it has a remote.

## Updating the image set

### Requirements

- Python 3.9+
- [Pillow](https://pillow.readthedocs.io/) for image conversion

```bash
pip install -r requirements.txt
```

### Running an update

From the repo root:

```bash
# Scrape new device photos for every brand in brands.json, then convert
# any new jpgs to png/webp
python scripts/update.py --all

# Only update specific brands
python scripts/update.py --brands samsung,apple,google

# Skip scraping (e.g. you added jpgs manually) and only run conversion
python scripts/update.py --all --skip-scrape

# Skip conversion and only scrape new source jpgs
python scripts/update.py --all --skip-convert

# List all configured brands and their status
python scripts/update.py --list
```

`update.py` prints a per-brand summary (downloaded / skipped / failed images,
and converted / already-up-to-date / failed conversions), plus a final
aggregate summary. It exits with a non-zero status if any brand had a
download or conversion failure, which makes it suitable for CI/cron use.

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
   python scripts/update.py --brands my-brand
   ```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on adding/updating
brands, reporting issues with images, and code style for the scripts.

## Roadmap

- GitHub Actions workflow to run `update.py --all` on a schedule and open a
  PR with any new device images.
- Confirm the correct GSMArena source URL for the `google` brand (currently
  a placeholder in `brands.json`).
