# Backend operations

## Verification email outbox

Registration and OTP resend requests save the pending OTP and an encrypted email
job in the same database transaction. A separate worker delivers queued messages.
Run the database migration before deploying the application:

```powershell
alembic upgrade head
```

Set `OTP_OUTBOX_ENCRYPTION_KEY` to a Fernet key in the backend environment. Generate
one with:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep this key stable and backed up; jobs encrypted with an old key cannot be
delivered after it changes. If the setting is omitted, the application derives
the encryption key from `SECRET_KEY` for backwards-compatible local development.
Production deployments should configure a dedicated key.

Run the API and the delivery worker as separate processes from the `backend`
directory:

```powershell
uvicorn app.main:app
python -m app.workers.email_outbox
```

The worker retries failed sends with exponential delay, up to five attempts. Jobs
that reach the limit are marked `failed` for operator review. Delivery is
at-least-once: if SMTP accepts a message but the worker loses its database
connection before marking the job sent, it may send that message again after its
lease expires. Expired or superseded OTPs are marked obsolete instead of sent.
