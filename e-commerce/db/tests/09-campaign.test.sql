-- Tests for the campaign schema: the budget of a campaign and its ledger (tests 1 to 3, foreign keys on), then the
-- rules decided in docs/superpowers/specs/2026-11-06-campaign-design.md (tests 4 to 11, C2, C3, C9 to C11).
-- Run after 09-campaign.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a budget needs an existing campaign, and the campaign no longer points back to the budget
DO $$
DECLARE c UUID := '11111111-1111-4111-8111-111111111111';
BEGIN
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 1000, 1000);
        RAISE EXCEPTION 'FAIL: a budget without a campaign was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign (id, created_by, name, start_at, end_at) VALUES (c, 'test', 'Black Friday', NOW(), NOW() + INTERVAL '1 day');
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 1000, 1000);
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
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, -1, 0);
        RAISE EXCEPTION 'FAIL: a negative budget was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 500, 500);
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

-- The rules below only look at the columns of the campaign tables, so the foreign keys are switched off for the fixture
-- rows (session_replication_role = replica). The ON DELETE rules are checked through pg_constraint in test 11.
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 4: a campaign ends after it starts
DO $$
BEGIN
    BEGIN
        INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Same time', '2026-11-10 00:00', '2026-11-10 00:00');
        RAISE EXCEPTION 'FAIL: a campaign that ends when it starts was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Backwards', '2026-11-10 00:00', '2026-11-09 23:59');
        RAISE EXCEPTION 'FAIL: a campaign that ends before it starts was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'One minute', '2026-11-10 00:00', '2026-11-10 00:01');
    RAISE NOTICE 'PASS test 4: end_at is after start_at';
END $$;

-- test 5: the campaign name is unique among rows that are not DELETED
DO $$
BEGIN
    INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Mega Sale', NOW(), NOW() + INTERVAL '1 day');
    BEGIN
        INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Mega Sale', NOW(), NOW() + INTERVAL '1 day');
        RAISE EXCEPTION 'FAIL: a duplicate campaign name was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.m_campaign SET row_status = 'ARCHIVED' WHERE name = 'Mega Sale';
    BEGIN
        INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Mega Sale', NOW(), NOW() + INTERVAL '1 day');
        RAISE EXCEPTION 'FAIL: the name of an ARCHIVED campaign was reused';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.m_campaign SET row_status = 'DELETED' WHERE name = 'Mega Sale';
    INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Mega Sale', NOW(), NOW() + INTERVAL '1 day');
    UPDATE campaign.m_campaign SET row_status = 'DELETED' WHERE name = 'Mega Sale';
    INSERT INTO campaign.m_campaign (created_by, name, start_at, end_at) VALUES ('test', 'Mega Sale', NOW(), NOW() + INTERVAL '1 day');
    RAISE NOTICE 'PASS test 5: campaign name unique among non deleted rows';
END $$;

-- test 6: the budget keeps a remaining amount between 0 and the budget, one live budget per campaign
DO $$
DECLARE c UUID := '66666666-6666-4666-8666-666666666666';
BEGIN
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 100, -0.01);
        RAISE EXCEPTION 'FAIL: a negative remaining amount was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 100, 100.01);
        RAISE EXCEPTION 'FAIL: a remaining amount above the budget was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 100, 100);
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 50, 50);
        RAISE EXCEPTION 'FAIL: a second live budget of the same campaign was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- an INACTIVE budget still holds the place, only DELETED frees it
    UPDATE campaign.m_campaign_budget SET row_status = 'INACTIVE' WHERE campaign_id = c;
    BEGIN
        INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 50, 50);
        RAISE EXCEPTION 'FAIL: a second budget was accepted while the first one is INACTIVE';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.m_campaign_budget SET row_status = 'DELETED' WHERE campaign_id = c;
    INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining) VALUES ('test', c, 50, 0);
    RAISE NOTICE 'PASS test 6: remaining between 0 and budget, one live budget per campaign';
END $$;

-- test 7: a ledger row says what it is (RESERVE or RELEASE) and for which order, once per budget, order and type
DO $$
DECLARE
    b UUID := '77777777-7777-4777-8777-777777777771'; c UUID := '77777777-7777-4777-8777-777777777772';
    o UUID := '77777777-7777-4777-8777-777777777773';
BEGIN
    INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
    VALUES ('test', b, c, o, 'RESERVE', '[]', 40.00, 60.00);
    INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
    VALUES ('test', b, c, o, 'RELEASE', '[]', 40.00, 100.00);
    BEGIN
        INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
        VALUES ('test', b, c, o, 'RESERVE', '[]', 40.00, 60.00);
        RAISE EXCEPTION 'FAIL: the same order reserved the same budget twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
        VALUES ('test', b, c, '77777777-7777-4777-8777-777777777774', 'REFUND', '[]', 1, 1);
        RAISE EXCEPTION 'FAIL: an unknown ledger entry type was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, entry_type, reference, usage, remaining)
        VALUES ('test', b, c, 'RESERVE', '[]', 1, 1);
        RAISE EXCEPTION 'FAIL: a ledger row without an order was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    -- the same order may use another budget
    INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
    VALUES ('test', '77777777-7777-4777-8777-777777777775', c, o, 'RESERVE', '[]', 10, 90);
    RAISE NOTICE 'PASS test 7: ledger entry type, order and one row per budget, order and type';
