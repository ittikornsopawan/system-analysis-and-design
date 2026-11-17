---
name: OpenAPI Contract Security Review
description: Read-only security review of the published OpenAPI 3.1 contract (authen, author, consent, product, shop, cart, sales, payment; 74 operations) against its approved API specs, with findings, severity, evidence, recommendation and the owner of each fix; read before the contract refactor, before the shipping and campaign domains are published, and before backend implementation of auth, payment or shop APIs.
---

# OpenAPI contract: security review

Date: 2026-11-17 · Reviewer: Peter (Security Auditor perspective of `.agents/agents/api-documenter.md`) · Reports to: Josh

Reviewed: `e-commerce/api/api-contract.json` on `origin/main` at `91624c0` (PR #208, 74 operations, 8 domains) against the approved specs in `e-commerce/doc/api/`. Nothing was edited: no contract, generator or spec. Shipping and campaign are not published yet and are out of scope.

## 1. Result

| Area | Result |
| --- | --- |
| Bearer auth on protected operations | PASS: all 74 operations match their spec (64 `bearerAuth`, 10 public). See 2.1 |
| Stripe webhook shape | PASS with 4 findings (F3, F4, F5, F8) |
| Secrets and personal data in examples | PASS. See 2.3 |
| Masked fields (margins, cost, user identity) | PASS for `GET /v1/shop`, storefront and shop-user. **FAIL for `GET /v1/shop/product-sku`** (F1) |
| 401/403/404 existence leaks | One leak (F2); other 404 rules match their specs |
| Rate and size limits | `pageSize` max 100 is reflected. Array and string limits are mostly missing (F7). No 429 exists in any spec (F9) |
| Ambiguity a dev may implement insecurely | F3, F4, F6, F7 |

Findings: 1 High, 4 Medium, 4 Low. Fix owner: **Marry** = generator or contract only. **Owner** = a spec change that the product owner must approve first (the contract follows after).

## 2. Checks that passed (evidence)

### 2.1 Authentication per operation

Method: for each operation, the `authorization` header row of its spec (`MANDATORY` or absent) was compared with `security` in the contract. There is no top-level `security`, so an operation is public exactly when it has no `security` key.

The 10 public operations all match a spec that says so:

| Operation | Spec evidence |
| --- | --- |
| `POST /v1/auth/register`, `POST /v1/auth/login` | no `authorization` header in the spec |
| `POST /v1/auth/refresh-token` | "No `authorization` header is required: the access token may have expired" |
| `POST /v1/auth/reset-password`, `POST /v1/auth/create-new-password` | "Public API: no `authorization` header" |
| `GET /v1/consent/active` | public consent text, no header |
| `GET /v1/storefront/product`, `/storefront/product-review`, `/storefront/shop/product` | "This API is public: it needs no access token" |
| `POST /v1/payment/webhook/stripe` | "The endpoint is public (no `authorization` header and no user) and is protected by `stripe-signature`" |

No protected operation is missing `bearerAuth`. No public operation carries it.

### 2.2 Credentials are not in URLs

No query parameter carries a token, password or reset token. The reset token, refresh token and password travel in JSON bodies. The webhook secret is not in the contract.

### 2.3 Examples

Scanned all request and response examples for JWTs, `sk_`/`whsec_` keys, signatures, emails, phone numbers and passwords. Found only placeholders: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (truncated JWT header), `rF3g7Hk9...` and `k9Vf2Tq8...` (truncated), `pi_..._secret_EXAMPLE`, `john.doe@example.com`, `Passw0rd-Example`, `NewSecret1x`, `t=...,v1=5257a869e7ec...` (truncated). No real secret or personal data.

### 2.4 Masking

| Field | Contract | Spec |
| --- | --- | --- |
| `platformMarginRate`, `shopMarginRate` in `GET /v1/shop` | `["number","null"]`, example `null` for a non-member | "Null when the caller is not an ACTIVE member of the shop and not a platform administrator" |
| Storefront product, review, shop product | no cost, margin, quantity or user fields | "It never returns the cost price, the margins, the margin rates of the shop, the quantity of a lot or the users of the shop" |
| `GET /v1/shop/user` | only `userId`, `displayName`, `profilePicturePath` | "The user name and the email address of a user are never returned" |

### 2.5 404 and 401 uniformity (as the specs require)

`POST /v1/order/cancel`, `POST /v1/payment` (start), `GET /v1/order`, `GET /v1/payment`, cart and checkout answer 404 for another user's data. Login has one 401 (E10002) for every failure, including the temporary refusal after 5 failures in 15 minutes. `reset-password` always answers 200 with one message. `create-new-password` answers one 400 for every bad-token case. All match the contract responses.

## 3. Findings

### F1 · High · `GET /v1/shop/product-sku` returns cost, margins and stock to any logged-in user

- **Operation:** `inquiryShopProductSku`, spec `shop/03-inquiry-shop-product-sku`.
- **Evidence:** the spec has no permission rule. `sequence.wsd` goes from "Access token is valid" straight to the SQL. No `shop.t_shop_user` check, no `PLATFORM_ADMIN`, no 403. The filters `id`, `shopId` and `productId` are all optional, and the lot query returns `cost_price`, `gross_margin`, `share_margin`, `platform_margin` and `quantity`. The contract mirrors this: responses `200, 400, 401, 408` only. Compare with `GET /v1/shop` (margins masked for non-members), `GET /v1/shop/user` (403 for non-members), and the storefront spec, which promises that cost and margins never leave the shop side.
- **Impact:** any registered customer can call `GET /v1/shop/product-sku` without filters and read the cost price, margins and stock of every shop. This is a business-confidential data leak and the opposite of what the other shop APIs promise.
- **Recommendation:** add the same permission model as `shop/01` (an ACTIVE `shop.t_shop_user` member of the shop, or `PLATFORM_ADMIN` in the verified `roles` claim, else 403 E10009). Decide the unfiltered call: either `shopId` becomes mandatory, or the list is limited to the shops the caller is a member of. Then the contract gets the 403 response.
- **Who fixes:** **Owner** (spec change in `shop/03` spec and sequence, then Josh/Peter update the spec, then Marry the contract). Until then a dev must not implement the API as written.

### F2 · Medium · `POST /v1/shop/payment/refund` tells a non-member whether a payment exists

- **Operation:** `refundPayment`, spec `payment/05-refund-payment`.
- **Evidence:** the sequence order is "(401) -> existence of the payment (404) -> lock the order row -> permission (403)". A payment that does not exist answers 404 E10004, an existing payment of another shop answers 403 E10009. `sales/05-cancel-order` took the safer rule: for a caller who is not the owner, a member or an administrator "the order counts as not found (404, E10004), the same answer as an order that does not exist".
- **Impact:** any logged-in user can test whether a payment UUID exists. Payment ids are random UUIDs, so the risk is low, but the two APIs behave differently for the same situation.
- **Recommendation:** use the cancel-order rule: a payment that the caller may not refund counts as not found (404). Keep 403 only for a STAFF member (who is allowed to see the payment but not to refund).
- **Who fixes:** **Owner** (spec change in `payment/05`), then Marry for the response text.
- **Related, Low:** `GET /v1/shop/order` and `GET /v1/shop/payment` answer 404 for a missing shop and 403 for a shop that exists, so `shopId` existence is visible. Shops are public on the storefront, so this is accepted. `shop/13` already hides it ("403 also when the shop does not exist"). Align it when the specs are next edited.

### F3 · Medium · The contract does not say that a signed JWT is not enough

- **Operation:** all `bearerAuth` operations (`components.securitySchemes.bearerAuth`).
- **Evidence:** the scheme says `type: http, scheme: bearer, bearerFormat: JWT` and "Access token from POST /v1/auth/login...". The specs require more: the logout, refresh and shop specs say the access token hash must match an ACTIVE stored token, the user must be ACTIVE, and roles come only from the verified `roles` claim ("do not query `author.m_role`"). None of this is in the contract.
- **Impact:** a dev who reads only the contract will use the standard ASP.NET `JwtBearer` middleware. A token that passed logout, a password reset or a refresh rotation is still cryptographically valid, so it would be accepted until it expires. Logout and "close all sessions on password reset" would not work.
- **Recommendation:** extend the `bearerAuth` description: after the signature and expiry check, the API must also check the stored credential (hash of the exact token, ACTIVE, not revoked) and that the user is ACTIVE; 401 E10002 on any failure; roles are read from the verified claim only. Mention the `roles` claim name and the `PLATFORM_ADMIN` value.
- **Who fixes:** **Marry** (generator text, no spec change).

### F4 · Medium · Authorization rules (who may call) are not in the contract

- **Operation:** all operations with a 403 or a membership rule: `author/*`, `consent/*upsert`, `product/*upsert`, `shop/*`, `payment/refund`, `GET /v1/shop/order`, `GET /v1/shop/payment` and others.
- **Evidence:** `PLATFORM_ADMIN` appears 5 times in the whole contract and only 5 operations mention a role in their 403 text. The `Domain` bullets of the specs (permission model, order of the checks, 403/404 rules) are not copied: `description` holds only the one-line `Description` row of the spec and the link `x-spec`. The only extension is `x-spec`.
- **Impact:** the contract says "401/403 possible" but not who gets 403. A dev who generates controllers from the contract will add `[Authorize]` and stop. The checks "member of the shop", "owner of the order", "PLATFORM_ADMIN" would exist only if the dev also reads each spec. Missing a membership check is the most common cause of broken access control (IDOR).
- **Recommendation:** per operation, add a short `x-authorization` extension (or a paragraph in `description`) with: required role or membership, whether the caller id comes only from the token, and the answer for a caller who is not allowed (403 or 404). Generate it from the permission bullet of each spec.
- **Who fixes:** **Marry** (generator). No spec change.

### F5 · Medium · Stripe webhook: the verification rules are in the spec but not in the contract

- **Operation:** `stripeWebhook`, spec `payment/02-stripe-webhook`.
- **Evidence:** the spec states every check: verify `stripe-signature` against the **raw body** with the signing secret, timestamp within 5 minutes, body is JSON, otherwise 400 E10001 and nothing is changed; the result is idempotent by payment state. The contract keeps only "protected by the Stripe signature" and the header description "Signature of Stripe for the raw body (timestamp t and signature v1)". The raw-body rule, the 5-minute tolerance and "nothing is changed" are missing. The operation has no `security` key (public by omission), and there is no security scheme that documents the signature.
- **Judgement of the design:** safe, because (a) public access is limited to this one endpoint and the signature is mandatory (`required: true`); (b) the spec looks the payment up by the PaymentIntent id (`provider_payment_id`), not by the `metadata` of the body; (c) state guards make a replay harmless; (d) the example response does not echo anything private.
- **Risk if implemented from the contract alone:** the typical error is to bind the body to a model (the ASP.NET model binder) and verify the signature on the re-serialised JSON. That fails for valid events and tempts the dev to skip the check. The other error is to not enforce the 5-minute tolerance.
- **Recommendation:** (1) set `security: []` explicitly on this operation; (2) copy the verification paragraph of the spec into the `description` (raw body, signing secret from configuration, 5-minute tolerance, order: verify first, then parse, then act; E10001, no change); (3) optionally add an `apiKey` security scheme in a header named `stripe-signature` so tools show the endpoint as protected; (4) add `pattern` `^t=\d+,v1=[0-9a-f]+` to the header.
- **Who fixes:** **Marry**.

### F6 · Low · Public by omission

- **Evidence:** the contract has no top-level `security`. Public operations are those without a `security` key, which is also what a forgotten key looks like. Shipping and campaign will add about 25 more operations.
- **Recommendation:** set a global `security: [{ bearerAuth: [] }]` and write `security: []` explicitly on the 10 public operations, so a missing key becomes a protected operation, and add a generator check "every operation either has security or `security: []`". The existing `check_docs.py api-contract` could also compare against the `authorization` header row of the spec (the script used for 2.1 is a small example).
- **Who fixes:** **Marry**.

### F7 · Medium · Input limits that exist in specs are not in the contract; some are missing in specs

- **Evidence (reflected):** `pageSize` has `maximum: 100` on all 22 operations that have it; `password` and `newPassword` of register and create-new-password have `minLength 8` and `maxLength 128`.
- **Evidence (not reflected):**
  - `GET /v1/checkout` `cartIds`: the spec says "at most 100 ids", the contract array has no `maxItems`.
  - 33 of 33 request arrays have no `maxItems`; only 77 of 252 request strings have `maxLength`.
  - `POST /v1/auth/login`: `password` has no `maxLength` (register allows 128). A very long password costs the password hash time on every call of an unauthenticated endpoint.
  - 44 of 45 request bodies have no `additionalProperties`, which in OpenAPI means extra properties are allowed. The specs say fields such as `userId` and `role` are never read from the request, but a generated .NET model would silently bind extra fields.
- **Evidence (missing in the specs):** the 14 `*/upsert/batch` specs do not say how many items a batch may have. A batch runs in one transaction, so a very large batch is a way to hold locks. The webhook has no body size limit.
- **Recommendation:** Marry adds `maxItems: 100` for `cartIds`, `maxLength` and `maxItems` wherever a spec states one, `maxLength: 128` for the login password, and `additionalProperties: false` for request bodies except the webhook. For batch size and the webhook body size the **owner** should decide a limit (suggestion: 100 items per batch, 64 KB for the webhook body) and Josh writes it into the specs.
- **Who fixes:** **Marry** for what the specs already state; **Owner** for batch size and body size.

### F8 · Low · Webhook payload: `additionalProperties: true` and amount check

- **Evidence:** the request schema and the nested `data`, `data.object` and `last_payment_error` objects use `additionalProperties: true`; required are `id`, `type`, `created`, `data`, `data.object.id`.
- **Judgement:** correct and necessary. Stripe adds fields at any time and the real payload has many more, so a closed schema would reject valid events. The needed fields are required. It is safe only because the signature is checked first.
- **Remaining points:**
  1. The spec never compares the event `amount` and `currency` with the stored payment. The result of a payment is taken only from this endpoint and the example shows `amount: 65700`. A check "amount and currency equal the payment" before COMPLETED would stop a wrong or mixed-up event (for example a test-mode event). Spec change: **Owner**.
  2. The example body carries `metadata.orderId` and `metadata.paymentId`. The spec correctly does not use them, but a dev may. Add the sentence "the `metadata` of the event is not trusted; the payment is found by the PaymentIntent id" to the spec description. **Owner/Josh** for the spec, then Marry.
  3. `created` is `type: number`; it is epoch seconds and should be `integer`. **Marry**.
  4. The event `livemode` is not checked. Keep test and live signing secrets per environment (DEV/QA/UAT/PRE-PROD use different secrets). A line in the dev handoff is enough.

### F9 · Low · No 429 and no rate limit outside login and reset-password

- **Evidence:** no spec and no contract response defines 429. Only two limits exist, both inside the business flow: login (5 failures in 15 minutes, then the same 401) and reset-password (3 per user per hour, same 200). Unauthenticated endpoints without any limit: `register`, `refresh-token`, `create-new-password` (token guess), the three storefront APIs, `consent/active` and the webhook.
- **Impact:** the missing limit is an infrastructure concern, but a dev reading the contract will not add one.
- **Recommendation:** the **owner** decides whether a gateway limit belongs to the contract. If yes, add a 429 `Error429` response (and `Retry-After`) to the public operations and the limits to the specs; if not, a sentence in the dev handoff that a gateway rate limit per IP is required for all public operations.
- **Who fixes:** **Owner** decision, then Josh (spec text), then Marry.

### F10 · Low · Other notes (no action needed unless the owner wants it)

- Registration answers 409 E10003 "Username or email address already exists", so registration shows whether an email is registered. This is approved by the owner (review Q3) and is the normal trade-off; login and reset do not leak.
- `timestamp` is a mandatory header on 73 operations but no spec defines a maximum clock skew. It is only a client time, never a security control; do not use it for replay protection.
- The webhook contract lists 200, 400 and 408; the spec says any other failure makes Stripe retry, so a 500 is possible. Add a generic 500 for clarity (Marry, optional).

## 4. Summary by owner of the fix

| Owner of the fix | Findings |
| --- | --- |
| **Owner** (spec change, then Josh/Peter update the specs, then Marry the contract) | F1 (High), F2, F7 batch and body limits, F8 amount check and metadata sentence, F9 |
| **Marry** (generator or contract only, no spec change) | F3, F4, F5, F6, F7 limits already in specs, F8 `created` type, F10 |

Suggested order: F1 first (it blocks the backend of shop SKU), then F3 to F5 together in the contract refactor, because they are text the generator can produce from the specs.

## 5. Not checked

- The 74 operations were compared by their authentication header and by the spec text on permissions. The SQL and the sequence diagrams were read only for the webhook, refund, cancel-order and shop product SKU.
- Shipping and campaign (not published). The author specs 13–17 were not reviewed beyond their auth rows.
- No tool was run against a live system: this is a document review.
