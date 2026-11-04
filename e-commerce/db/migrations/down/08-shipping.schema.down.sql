-- Rollback of 08-shipping.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS shipping.t_shipping_stop;

DROP TABLE IF EXISTS shipping.t_shipping_item;

DROP TABLE IF EXISTS shipping.t_shipping;

DROP SCHEMA IF EXISTS shipping;
