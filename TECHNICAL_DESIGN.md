# Plan Kept: As-Built Technical Design

## Stateful partner

One FastAPI service persists a workspace document through plan loading, separate perspectives,
synthesis, clarification, facilitator review, repair, follow-up, and closure. Each transition checks
its predecessor. State consists of bounded fields—preferences, questions, responses, sharing,
revisions, evidence, decisions, actions, and timeline—not an unrestricted conversation transcript.

## Privacy boundary

Each response carries `private`, `facilitator`, or `team` sharing. Role-view projection filters
responses and timeline entries. Synthesis selects only non-private, non-skipped responses. Tests
attempt the private-response leak and verify both protections.

This prototype demonstrates application-layer boundaries; it does not claim production identity,
authorization, consent, retention, or education-record compliance.

## Model and evidence

Gemini 3.5 Flash reads only an authorized synthetic plan. The model must transcribe before extracting
a restricted schema. Application code drops unsupported keys, non-verbatim quotes, and invalid
confidence. Prompt and schema prohibit diagnosis, legal findings, danger/credibility scoring,
discipline/restraint recommendations, and plan alteration.

## Conflict, authority, and closure

The ledger describes `conflicting`, `unknown`, or `reported_unavailable` shared evidence. Every
entry’s system truth decision is null. Conflict produces a targeted operational question. A named
facilitator selects a bounded finding and approves owner/due-date repairs. The workflow is not
closed until the fictional student reports whether the support was available.

## Deployment

The included non-root Python 3.12 image targets Cloud Run. Memory is used locally and the Firestore
adapter is selected with `USE_FIRESTORE=true`. Health, proof, research, and conformance endpoints
make important boundaries inspectable.

## Explicitly absent

Production SSO/RBAC, real school-system integration, legal-compliance automation, real student
records, a live model recording, field evaluation, professional validation, and outcome evidence.
