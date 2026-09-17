#!/usr/bin/env bash
# Postgres bazasining kunlik zaxira nusxasini oladi (docker-compose konteyneridan),
# ixtiyoriy ravishda DigitalOcean Spaces'ga (boshqa serverga) nusxalaydi va
# 7 kundan eski LOKAL nusxalarni o'chiradi. .env shu skript bilan bir katalogda
# bo'lishi kerak.
#
# Qo'lda sinash:   bash scripts/backup_db.sh
# Cron (har kuni soat 03:00):
#   crontab -e
#   0 3 * * * /usr/bin/bash /root/qizil_tut_market_bot/scripts/backup_db.sh >> /var/log/market_backup.log 2>&1

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

set -a
source .env
set +a

BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
FILE="$BACKUP_DIR/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$FILE"

echo "Zaxira saqlandi: $FILE ($(du -h "$FILE" | cut -f1))"

# Ixtiyoriy: DigitalOcean Spaces'ga (boshqa joyga) nusxalash — faqat .env'da
# SPACES_BUCKET sozlangan bo'lsa ishga tushadi. Sozlanmagan bo'lsa, bu qadam
# jimgina o'tkazib yuboriladi — skriptning qolgan qismi buzilmaydi.
if [ -n "${SPACES_BUCKET:-}" ]; then
    if command -v aws >/dev/null 2>&1; then
        AWS_ACCESS_KEY_ID="$SPACES_ACCESS_KEY" \
        AWS_SECRET_ACCESS_KEY="$SPACES_SECRET_KEY" \
        aws s3 cp "$FILE" "s3://${SPACES_BUCKET}/db-backups/$(basename "$FILE")" \
            --endpoint-url "$SPACES_ENDPOINT" --only-show-errors
        echo "Spaces'ga nusxalandi: ${SPACES_BUCKET}/db-backups/$(basename "$FILE")"
    else
        echo "OGOHLANTIRISH: aws-cli o'rnatilmagan, Spaces'ga yuklanmadi (lokal nusxa saqlandi)." >&2
    fi
fi

# 7 kundan eski LOKAL zaxiralarni o'chirish (Spaces'dagilar bunga tegishli emas)
find "$BACKUP_DIR" -name "${POSTGRES_DB}_*.sql.gz" -mtime +7 -delete
