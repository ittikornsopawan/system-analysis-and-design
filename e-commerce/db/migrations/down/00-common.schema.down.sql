-- Rollback of 00-common.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS consent.t_consent;

DROP TABLE IF EXISTS consent.m_consent_type;

DROP TABLE IF EXISTS public.t_key;

DROP SCHEMA IF EXISTS consent;
