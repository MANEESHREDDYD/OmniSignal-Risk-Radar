# OmniSignal Risk Radar Demo Script

Estimated duration: 7-10 minutes.

## 1. Start the Product

Start the backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000`.

## 2. Connect Six Demo Accounts

1. Open `/connections`.
2. Point out the six synthetic accounts:
   - Personal Gmail
   - Work Gmail
   - School Outlook
   - Phone SMS
   - iMessage
   - Google Calendar
3. Click **Sync demo data** on one account.
4. Explain that all connectors read local fixtures and never request real credentials.

Key message: the connector contract is integration-ready while the V1.0 demo remains private and zero-budget.

## 3. View the Unified Inbox

1. Open `/inbox`.
2. Show Gmail, Outlook, SMS, iMessage, and calendar messages in one table.
3. Point out the account, source platform, priority, component scores, and recommended route.
4. Explain that every platform is normalized before analysis.

## 4. Filter P0 Alerts

1. Select **P0 immediate**.
2. Show the security, bank/card, official deadline, customer-launch, and interview-confirmation alerts.
3. Explain that deterministic safety overrides protect high-consequence cases even when a weighted score is borderline.

## 5. Open a Security Alert

1. Open message `msg_037`, or select any row titled **Security alert: new sign-in from unknown device**.
2. Show:
   - Original message
   - Urgency score
   - Consequence-risk score
   - Action-needed score
   - Weighted priority
   - Explainable reason cards
3. Point out that the security signal forces a minimum P0 classification.

## 6. Open a Recruiter or Interview Deadline

1. Return to the inbox.
2. Open an interview message such as `msg_031`.
3. Show the deadline-today and confirmation-required reasons.
4. Explain that the system distinguishes an important recruiter message from a generic scheduling request.

## 7. Add a Simulated Scheduling Review Marker

1. Open a message such as `msg_001` with time-zone and location ambiguity.
2. Click **Scheduling review**.
3. Explain that OmniSignal does not auto-book risky or underspecified meetings.
4. The action records a local simulated marker and audit event only. No real
   queue, reply, or calendar action runs.

## 8. Act on a Notification

1. Open `/notifications`.
2. Snooze or resolve one notification.
3. Explain that the state change is local and does not send an outbound message.

## 9. Show the Audit Trail

1. Open `/audit-log`.
2. Find the notification action or scheduling handoff.
3. Point out the actor, action, target, timestamp, and result.

Key message: important assistant behavior is traceable and correctable.

## 10. Show Analytics and Evaluation

1. Open `/analytics`.
2. Show:
   - 80 messages analyzed
   - Priority distribution
   - Platform distribution
   - Top risk reasons
   - Priority accuracy
   - P0 precision and recall
   - Scheduling routing accuracy
   - Newsletter suppression accuracy
3. Clarify that the metrics are synthetic fixture conformance over repeated
   templates, not real-world inbox accuracy. Show labeled and ignored-unlabeled
   counts.

## Closing Positioning

OmniSignal is a deterministic local risk-radar prototype. It explains synthetic
priority decisions, manages in-app notifications and tasks, records local
actions, and marks scheduling ambiguity for simulated review. It does not send
email, write calendars, or book meetings.
