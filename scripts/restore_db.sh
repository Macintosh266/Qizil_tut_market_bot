#!/usr/bin/env bash
# Zaxiradan bazani tiklaydi. DIQQAT: joriy bazadagi barcha ma'lumotlarni
# almashtiradi (restore avvalgi holatga qaytaradi).
#
# Ishlatish: bash scripts/restore_db.sh backups/online_market_2026-09-08_03-00-00.sql.gz

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Foydalanish: bash scripts/restore_db.sh <zaxira_fayli.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

set -a
source .env
set +a

echo "DIQQAT: bu joriy '$POSTGRES_DB' bazasidagi barcha ma'lumotlarni '$BACKUP_FILE' bilan almashtiradi."
read -p "Davom etasizmi? (ha/yo'q): " confirm
if [ "$confirm" != "ha" ]; then
    echo "Bekor qilindi."
    exit 0
fi

gunzip -c "$BACKUP_FILE" | docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Tiklandi: $BACKUP_FILE"
