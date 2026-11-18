---
name: Newsletter subscription API spec
description: POST /newsletter/subscriptions behaviour. Approved for implementation.
status: approved
approved_by: Product Owner
approved_at: 2026-11-18T09:00:00+07:00
---

# POST /newsletter/subscriptions (anonymous)

Request: `{ "email": string, "firstName": string, "consent": boolean }`

Rules, in this order:
1. N1 `email` and `firstName` are required; `email` must be a valid email (project rule); `firstName` max 100 chars.
   Failure → 400 with one message per problem, in the project's standard validation message forms.
2. N2 `consent` must be `true` (PDPA marketing consent). Otherwise → 422 `Newsletter.ConsentRequired`.
3. N3 Email is stored normalised (project rule). If that email is already subscribed → 200 with the existing
   subscription (idempotent; no second welcome email).
4. N4 New subscription → 201 with `{ id, email, subscribedAt }` (UTC), and one welcome email is sent
   after the subscription is committed. A failed welcome email does not undo the subscription; log it.
