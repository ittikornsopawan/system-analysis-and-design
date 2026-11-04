-- Rollback of 09-campaign.schema.up.sql (tables dropped in reverse dependency order)

DROP TABLE IF EXISTS campaign.t_campaign_discount;

DROP TABLE IF EXISTS campaign.t_campaign_shop;

DROP TABLE IF EXISTS campaign.t_campaign_product;

DROP TABLE IF EXISTS campaign.m_campaign_budget_ledger;

-- m_campaign and m_campaign_budget reference each other, so they are dropped together
DROP TABLE IF EXISTS campaign.m_campaign_budget, campaign.m_campaign;

DROP SCHEMA IF EXISTS campaign;
