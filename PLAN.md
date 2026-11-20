# FocusFlow Production Plan for Render

## Summary

Prepare FocusFlow for a lean, single-region public launch **after the real planner replaces the dashboardâ€™s mock task data**. Deploy the frontend as a Render Static Site, the API as a Render Web Service, and use Render Postgres, Render Key Value, and a background worker. Keep document uploads disabled until durable object storage is configured.

## Product and API Changes

- Add authenticated task, fixed-commitment, availability, schedule-block, and completion-history data. Replace dashboard seed data and localStorage-backed task state with backend API calls; do not import demo data into production.
- Add endpoints for task CRUD, availability, schedule retrieval and recalculation, and completing or editing schedule blocks. Enforce ownership using the authenticated user on every operation.
- Build a deterministic scheduler that uses due dates, importance, estimated effort, availability, and fixed commitments. It must avoid overlapping blocks, preserve completed and manually adjusted blocks, and recalculate future unstarted blocks when relevant inputs change.
- Build planner-chat context on the server from the signed-in userâ€™s tasks and schedule. The client must not supply authoritative planner data.
- Add versioned database migrations for the existing auth/RAG schema and new planner, session, and ingestion-job tables. Run migrations as a Render pre-deploy command. [Render pre-deploy commands](https://render.com/docs/deploys)

## Render Services and Production Configuration

- Manage the deployment through a Render Blueprint: a Static Site for the Vite build, a Web Service for FastAPI, managed Postgres, a private Render Key Value instance for rate limits, and a private background worker.
- Configure the API service to bind to `0.0.0.0:$PORT`; Render web services expect the configured port, defaulting to `10000`. [Render web services](https://render.com/docs/web-services) Configure the static siteâ€™s SPA fallback and set `VITE_API_BASE_URL` to the API origin. Restrict CORS to the production and staging frontend origins.
- Use paid production Postgres so point-in-time recovery is available; create and test a restore procedure before launch. [Render Postgres recovery](https://render.com/docs/postgresql-backups) Keep Postgres and Key Value off public ingress.
- Use Key Value only for expiring rate-limit data. Store durable ingestion jobs in Postgres so queue work survives Redis-compatible cache loss; use a paid Key Value plan with cache-appropriate eviction settings. [Render Key Value](https://render.com/docs/key-value)
- Run uploaded-document extraction and embedding in the background worker. Store source files in an S3-compatible object store behind a provider-neutral adapter. Keep uploads disabled in production until the provider, credentials, access policy, and retention rules are selected and configured.
- Move production secrets into Render environment settings; remove development credential defaults from production configuration. Use a restricted database runtime role, bounded connection pooling, least-privilege service settings, pinned dependencies, and sanitized logs.
- Replace the current bearer-token persistence with short-lived access tokens held in memory and rotating refresh tokens in Secure, HttpOnly cookies. Persist refresh-token hashes and revocable session records, add CSRF protection for cookie-authenticated operations, and revoke sessions on password reset.
- Add separate staging and production environments with isolated databases, Key Value instances, secrets, and object-storage configuration. Deploy staging first, then promote the same tested revision to production.

## Acceptance and Test Plan

- Scheduler unit tests cover priority ordering, availability, fixed-event conflicts, due-date risk, timezone/DST boundaries, manual overrides, completion, and repeatable recalculation.
- Backend integration tests cover authentication and session rotation, user-to-user data isolation, task and schedule APIs, migration from an empty database, and ingestion-job retry/idempotency and failure handling.
- Frontend end-to-end flows cover signup and email verification, login/logout, password reset, creating a task, viewing and changing the generated schedule, completing a block, and asking the planner about persisted data.
- Staging smoke checks confirm static-site routing, API port and health checks, CORS and cookie behavior, SMTP delivery, database connectivity, and worker processing. Test a Postgres restore before public launch.
- Public launch is ready when planner data is server-backed, no demo tasks appear, production secrets and backups are verified, and document uploads remain disabled until object storage is configured.

## Defaults and Deferred Choice

- Default to one modest paid instance per service in one Render region; add redundancy after observing real traffic and uptime needs.
- Do not include calendar-provider integrations or adaptive machine learning in this release; use deterministic scheduling and recorded completion history.
- Object-storage vendor is intentionally deferred per your preference. The implementation must use an S3-compatible interface and must not enable public uploads until a provider is chosen.

