-- Tests for payment.t_payment: one row is one Stripe PaymentIntent, an order has at most one live payment,
-- a paid payment has its transaction time and a refunded payment has its refund details.
-- Run after 07-payment.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the columns of the payment, not the parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: a payment without the id of its provider payment is rejected, the same provider payment twice is rejected
DO $$
DECLARE
    o UUID := '11111111-1111-4111-8111-111111111111';
BEGIN
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method)
        VALUES ('test', o, NULL, 100, 'CREDIT_CARD', 'STANDARD');
        RAISE EXCEPTION 'FAIL: a payment without provider_payment_id was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method)
        VALUES ('test', o, 'pi_test_0001', 100, 'CREDIT_CARD', 'STANDARD');
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status)
        VALUES ('test', '22222222-2222-4222-8222-222222222222', 'pi_test_0001', 100, 'CREDIT_CARD', 'STANDARD', 'FAILED');
        RAISE EXCEPTION 'FAIL: the same provider_payment_id twice was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 1: provider_payment_id is required and unique';
END $$;

-- test 2: an order has at most one live payment (PENDING, PROCESSING, COMPLETED), a failed one does not count
DO $$
DECLARE
    o UUID := '33333333-3333-4333-8333-333333333333';
BEGIN
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, failure_code)
        VALUES ('test', o, 'pi_test_1001', 100, 'CREDIT_CARD', 'STANDARD', 'FAILED', 'card_declined');
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status)
        VALUES ('test', o, 'pi_test_1002', 100, 'THAI_QR', 'STANDARD', 'PENDING');
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status)
        VALUES ('test', o, 'pi_test_1003', 100, 'CREDIT_CARD', 'STANDARD', 'PROCESSING');
        RAISE EXCEPTION 'FAIL: a second live payment on one order was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE payment.t_payment SET status = 'CANCELLED' WHERE provider_payment_id = 'pi_test_1002';
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at)
        VALUES ('test', o, 'pi_test_1004', 100, 'CREDIT_CARD', 'STANDARD', 'COMPLETED', NOW());
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status)
        VALUES ('test', o, 'pi_test_1005', 100, 'CREDIT_CARD', 'STANDARD', 'PENDING');
        RAISE EXCEPTION 'FAIL: a new payment next to a COMPLETED one was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: one live payment per order';
END $$;

-- test 3: COMPLETED and REFUNDED need transaction_at
DO $$
DECLARE
    o UUID := '44444444-4444-4444-8444-444444444444';
BEGIN
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status)
        VALUES ('test', o, 'pi_test_2001', 100, 'CREDIT_CARD', 'STANDARD', 'COMPLETED');
        RAISE EXCEPTION 'FAIL: a COMPLETED payment without transaction_at was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at)
        VALUES ('test', o, 'pi_test_2002', 100, 'CREDIT_CARD', 'STANDARD', 'COMPLETED', NOW());
    RAISE NOTICE 'PASS test 3: a paid payment has transaction_at';
END $$;

-- test 4: REFUNDED needs refunded_at and provider_refund_id, and they are rejected on any other status
DO $$
DECLARE
    o UUID := '55555555-5555-4555-8555-555555555555';
BEGIN
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at)
        VALUES ('test', o, 'pi_test_3001', 100, 'CREDIT_CARD', 'STANDARD', 'REFUNDED', NOW());
        RAISE EXCEPTION 'FAIL: a REFUNDED payment without refund details was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at, refunded_at, provider_refund_id)
        VALUES ('test', o, 'pi_test_3002', 100, 'CREDIT_CARD', 'STANDARD', 'COMPLETED', NOW(), NOW(), 're_test_3002');
        RAISE EXCEPTION 'FAIL: refund details on a COMPLETED payment were accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at, refunded_at)
        VALUES ('test', o, 'pi_test_3003', 100, 'CREDIT_CARD', 'STANDARD', 'REFUNDED', NOW(), NOW());
        RAISE EXCEPTION 'FAIL: refunded_at without provider_refund_id was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, transaction_at, refunded_at, provider_refund_id, refund_reason)
        VALUES ('test', o, 'pi_test_3004', 100, 'CREDIT_CARD', 'STANDARD', 'REFUNDED', NOW(), NOW(), 're_test_3004', 'Out of stock');
    RAISE NOTICE 'PASS test 4: a refund has its details';
END $$;

-- test 5: failure details only on a FAILED payment, the currency is a 3 letter upper case code
DO $$
DECLARE
    o UUID := '66666666-6666-4666-8666-666666666666';
BEGIN
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, status, failure_code)
        VALUES ('test', o, 'pi_test_4001', 100, 'CREDIT_CARD', 'STANDARD', 'PENDING', 'card_declined');
        RAISE EXCEPTION 'FAIL: failure_code on a PENDING payment was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, currency)
        VALUES ('test', o, 'pi_test_4002', 100, 'CREDIT_CARD', 'STANDARD', 'thb');
        RAISE EXCEPTION 'FAIL: a lower case currency was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, provider)
        VALUES ('test', o, 'pi_test_4003', 100, 'CREDIT_CARD', 'STANDARD', 'PAYPAL');
        RAISE EXCEPTION 'FAIL: an unknown provider was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 5: failure details, currency and provider are checked';
END $$;

-- test 6: payments are financial history, an order with a payment cannot be deleted (RESTRICT)
DO $$
DECLARE
    d "char";
BEGIN
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'payment.t_payment'::regclass AND contype = 'f' AND confrelid = 'sales.t_order'::regclass;
    IF d IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: payment.t_payment.order_id is not ON DELETE RESTRICT (confdeltype = %)', d;
    END IF;
    RAISE NOTICE 'PASS test 6: order_id is ON DELETE RESTRICT';
END $$;

-- test 7: the shipping method is one of the three methods and the shipping fee is never negative, a fee defaults to 0
DO $$
DECLARE
    o UUID := '77777777-7777-4777-8777-777777777777';
    f NUMERIC;
BEGIN
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method)
        VALUES ('test', o, 'pi_test_5001', 100, 'CREDIT_CARD', 'DRONE');
        RAISE EXCEPTION 'FAIL: an unknown shipping method was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method, shipping_fee)
        VALUES ('test', o, 'pi_test_5002', 100, 'CREDIT_CARD', 'EXPRESS', -1);
        RAISE EXCEPTION 'FAIL: a negative shipping fee was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method)
        VALUES ('test', o, 'pi_test_5003', 100, 'CREDIT_CARD');
        RAISE EXCEPTION 'FAIL: a payment without a shipping method was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    INSERT INTO payment.t_payment (created_by, order_id, provider_payment_id, amount, payment_method, shipping_method)
    VALUES ('test', o, 'pi_test_5004', 100, 'CREDIT_CARD', 'SAME_DAY') RETURNING shipping_fee INTO f;
    IF f <> 0 THEN RAISE EXCEPTION 'FAIL: shipping_fee does not default to 0 (%)', f; END IF;
    RAISE NOTICE 'PASS test 7: shipping method and shipping fee are checked';
END $$;

ROLLBACK;
