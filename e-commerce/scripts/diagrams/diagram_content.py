"""Shared row/box/link builders and the earlier order-lifecycle view content."""

SANS, MONO = "sans", "mono"


def row(text, role=SANS):
    return (text, role)


def box(key, x, y, w, h, title, tag, rows, kind="backend", refs=None):
    return dict(id=key, x=x, y=y, w=w, h=h, title=title, tag=tag,
                rows=rows, kind=kind, refs=refs)


def link(source, target, points, label=None, color="muted", dashed=False):
    return dict(source=source, target=target, points=points,
                label=label, color=color, dashed=dashed)


SYSTEM = dict(
    slug="system-design", title="Order lifecycle & proposed data boundaries",
    type="State Machine", pattern="Lifecycle phase map",
    eyebrow="E-COMMERCE / 03 / SPECIFIED BUSINESS BEHAVIOR",
    subtitle="Existing SQL business states · proposed Redis admission/cache, MongoDB config and asynchronous audit/transaction projections.",
    desc="An order advances through waiting for payment, payment confirmation, processing and completion, with guarded cancellation, refund, retry and recovery paths and explicit stock and budget effects.",
    nodes=[
        box("wait",104,360,288,216,"Awaiting payment","WAIT_PAYMENT",[
            row("sales/02 · customer checkout",MONO),
            row("One order per selected shop"),
            row("Price, lot and address snapshotted"),
            row("Reserve stock + campaign budget"),
            row("Configured payment window: 30 min default"),
            row("Purchased cart rows deleted in same TX"),
            row("Only a webhook can confirm payment"),
        ],"state"),
        box("paid",488,360,288,216,"Payment confirmed","PAYMENT_CONFIRMED",[
            row("payment/02 · signed Stripe success",MONO),
            row("Payment COMPLETED; order now paid"),
            row("Guard: order is still WAIT_PAYMENT"),
            row("Accept success if stock is still held"),
            row("Shipping has not started"),
            row("Whole-payment refund is allowed here"),
            row("The browser is not payment truth"),
        ],"state"),
        box("processing",872,360,288,216,"Fulfilling the order","PROCESSING",[
            row("shipping/01 · shop member/admin",MONO),
            row("First PENDING parcel starts this phase"),
            row("Split parcels; assigned qty ≤ item qty"),
            row("Shop records SHIPPED + tracking"),
            row("Receiver or eligible system completion"),
            row("More parcels keep order PROCESSING"),
            row("Cancelled/returned parcels can reopen"),
        ],"state"),
        box("complete",1256,360,288,216,"Order completed","COMPLETED / HAPPY TERMINAL",[
            row("shipping/06 · owner / system",MONO),
            row("Owner confirms SHIPPED parcels"),
            row("System: eligible orders after 7 days"),
            row("No PENDING; all item qty allocated"),
            row("All remaining SHIPPED aged >= 7d"),
            row("Partial / unshipped stays PROCESSING"),
            row("Every active item fully DELIVERED"),
            row("Allows purchased-product review"),
            row("No campaign-budget release"),
        ],"focal"),
        box("cancelled",104,744,288,232,"Order cancelled","CANCELLED / ALTERNATE TERMINAL",[
            row("sales/05 · owner/shop/admin/expiry",MONO),
            row("Only WAIT_PAYMENT may be cancelled"),
            row("Payment PROCESSING blocks this path"),
            row("Cancel PENDING PaymentIntent"),
            row("Restore quantities to original lots"),
            row("Release budget; append RELEASE ledger"),
            row("Keep order and items as history"),
            row("Repeat → 409; no double stock release"),
        ],"terminal"),
        box("refunded",488,744,288,232,"Order refunded","REFUNDED / ALTERNATE TERMINAL",[
            row("payment/05 or payment/02 refund event",MONO),
            row("Order must be PAYMENT_CONFIRMED"),
            row("Payment must already be COMPLETED"),
            row("Shop member / admin requests API refund"),
            row("Refund whole amount including shipping"),
            row("Restore stock to original lots"),
            row("Release campaign reservations once"),
            row("No partial refund / return flow here"),
        ],"terminal"),
    ],
    zones=[
        (40,160,1504,152,"WAIT / RETRY / GUARDED RECOVERY", "recovery"),
        (40,704,1504,304,"ALTERNATE OUTCOMES", "outcome"),
    ],
    start=(56,468),
    edges=[
        link(None,"wait",[(62,468),(104,468)],(80,452,"CREATE")),
        link("wait","paid",[(392,468),(488,468)],(440,452,"WEBHOOK OK")),
        link("paid","processing",[(776,468),(872,468)],(824,452,"FIRST PARCEL")),
        link("processing","complete",[(1160,468),(1256,468)],(1208,452,"ALL DELIVERED")),
        link("wait","cancelled",[(248,576),(248,744)],(298,652,"EXPIRE/CANCEL")),
        link("paid","refunded",[(632,576),(632,744)],(676,652,"FULL REFUND")),
        link("processing","paid",[(1016,360),(1016,232),(632,232),(632,360)],(824,216,"NO LIVE PARCEL"),dashed=True),
        link("wait","wait",[(200,360),(200,264),(296,264),(296,360)],(248,248,"PAYMENT RETRY"),dashed=True),
    ],
    notes=[
        (56,200,"Payment failure / cancellation",11,"body"),
        (56,220,"leaves the order WAIT_PAYMENT.",11,"body"),
        (56,240,"Retry creates or reuses an intent.",11,"body"),
        (56,280,"Expiry waits during",11,"body"),
        (56,300,"payment processing.",11,"body"),
        (1080,200,"Reopen paid phase only when no parcel",11,"body"),
        (1080,220,"is PENDING, SHIPPED or DELIVERED.",11,"body"),
        (1080,244,"Cancelled / returned parcels free their",11,"body"),
        (1080,264,"assigned quantities for a new parcel.",11,"body"),
        (872,616,"Primary rail: sales.t_order states. Payment and parcel states are separate.",11,"body"),
        (872,640,"Delivery: receiver confirmation or guarded 7-day system job (shipping/06).",11,"body"),
        (872,752,"Redis / MongoDB boundaries (PROPOSED)",14,"heading"),
        (872,784,"Redis quota gate before CREATE: 429 / protected outage 503 writes no order.",11,"body"),
        (872,808,"SQL source + outbox intent commit; then invalidate cache and relay event copies.",11,"body"),
        (872,832,"MongoDB: versioned config and audit/projections; no shared cross-store commit.",11,"body"),
        (872,856,"Live stock, payable price, payment state and permission authority stay SQL.",11,"body"),
        (872,880,"Cancel/refund restores once. Lock order: order row → lots → budgets.",11,"body"),
        (872,904,"Late money after cancel: refund payment; never release stock/budget twice.",11,"body"),
        (872,928,"Signed webhooks bypass user Redis quotas; SQL idempotency stays authoritative.",11,"body"),
        (872,952,"MongoDB outage queues publication intent; replay never repeats the business write.",11,"body"),
        (872,976,"Post-shipping refunds remain manual follow-up; neither store adds an order state.",11,"body"),
    ],
    source="Existing: sales/02,05 · payment/01,02,05 · shipping/01,02,06 · campaign C2–C9 | In-review boundaries: redis-design.md + mongodb-design.md",
    legend=[("state","Persisted order state"),("focal","Completed order"),("terminal","Alternate terminal"),("arrow","Guarded status transition"),("dashed","Retry / recovery route")],
)


DIAGRAMS = [SYSTEM]
