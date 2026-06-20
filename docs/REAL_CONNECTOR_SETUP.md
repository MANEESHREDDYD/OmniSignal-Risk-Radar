# Real Google Connector Setup (Optional, Read-Only)

This guide explains how to enable the **optional** V1.1 read-only Google
connector locally. **You do not need any of this to run the demo** — synthetic
demo mode is the default and works with no configuration.

> Safety summary: read-only Gmail and Calendar only. No email is sent, no calendar
> event is written, no message is forwarded or exported, no attachment is
> downloaded. Tokens are encrypted at rest and never leave your machine. Real
> connectors stay disabled until you explicitly turn them on.

---

## 1. Create a Google Cloud project

1. Go to <https://console.cloud.google.com/>.
2. Create a new project (e.g. `omnisignal-local`).
3. Select the project.

## 2. Enable the APIs

In **APIs & Services → Library**, enable:

- **Gmail API**
- **Google Calendar API**

## 3. Configure the OAuth consent screen

1. **APIs & Services → OAuth consent screen**.
2. User type: **External** (fine for local testing) and create.
3. Fill in app name, your support email, and developer email.
4. **Scopes**: add the read-only scopes only:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar.events.readonly`
   - (optional) `https://www.googleapis.com/auth/calendar.calendarlist.readonly`
5. **Test users**: add your own Google account. While the app is in "Testing",
   only listed test users can connect.

## 4. Create an OAuth web client

1. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
2. Application type: **Web application**.
3. **Authorized redirect URI** — add exactly:

   ```text
   http://localhost:8000/api/auth/google/callback
   ```

4. Save and copy the **Client ID** and **Client secret**.

## 5. Configure environment variables

Copy `.env.example` to `.env` (never commit `.env`) and set:

```text
DEMO_MODE=true
REAL_CONNECTORS_ENABLED=true

GOOGLE_CLIENT_ID=<your client id>
GOOGLE_CLIENT_SECRET=<your client secret>
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
TOKEN_ENCRYPTION_KEY=<generated below>
```

Generate a token encryption key locally (do **not** commit it):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Notes:

- `REAL_CONNECTORS_ENABLED=true` is required before any real OAuth route or sync
  will run. With it `false`, all real endpoints return a safe blocked response.
- `TOKEN_ENCRYPTION_KEY` is required to store tokens. If it is missing while real
  connectors are enabled, real OAuth/token storage is blocked with a clear error
  and the app stays usable in demo mode.

## 6. Run the app locally

Backend (from `backend/`, with the `.env` loaded into your shell environment):

```bash
uvicorn app.main:app --reload
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Open <http://localhost:3000/settings/integrations>.

## 7. Connect Google

1. On **Settings → Integrations**, confirm the banner shows real connectors
   enabled and the Google card shows **Ready to connect**.
2. Click **Connect Google**, complete the Google consent screen (read-only
   scopes), and you will be redirected back with `?google=connected`.

## 8. Run a read-only sync

- **Sync Gmail read-only** pulls a small batch (≤25) of recent messages.
- **Sync Calendar read-only** pulls events for the next 14 days / past 3 days.
- Synced items appear in the unified inbox and radar with a **Real** badge and a
  row in **Recent real sync runs**.

## 9. Disconnect

Click **Disconnect**. This deletes the connection's encrypted tokens and marks it
disconnected. Synthetic demo data is unaffected.

## 10. Delete local cache

Click **Delete local cache**. This removes only the real synced messages/events
for that connection (and their assessments, notifications, etc.). Synthetic demo
data is never touched. The action is audited with counts.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Buttons disabled, "Real connectors disabled" | `REAL_CONNECTORS_ENABLED` not `true` | Set it in `.env` and restart the backend |
| "blocked_missing_config" | Missing client id/secret or token key | Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `TOKEN_ENCRYPTION_KEY` |
| `redirect_uri_mismatch` from Google | Redirect URI not registered | Add `http://localhost:8000/api/auth/google/callback` exactly in the OAuth client |
| `access_denied` / app not verified | Your account isn't a test user | Add your account under OAuth consent → Test users |
| Callback returns `error_state` | OAuth state expired/invalid | Restart the connect flow from the Integrations page |
| Callback returns `error_exchange` | Token exchange failed | Re-check client id/secret and that the APIs are enabled |
| Sync returns `failed` | Token expired / API error | Reconnect the account, then retry the sync |

## Security reminders

- Never commit `.env`, `*.db`/`*.sqlite`, OAuth tokens, the
  `TOKEN_ENCRYPTION_KEY`, or any real message content. All are covered by
  `.gitignore`.
- This connector is read-only and performs no outbound actions.
- Real Gmail/Calendar access only happens on your machine after you opt in.
