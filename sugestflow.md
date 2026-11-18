# Suggested Backend Workflow

## Current assessment

The backend has a coherent foundation for authentication and document Q&A, but it does not yet implement FocusFlow's core productivity loop: managing tasks and availability, generating schedules, tracking progress, and adapting recommendations as circumstances change.

### What is already in place

- **Authentication:** Registration stages an account until email verification. Password resets and email changes use OTPs, and token versions support invalidating existing access tokens.
- **Document Q&A:** Documents are uploaded, extracted and cleaned, split into chunks, embedded, stored in PostgreSQL with pgvector, retrieved for a query, and passed to the LLM with source information.
- **Local development:** Docker Compose starts the API, database, Redis, and frontend together.

### Main gaps

- There are no backend task, schedule, availability, or completion-history endpoints and models. The planner chat route accepts caller-supplied context instead of using persisted planner data, so it cannot yet provide the advertised adaptive planning loop.
- Document extraction and embedding run inside the upload request, which can make requests slow or prone to timeouts as files grow.
- Several RAG error cases return an `error` object with HTTP 200, making failures look successful to clients.
- Inline text ingestion has no explicit size limit, even though file uploads do.
- The SQL schema files initialize a new Docker database but do not provide a migration path for existing databases as the schema evolves.
- Authentication has access tokens but no refresh-token or session workflow.

## Recommended workflow

### 1. Build the planner domain

Persist the user-owned data the product promises to reason over:

1. Users create and update tasks with due dates, estimated effort, importance, status, and optional categories.
2. Users provide availability and scheduling preferences.
3. The planner creates schedule blocks from open tasks and available time, using a deterministic scheduling service as the first version.
4. Users complete, postpone, or edit tasks and schedule blocks.
5. Each change triggers a schedule recalculation and records enough history to explain recommendations and learn from actual completion patterns.
6. The AI assistant receives a server-built snapshot of the authenticated user's planner data, rather than arbitrary planner context supplied by the client.

Keep scheduling rules in a normal service layer so they can be tested and used without an LLM. Use the LLM to explain or refine recommendations, not as the source of truth for dates, task state, or schedule constraints.

### 2. Move document ingestion to background processing

1. Validate the upload type and size at the API boundary.
2. Store the source document and create a `processing` record.
3. Enqueue an ingestion job and return the document ID and current status.
4. A worker extracts, cleans, chunks, and embeds the document, then persists chunks and marks the document `ready`.
5. On failure, record a safe user-facing error and mark the document `failed`; keep detailed exception information in server logs.
6. Let clients poll document status or receive completion updates. Keep retrieval restricted to the authenticated user's ready documents.

Apply an equivalent explicit size limit to inline text. Preserve source titles and chunk references so answers can cite their documents reliably.

### 3. Standardize API behavior and persistence

- Return proper HTTP status codes for validation failures, missing resources, rate limits, unavailable dependencies, and unexpected failures. Keep response shapes consistent.
- Use database migrations for schema changes rather than relying only on first-start initialization scripts.
- Add connection pooling when request volume warrants it; current repository calls open and close a database connection for each operation.
- Add refresh/session support only when the product needs longer-lived sessions, with revocation and rotation rules defined explicitly.

## Suggested implementation order

1. Add database migrations and core task, availability, schedule-block, and completion models.
2. Implement authenticated CRUD endpoints and a deterministic schedule generation/recalculation service.
3. Build planner context on the server from persisted data and connect it to the AI assistant.
4. Standardize error status codes and add request-size limits, including inline text.
5. Move ingestion to a worker queue and expose processing status.
6. Add refresh/session support and operational improvements as product requirements and traffic call for them.

## Verdict

The current backend is a good prototype foundation for authentication and document Q&A. The next architectural step should be the task and scheduling data flow, because that is the missing foundation for FocusFlow's core product workflow. Background ingestion, consistent HTTP errors, bounded inputs, and schema migrations should follow as the backend grows.
