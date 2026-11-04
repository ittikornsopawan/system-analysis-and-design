-- Rollback of 05-cart.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS cart.t_cart;

DROP SCHEMA IF EXISTS cart;
