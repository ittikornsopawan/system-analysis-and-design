-- Rollback of 02-author.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS author.t_user_permission;

DROP TABLE IF EXISTS author.t_user_role;

DROP TABLE IF EXISTS author.t_role_permission_scope;

DROP TABLE IF EXISTS author.t_role_permission;

DROP TABLE IF EXISTS author.t_permission_scope;

DROP TABLE IF EXISTS author.m_scope;

DROP TABLE IF EXISTS author.m_permission;

DROP TABLE IF EXISTS author.m_role;

DROP SCHEMA IF EXISTS author;
