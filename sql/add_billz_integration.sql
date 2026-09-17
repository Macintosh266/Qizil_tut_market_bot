-- =====================================================================
-- Qizil Tut Market Bot — Billz.io integratsiyasi uchun migratsiya.
--
-- Bu skript IDEMPOTENT — bir necha marta ishga tushirsangiz ham xato
-- bermaydi (IF NOT EXISTS tekshiruvlari bilan himoyalangan).
--
-- Ishga tushirish:
--   psql -U <user> -d <database> -f sql/add_billz_integration.sql
-- yoki Docker orqali:
--   docker exec -i <postgres_container> psql -U <user> -d <database> < sql/add_billz_integration.sql
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 1) markets.billz_shop_id (eski, endi ishlatilmaydi, lekin zararsiz) va
--    markets.billz_secret_key — HAR BIR do'konning o'z Billz API kaliti
--    (chunki har bir do'kon Billz'da alohida akkauntga ega)
-- ---------------------------------------------------------------------
ALTER TABLE markets
    ADD COLUMN IF NOT EXISTS billz_shop_id VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS ux_markets_billz_shop_id
    ON markets (billz_shop_id) WHERE billz_shop_id IS NOT NULL;

ALTER TABLE markets
    ADD COLUMN IF NOT EXISTS billz_secret_key VARCHAR(512);

-- Agar bu ustun avvalroq VARCHAR(255) sifatida yaratilgan bo'lsa (shifrlash
-- funksiyasi qo'shilishidan oldin), kengaytiramiz — shifrlangan qiymat asl
-- kalitdan uzunroq bo'lishi mumkin:
ALTER TABLE markets
    ALTER COLUMN billz_secret_key TYPE VARCHAR(512);

-- ---------------------------------------------------------------------
-- 2) products.billz_product_id — Billz'dan kelgan mahsulotni aniqlash
--    (qo'lda qo'shilgan mahsulotlarda bu ustun NULL bo'lib qoladi)
-- ---------------------------------------------------------------------
ALTER TABLE products
    ADD COLUMN IF NOT EXISTS billz_product_id VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS ux_products_billz_product_id
    ON products (billz_product_id) WHERE billz_product_id IS NOT NULL;

COMMIT;

-- =====================================================================
-- Tekshirish (ixtiyoriy):
--   \d markets
--   \d products
-- =====================================================================
