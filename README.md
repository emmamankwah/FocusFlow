# FocusFlow AI

FocusFlow AI is a productivity platform for students and professionals. It aims to help people organize work, decide what matters next, and build schedules that adapt as deadlines and workloads change.

## Why FocusFlow

Traditional task managers store tasks but leave prioritization and replanning to the user. FocusFlow is designed to consider deadlines, effort, availability, and past progress so people can make steady progress without becoming overwhelmed.

## What Works Today

- **Account access:** Email and password registration and login, email verification, password reset, and profile management.
- **Dashboard preview:** A task list, focus timer, workload insights, and planner interface. Dashboard tasks and metrics are demo data stored in the browser; they are not persisted to the backend.
- **AI chat:** Authenticated chat using an OpenAI-compatible API. The planner context currently comes from the client-side demo dashboard, not saved task or schedule data.
- **Document Q&A:** Upload or enter documents, retrieve relevant passages, and ask questions grounded in them. The backend supports PDF and Word files, plus image OCR when Tesseract is installed.

## Product Vision

FocusFlow aims to become a personal productivity coach that helps users organize tasks, balance workloads, and adjust plans as circumstances change. The long-term goal is to generate useful schedules from deadlines, task effort, availability, and completion history.

### Planned Features

These are product goals, not currently backed by persistent planner services:

- Persisted task, availability, calendar, schedule, and completion-history data.
- A scheduling engine that avoids conflicts and recalculates future work when plans change.
- Planner chat grounded in server-stored user tasks and schedules.
- Calendar views, task attachments, and real notification delivery.
- Analytics and risk insights based on a user's actual history.
- Adaptive workload recommendations based on observed patterns.
- Admin tools, roles, and reporting.

Google sign-in is shown in the login interface but is not connected. Refresh-token sessions are not implemented. Two-factor authentication and collaboration remain future ideas.

## Technology Stack

### Frontend

- React, JavaScript, and Vite
- Tailwind CSS and Framer Motion
- React Router, TanStack Query, Zustand, and React Hook Form

### Backend

- Python, FastAPI, Uvicorn, and Pydantic
- PostgreSQL with pgvector for application data and document embeddings
- Redis for authentication rate limits
- JWT access tokens, Argon2 password hashing, and SMTP email flows
- OpenAI-compatible chat API and FastEmbed sentence embeddings
- PDF and Word extraction, text processing, and image OCR with Tesseract and Pillow

## Local Development

Run the frontend and backend as separate services. For backend installation and startup instructions, see [Backend/README.md](Backend/README.md). Install frontend dependencies from `Frontend` with `npm install`, then start Vite with `npm run dev`.

Configure PostgreSQL, Redis, SMTP, and any AI provider credentials through local environment variables. Image OCR also requires the Tesseract executable on the host. The FastEmbed model downloads on first use and is cached locally.

## Long-Term Vision

FocusFlow AI is intended to grow into an intelligent work-planning assistant that combines reliable scheduling, useful progress insights, and personalized coaching for academic and professional goals.
