-- Rollback of 03-product.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS product.m_product_sku_option_value;

DROP TABLE IF EXISTS product.m_product_sku;

DROP TABLE IF EXISTS product.m_product_image;

DROP TABLE IF EXISTS product.m_product_option_value;

DROP TABLE IF EXISTS product.m_product_option;

DROP TABLE IF EXISTS product.m_product_attribute;

DROP TABLE IF EXISTS product.m_product;

DROP TABLE IF EXISTS product.m_product_brand;

DROP TABLE IF EXISTS product.m_product_category_attribute;

DROP TABLE IF EXISTS product.m_product_category;

DROP TABLE IF EXISTS product.m_product_type;

DROP SCHEMA IF EXISTS product;
