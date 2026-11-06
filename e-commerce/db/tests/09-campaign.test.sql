-- Tests for campaign.m_campaign_budget (the budget of a campaign) and its ledger.
-- Run after 09-campaign.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a budget needs an existing campaign, and the campaign no longer points back to the budget
DO $$
DECLARE c UUID := '11111111-1111-4111-8111-111111111111';
BEGIN
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget) VALUES ('test', c, 1000);
        RAISE EXCEPTION 'FAIL: a budget without a campaign was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign (id, created_by, name, start_at, end_at) VALUES (c, 'test', 'Black Friday', NOW(), NOW() + INTERVAL '1 day');
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget) VALUES ('test', c, 1000);
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'campaign' AND table_name = 'm_campaign' AND column_name = 'budget_id') THEN
        RAISE EXCEPTION 'FAIL: campaign.m_campaign still has budget_id';
    END IF;
    RAISE NOTICE 'PASS test 1: budget belongs to a campaign, no circular reference';
END $$;

-- test 2: the budget cannot be negative and deleting the campaign removes its budgets
DO $$
DECLARE c UUID := '22222222-2222-4222-8222-222222222222';
BEGIN
    INSERT INTO campaign.m_campaign (id, created_by, name, start_at, end_at) VALUES (c, 'test', 'Cyber Monday', NOW(), NOW() + INTERVAL '1 day');
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget) VALUES ('test', c, -1);
        RAISE EXCEPTION 'FAIL: a negative budget was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget) VALUES ('test', c, 500);
    DELETE FROM campaign.m_campaign WHERE id = c;
    IF EXISTS (SELECT 1 FROM campaign.m_campaign_budget WHERE campaign_id = c) THEN
        RAISE EXCEPTION 'FAIL: the budget stayed after its campaign was deleted';
    END IF;
    RAISE NOTICE 'PASS test 2: budget check and cascade from campaign';
END $$;

-- test 3: no foreign key in the campaign schema is deferrable (nothing circular is left)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace
               WHERE n.nspname = 'campaign' AND c.contype = 'f' AND c.condeferrable) THEN
        RAISE EXCEPTION 'FAIL: a campaign foreign key is deferrable';
    END IF;
    RAISE NOTICE 'PASS test 3: all campaign foreign keys are plain';
END $$;

ROLLBACK;
