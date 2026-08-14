#!/usr/bin/env bash
# =============================================================================
# device-images.sh — device-images project task runner
# Usage: ./device-images.sh <command>
# =============================================================================
set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}▶  $*${RESET}"; }
success() { echo -e "${GREEN}✓  $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠  $*${RESET}"; }
err()     { echo -e "${RED}✗  $*${RESET}" >&2; exit 1; }
header()  { echo -e "\n${BOLD}${BLUE}━━━  $*  ━━━${RESET}\n"; }

VENV_DIR=".venv"
PY="${VENV_DIR}/bin/python"

# ── Helpers ───────────────────────────────────────────────────────────────────

# Verifies we are at the project root (brands.json must exist)
check_root() {
  [[ -f brands.json ]] || err "Run this script from the project root (brands.json not found)."
}

# Creates the venv (if missing) and installs/updates deps from requirements.txt
ensure_venv() {
  if [[ ! -x "$PY" ]]; then
    info "Creating virtualenv at ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR"
  fi
  "$PY" -m pip install -q --upgrade pip
  "$PY" -m pip install -q -r requirements.txt
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_help() {
  echo -e "${BOLD}device-images task runner${RESET}\n"
  echo -e "Usage:  ${CYAN}./device-images.sh <command>${RESET}\n"
  echo -e "${BOLD}Setup${RESET}"
  echo -e "  ${GREEN}setup${RESET}               Create venv + install Python deps (Pillow)"
  echo ""
  echo -e "${BOLD}Updating images${RESET}"
  echo -e "  ${GREEN}update${RESET}              Scrape new device photos for every brand, then convert + regen manifest"
  echo -e "  ${GREEN}update-marketing${RESET}    Same as update, plus refresh device_marketing_names.json"
  echo -e "  ${GREEN}scrape${RESET}              Scrape only (no format conversion)"
  echo -e "  ${GREEN}convert${RESET}             Convert only (no scraping) — regenerates png/webp + manifest"
  echo -e "  ${GREEN}brands <a,b,c>${RESET}      Update only the given comma-separated brand slugs"
  echo -e "  ${GREEN}list${RESET}                List configured brands and their GSMArena source URL"
  echo ""
}

cmd_setup() {
  header "Setting up environment"
  ensure_venv
  success "Venv ready at ${VENV_DIR} — deps installed from requirements.txt."
}

cmd_update() {
  header "Scraping + converting all brands"
  ensure_venv
  "$PY" scripts/update.py --all
  success "Update complete."
}

cmd_update_marketing() {
  header "Scraping + converting all brands (+ marketing names)"
  ensure_venv
  "$PY" scripts/update.py --all --update-marketing-names
  success "Update complete."
}

cmd_scrape() {
  header "Scraping all brands (no conversion)"
  ensure_venv
  "$PY" scripts/update.py --all --skip-convert
  success "Scrape complete."
}

cmd_convert() {
  header "Converting all brands (no scraping)"
  ensure_venv
  "$PY" scripts/update.py --all --skip-scrape
  success "Convert complete."
}

cmd_brands() {
  local slugs="${1:-}"
  [[ -n "$slugs" ]] || err "Usage: ./device-images.sh brands <slug1,slug2,...>"
  header "Updating brand(s): ${slugs}"
  ensure_venv
  "$PY" scripts/update.py --brands "$slugs"
  success "Done."
}

cmd_list() {
  ensure_venv
  "$PY" scripts/update.py --list
}

# ── Entry point ───────────────────────────────────────────────────────────────

check_root

case "${1:-help}" in
  help|--help|-h)     cmd_help ;;
  setup)               cmd_setup ;;
  update)               cmd_update ;;
  update-marketing)     cmd_update_marketing ;;
  scrape)               cmd_scrape ;;
  convert)              cmd_convert ;;
  brands)               cmd_brands "${2:-}" ;;
  list)                 cmd_list ;;
  *)                    err "Unknown command: '${1}'. Run './device-images.sh help' to see available commands." ;;
esac
