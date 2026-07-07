#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FEISHU2MD="${FEISHU2MD:-/Users/huang/Downloads/free_download_manager/feishu2md-v2.4.5-darwin-arm64/feishu2md}"
MANIFEST="${MANIFEST:-${ROOT_DIR}/feishu-export/links.tsv}"
DOWNLOAD_ROOT="${DOWNLOAD_ROOT:-/Users/huang/Downloads/feishu}"
FEISHU_SOURCE="${FEISHU_SOURCE:-${DOWNLOAD_ROOT}/学习笔记}"
HUGO_DOCS="${HUGO_DOCS:-${ROOT_DIR}/content/zh/docs}"

cd "${ROOT_DIR}"

python3 feishu-export/download_feishu.py \
  --manifest "${MANIFEST}" \
  --output "${DOWNLOAD_ROOT}" \
  --feishu2md "${FEISHU2MD}"

python3 feishu-export/migrate_to_hugo.py \
  --source "${FEISHU_SOURCE}" \
  --dest "${HUGO_DOCS}" \
  --clean

bash feishu-export/deploy_site.sh
