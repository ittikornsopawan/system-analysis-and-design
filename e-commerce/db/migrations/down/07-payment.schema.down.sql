-- Rollback of 07-payment.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS payment.t_payment;

DROP SCHEMA IF EXISTS payment;
