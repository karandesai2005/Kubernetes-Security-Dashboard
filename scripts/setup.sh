#!/usr/bin/env bash
set -euo pipefail

echo "==> Copying env files"
cp -n .env.example .env || true
cp -n frontend/.env.example frontend/.env.local || true

echo "==> Done. Run: make dev"
