# Plan Kept Developer API

The hosted UI remains keyless for judges. Integrations use the stable, authenticated `/v1` API.

## Get a free key

```bash
curl -X POST "$BASE_URL/api/developer/keys" \
  -H "Content-Type: application/json" \
  -d '{"label":"evaluation","acceptable_use_acknowledgement":true}'
```

The key is displayed once and valid for 180 days. Only an HMAC digest is persisted. A keyed network fingerprint—not a raw client address—is retained for abuse control. Both key and network receive 50 requests per UTC day, enforced atomically in Firestore; up to five keys may be issued per network per day and share that ceiling. Every authenticated response reports quota and reset headers.

## Use the service

```bash
curl -X POST "$BASE_URL/v1/tabletop-runs" -H "X-API-Key: $API_KEY"
```

For an input-driven workflow, `POST /v1/workspaces` with a fictional plan transcription and exact-quoted promises. Participants submit separately controlled responses; the partner auto-synthesizes only consented evidence, pauses for qualified clarification and repair decisions, schedules the durable follow-up, and closes only on the student's experience. See `/docs` and `GET /v1/workspaces/{workspace_id}/autonomy-proof`.

The public deployment accepts fictional synthetic education data only. Do not send education records or personally identifying data. Plan Kept does not decide truth, legality, diagnosis, discipline, restraint, or plan changes.

## Security and durability

- The HMAC pepper is injected from Google Secret Manager.
- Firestore transactions prevent concurrent quota bypass.
- No resource-list endpoint exposes another caller's records.
- Participant sharing controls, bounded role views, safe trace receipts, and durable Cloud Scheduler wakeups preserve the product's authority and privacy model.