END $$;

-- test 8: a campaign product row names a product or a category, never both, never none, and not twice
DO $$
DECLARE
    c UUID := '88888888-8888-4888-8888-888888888881'; p UUID := '88888888-8888-4888-8888-888888888882';
    k UUID := '88888888-8888-4888-8888-888888888883';
BEGIN
    BEGIN
        INSERT INTO campaign.t_campaign_product (created_by, campaign_id) VALUES ('test', c);
        RAISE EXCEPTION 'FAIL: a campaign product with neither product nor category was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_id, product_category_id) VALUES ('test', c, p, k);
        RAISE EXCEPTION 'FAIL: a campaign product with both product and category was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_id) VALUES ('test', c, p);
    INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_category_id) VALUES ('test', c, k);
    BEGIN
        INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_id) VALUES ('test', c, p);
        RAISE EXCEPTION 'FAIL: the same product twice in a campaign was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_category_id) VALUES ('test', c, k);
        RAISE EXCEPTION 'FAIL: the same category twice in a campaign was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.t_campaign_product SET row_status = 'DELETED' WHERE campaign_id = c;
    INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_id) VALUES ('test', c, p);
    INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_category_id) VALUES ('test', c, k);
    -- the same product in another campaign is fine
    INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_id) VALUES ('test', '88888888-8888-4888-8888-888888888884', p);
    RAISE NOTICE 'PASS test 8: campaign product target and uniqueness';
END $$;

-- test 9: a shop joins a campaign once among rows that are not DELETED
DO $$
DECLARE
    c UUID := '99999999-9999-4999-8999-999999999991'; s UUID := '99999999-9999-4999-8999-999999999992';
BEGIN
    INSERT INTO campaign.t_campaign_shop (created_by, campaign_id, shop_id) VALUES ('test', c, s);
    BEGIN
        INSERT INTO campaign.t_campaign_shop (created_by, campaign_id, shop_id) VALUES ('test', c, s);
        RAISE EXCEPTION 'FAIL: the same shop twice in a campaign was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.t_campaign_shop SET row_status = 'DELETED' WHERE campaign_id = c AND shop_id = s;
    INSERT INTO campaign.t_campaign_shop (created_by, campaign_id, shop_id) VALUES ('test', c, s);
    INSERT INTO campaign.t_campaign_shop (created_by, campaign_id, shop_id) VALUES ('test', '99999999-9999-4999-8999-999999999993', s);
    RAISE NOTICE 'PASS test 9: one row per shop and campaign among non deleted rows';
END $$;

-- test 10: a discount is positive, a percentage is at most 100, one live discount per campaign
DO $$
DECLARE c UUID := 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1';
BEGIN
    BEGIN
        INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value) VALUES ('test', c, 'FIXED_AMOUNT', 0);
        RAISE EXCEPTION 'FAIL: a discount of 0 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value) VALUES ('test', c, 'PERCENTAGE', 100.01);
        RAISE EXCEPTION 'FAIL: a percentage above 100 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value) VALUES ('test', c, 'PERCENTAGE', 100);
    BEGIN
        INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value) VALUES ('test', c, 'FIXED_AMOUNT', 50);
        RAISE EXCEPTION 'FAIL: a second live discount of the same campaign was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE campaign.t_campaign_discount SET row_status = 'DELETED' WHERE campaign_id = c;
    -- a fixed amount may be larger than 100 baht
    INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value) VALUES ('test', c, 'FIXED_AMOUNT', 500);
    RAISE NOTICE 'PASS test 10: discount value and one live discount per campaign';
END $$;

-- test 11: an order that used a budget cannot be deleted (RESTRICT), the ledger follows its budget and campaign (CASCADE)
DO $$
DECLARE d "char";
BEGIN
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'campaign.m_campaign_budget_ledger'::regclass AND contype = 'f' AND confrelid = 'sales.t_order'::regclass;
    IF d IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: m_campaign_budget_ledger.order_id must be ON DELETE RESTRICT, found %', d;
    END IF;
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'campaign.m_campaign_budget_ledger'::regclass AND contype = 'f' AND confrelid = 'campaign.m_campaign_budget'::regclass;
    IF d IS DISTINCT FROM 'c' THEN
        RAISE EXCEPTION 'FAIL: m_campaign_budget_ledger.campaign_budget_id must be ON DELETE CASCADE, found %', d;
    END IF;
    RAISE NOTICE 'PASS test 11: ledger order is ON DELETE RESTRICT, ledger budget is CASCADE';
END $$;

ROLLBACK;
