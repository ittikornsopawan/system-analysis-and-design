-- Rollback of 00-common.schema.up.sql (the view first, then the tables in reverse dependency order)

DROP VIEW IF EXISTS consent.v_applicable_consent;

DROP TABLE IF EXISTS consent.t_consent;

DROP TABLE IF EXISTS consent.m_consent_type;

DROP TABLE IF EXISTS public.m_parameter;

DROP TABLE IF EXISTS public.t_key;

DROP SCHEMA IF EXISTS consent;
