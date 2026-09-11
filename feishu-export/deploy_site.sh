#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUBLIC_DIR="${ROOT_DIR}/public"
PUBLIC_BRANCH="${PUBLIC_BRANCH:-master}"
SOURCE_BRANCH="${SOURCE_BRANCH:-$(git -C "${ROOT_DIR}" branch --show-current)}"
PUBLIC_COMMIT_MSG="${PUBLIC_COMMIT_MSG:-deploy: publish Feishu docs}"
SOURCE_COMMIT_MSG="${SOURCE_COMMIT_MSG:-docs: sync Feishu notes}"

cd "${ROOT_DIR}"
hugo --destination public --cleanDestinationDir --gc --minify

if [[ ! -d "${PUBLIC_DIR}/.git" ]]; then
  echo "public/ is not a git repository" >&2
  exit 1
fi

git -C "${PUBLIC_DIR}" add -A
if git -C "${PUBLIC_DIR}" diff --cached --quiet; then
  echo "public/: no changes to commit"
else
  git -C "${PUBLIC_DIR}" commit -m "${PUBLIC_COMMIT_MSG}"
  git -C "${PUBLIC_DIR}" push origin "${PUBLIC_BRANCH}"
fi

git -C "${ROOT_DIR}" add hugo.toml content/zh/docs public feishu-export
if git -C "${ROOT_DIR}" diff --cached --quiet; then
  echo "source: no changes to commit"
else
  git -C "${ROOT_DIR}" commit -m "${SOURCE_COMMIT_MSG}"
  git -C "${ROOT_DIR}" push origin "${SOURCE_BRANCH}"
fi
