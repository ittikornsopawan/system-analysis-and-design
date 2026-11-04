-- Rollback of 06-order.schema.up.sql (tables dropped in reverse dependency order)
DROP TABLE IF EXISTS order.t_order_item;

DROP TABLE IF EXISTS order.t_order;

DROP SCHEMA IF EXISTS order;