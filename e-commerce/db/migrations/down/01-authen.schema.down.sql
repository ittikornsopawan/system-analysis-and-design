-- Rollback of 01-authen.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS authen.t_user_refresh_token;

DROP TABLE IF EXISTS authen.t_user_access_token;

DROP TABLE IF EXISTS authen.t_user_address;

DROP TABLE IF EXISTS authen.m_user_information;

DROP TABLE IF EXISTS authen.l_user_referral;

DROP TABLE IF EXISTS authen.t_user_reset_password;

DROP TABLE IF EXISTS authen.m_user_password;

DROP TABLE IF EXISTS authen.t_user_consent;

DROP TABLE IF EXISTS authen.m_user;

DROP SCHEMA IF EXISTS authen;
