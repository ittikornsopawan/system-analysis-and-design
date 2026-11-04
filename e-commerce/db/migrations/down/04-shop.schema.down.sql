-- Rollback of 04-shop.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS shop.t_shop_user;

DROP TABLE IF EXISTS shop.t_shop_product_review;

DROP TABLE IF EXISTS shop.t_shop_product_sku;

DROP TABLE IF EXISTS shop.t_shop_product;

DROP TABLE IF EXISTS shop.m_shop_image;

DROP TABLE IF EXISTS shop.m_shop;

DROP TABLE IF EXISTS shop.m_shop_type;

DROP SCHEMA IF EXISTS shop;
