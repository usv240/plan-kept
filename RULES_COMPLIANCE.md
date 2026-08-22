# Rules compliance — Plan Kept

| Rules.md requirement | Evidence | Status |
|---|---|---|
| One category | The Collaborative Partner | Pass |
| Gemini 3.5+ | Deployed `/api/demo/full` live fail-closed Gemini 3.5 Flash receipt with exact-quote grading | Pass |
| Google agent framework | Google Gen AI SDK (`google-genai`) | Pass |
| Google Cloud service | Cloud Run, Firestore, Cloud Trace | Pass |
| Leads and asks clarifying questions | Role-specific questions plus conflict-targeted clarification | Pass |
| Captures feedback and adapts | Preferences, revision history, sharing changes, withdrawal and synthesis invalidation | Pass |
| Persistent bounded memory | Preferences, promises, decisions, actions and follow-up; no transcript replay | Pass |
| Working public access | Public product, fictional workspace, scoped role endpoint and proofs | Pass |
| Public repository | https://github.com/usv240/plan-kept | Pass |
| Reproducible setup and diagram | README, Dockerfile, deploy script, indexes, `docs/architecture.svg` | Pass |
| Privacy and authority | Token-gated demo views, injection quarantine, no truth/risk/legal/discipline score | Pass |
| Under-four-minute public video | Must be published by entrant with live collaboration and Cloud evidence | Entrant action |
| Additional Google AI model | Gemini Embedding 001 performs operational semantic routing; claim only with a live `semantic_routing` receipt | Implemented; live evidence recorded |
| Optional public content/social post | Drafts are in `docs/`; eligible platform publication remains entrant action | Entrant action |

Every person, plan and response is fictional. The service makes no educational, clinical, legal or prevention outcome claim.

## Additional production evidence

| Requirement | Implementation | Status |
|---|---|---|
| Self-service integration | Keyless judge UI plus protected `/v1`, no account required, 50 requests per key and network per UTC day | Pass |
| Secure public endpoint | HMAC-only keys, fingerprint-only IP handling, Secret Manager pepper, atomic Firestore quota transactions | Pass |
| Visible autonomy | Cumulative trace-derived receipt, direct proof endpoint, zero continue-click count, honest synthetic-event disclosure | Pass |