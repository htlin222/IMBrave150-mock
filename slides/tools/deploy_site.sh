#!/usr/bin/env bash
# Publish the site to Cloudflare Pages.
#
#   slides/tools/deploy_site.sh
#
# Reads credentials from the repo's .env (gitignored). This repo's .env predates
# the cf-page convention and uses CF_TOKEN, so both names are accepted. The
# token is never printed.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
[ -f "$HERE/.env" ] && set -a && . "$HERE/.env" && set +a

TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_TOKEN:-}}"
ACCOUNT="${CLOUDFLARE_ACCOUNT_ID:-3a77813251d473c40d8873a59f6c0e80}"
PROJECT="${CF_PAGES_PROJECT:-imbrave150-talk}"
DIR="${CF_PAGES_DIR:-slides/site}"

[ -n "$TOKEN" ] || { echo "no API token: put CLOUDFLARE_API_TOKEN in .env"; exit 1; }

"$HERE/slides/tools/build_site.sh"

export CLOUDFLARE_API_TOKEN="$TOKEN" CLOUDFLARE_ACCOUNT_ID="$ACCOUNT"

# First run creates the project; afterwards this is a harmless failure.
npx --yes wrangler@4 pages project create "$PROJECT" \
  --production-branch=main >/dev/null 2>&1 || true

npx --yes wrangler@4 pages deploy "$HERE/$DIR" \
  --project-name="$PROJECT" --branch=main --commit-dirty=true
