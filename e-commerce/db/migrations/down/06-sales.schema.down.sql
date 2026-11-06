-- Rollback of 06-sales.schema.up.sql (tables dropped in reverse dependency order)
DROP TABLE IF EXISTS sales.t_order_item;

DROP TABLE IF EXISTS sales.t_order;

DROP SCHEMA IF EXISTS sales;