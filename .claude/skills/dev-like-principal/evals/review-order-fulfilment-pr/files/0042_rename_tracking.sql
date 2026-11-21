-- Deployed with the app via rolling deploy (old and new pods run side by side for ~10 min).
-- orders has ~12 million rows. The nightly carrier-sync job (separate service, deployed independently)
-- reads orders.tracking_no.
ALTER TABLE orders RENAME COLUMN tracking_no TO tracking_number;
