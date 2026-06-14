# Contributing

Thanks for considering a contribution to `device-images`! This project is a
shared collection of device product photos plus the scripts that keep it
up to date.

## Ways to contribute

### 1. Add or update a brand

1. Add/update the brand's entry in [`brands.json`](brands.json) with its
   GSMArena listing URL (page 1) and title filters:
   - `title_include`: a list of substrings — at least one must appear in a
     device's title for it to be included (e.g. `["Android smartphone"]`).
   - `title_exclude`: a list of substrings — if any appear in the title, the
     device is skipped (e.g. `["tablet", "smartwatch"]`).
2. Create the brand's folders if they don't exist:
   ```bash
   mkdir -p images/<slug>/{jpg,png,webp}
   ```
3. Run `python scripts/update.py --brands <slug>` and confirm it downloads
   images and converts them without errors.
4. Commit `brands.json`, the new `images/<slug>/...` files together.

### 2. Report or fix an incorrect/missing image

- Open an issue describing which device/brand is affected and what's wrong
  (missing, wrong device, low quality, etc.).
- If you have a fix, you can submit a PR that replaces the file(s) under
  `images/<brand>/{jpg,png,webp}/` directly — please keep the same base
  filename across all three formats, or update all three together.

### 3. Improve the scripts

- `scripts/scraper.py` — GSMArena fetching/parsing logic.
- `scripts/converter.py` — jpg → png/webp conversion.
- `scripts/update.py` — CLI orchestration.

Please keep the scripts dependency-light: standard library + Pillow only.
Use type hints for new functions, and keep the per-brand
scrape/convert/summary console output format intact, since it's relied on
for monitoring long-running updates.

## Takedown requests

If you are a rights holder and want an image removed, see the process in
[`LICENSE-IMAGES.md`](LICENSE-IMAGES.md).

## Pull request checklist

- [ ] Ran `python scripts/update.py --brands <affected-brands>` (or the full
      `--all` run for script changes) without errors
- [ ] New/changed images have matching `jpg`/`png`/`webp` versions with the
      same base filename
- [ ] `brands.json` is valid JSON (e.g. `python -m json.tool brands.json`)
