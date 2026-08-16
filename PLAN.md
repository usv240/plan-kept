# Plan Kept: Prize-Quality Build Plan

**Track:** The Collaborative Partner  
**Product promise:** After a school crisis, determine whether the supports already promised to a student were actually available—and make the repair work visible.  
**Primary user:** A qualified school support-team facilitator working with a student and family.  
**Status:** Approved only in this redesigned accommodation-gap form; the generic restraint-reporting concept is rejected.

## 1. The precise friction

Incident systems record what happened. Behavior-plan tools help draft plans. The unresolved question
is often whether an existing support was understood, available, offered, usable, and followed.
The answer is distributed across a student's account, family knowledge, staff accounts, schedules,
resource availability, and previous commitments.

Plan Kept is a structured, multi-perspective collaboration workspace. It helps an authorized team
find implementation gaps and track repairs. It does not judge blame, legality, diagnosis, danger,
discipline, or whether restraint was justified.

## 2. Defensible differentiation

RecordHQ, Cairn, MangoApps, and other systems already offer incident recording, pupil/staff
debriefs, parent notifications, action tracking, and behavior insights. Plan Kept cannot win as
another reporting system.

Its narrow contribution is a **promise-to-reality ledger**:

```text
approved support or prior commitment
  -> separately collected perspectives
  -> evidence and availability checks
  -> explicit agreement / conflict / unknown
  -> qualified-team decision
  -> owned repair action
  -> follow-up with the student and family
```

The demo begins with an existing synthetic support plan. It never asks the model to invent one.

## 3. Research and prior-art sources

| Design claim | Source and use |
|---|---|
| Restraint or seclusion should be avoided except where behavior poses imminent danger of serious physical harm | [U.S. Department of Education resource document](https://www.ed.gov/teaching-and-administration/safe-learning-environments/school-safety-and-security/school-climate-and-student-discipline/restraint-and-seclusion-resource-document) — safety framing only |
| Schools should debrief and make prevention-focused adjustments after restrictive interventions | [Center on PBIS, Restraint/Seclusion](https://www.pbis.org/topics/restraintseclusion) — prevention-loop rationale |
| Collaborative problem solving has evidence of reducing restrictive practices in a child psychiatric setting | [Five-year prospective study](https://pubmed.ncbi.nlm.nih.gov/19033167/) — mechanism inspiration with explicit non-school limitation |
| Trauma-informed reduction strategies have a published evidence base across child and adolescent settings | [Systematic review](https://pubmed.ncbi.nlm.nih.gov/37593061/) — design principles and research limitations |
| Existing products already implement pupil/staff debriefs, actions, conversational reporting, and analytics | [RecordHQ](https://recordhq.co.uk/), [Cairn](https://cairn.school/), [MangoApps template](https://www.mangoapps.com/templates/forms/seclusion-and-restraint-incident-reporting-and-debrief-form) — prior-art boundary |

The public product must state that cited intervention studies do not validate this AI system and
that some evidence comes from clinical rather than ordinary K-12 settings.

## 4. End-to-end collaborative flow

1. A qualified facilitator creates a synthetic review workspace and loads an approved support-plan fixture.
2. Gemini 3.5 Flash transcribes the plan and extracts only quote-supported commitments.
3. Student, family, teacher, aide, and coordinator receive separate, role-appropriate sessions.
4. The partner asks one plain-language question at a time and explains why it is asking.
5. Participants may answer, skip, correct, mark a term unclear, or keep a statement private.
6. The synthesis agent classifies each promise as confirmed available, reported unavailable,
   conflicting, unknown, or not relevant—never as true/false based solely on majority.
7. Conflicts produce targeted clarifying questions with both accounts shown only to authorized roles.
8. The facilitator reviews evidence and records the team decision.
9. Repair actions receive an owner, deadline, approval, and student/family-visible status.
10. Persistent memory recalls the student's communication preferences and prior unresolved promises.
11. At follow-up, the student and family can confirm whether the repair was experienced in practice.

## 5. Child safety, privacy, and authority contract

- No behavior prediction, risk score, diagnosis, discipline recommendation, restraint recommendation,
  legal conclusion, or automatic support-plan change.
- Separate perspective records remain private unless the participant and authorized workflow permit sharing.
- The system identifies disagreement; it does not identify a liar.
- The student's ability to skip, correct, pause, use plain language, and choose text or recorded
  synthetic demonstration input is visible at all times.
- Qualified humans approve every finding and action.
- The repository and public demo use fictional students, schools, and records.
- Full chat replay is avoided; persistent memory stores bounded preferences and approved facts.

## 6. Architecture

- FastAPI service on Cloud Run.
- Gemini 3.5 Flash through Vertex AI / Google Gen AI SDK for multimodal support-plan reading and
  bounded conflict-question generation.
- Firestore-compatible structured workspaces, perspectives, preferences, evidence, decisions, and actions.
- Role-aware access layer for student, family, staff, facilitator, and auditor views.
- Source verifier and contradiction engine.
- Cloud Scheduler-compatible follow-up wakes.
- OpenTelemetry hooks for Cloud Trace and structured audit events.
- Replay fixtures for deterministic evaluation and public demonstrations.

## 7. Judge and first-user experience

This is not styled as disciplinary software. The visual language is calm, private, and agency-first.
The participant view shows one question, why it matters, privacy state, and response controls. The
facilitator view shows a promise-to-reality matrix. Color is never used without labels and icons.

The signature moment is a real conflict handled respectfully:

> The plan promises access to a quiet room. The student reports it was locked. Staff report it was
> offered. The system does not decide who is wrong; it asks whether the room-access log and substitute
> instructions can resolve the gap, then waits for a qualified decision.

## 8. Evaluation

- Support-plan extraction accuracy against adjacent truth.
- Every extracted commitment has an exact source quote.
- No private statement appears in an unauthorized role view.
- Conflict classification and targeted-question accuracy across synthetic cases.
- Zero prohibited predictions, diagnoses, legal conclusions, or automatic plan changes.
- Correction and preference adaptation persist across sessions.
- Action reminders are idempotent and bounded.
- Participant can complete the flow by keyboard and at 320px width.
- Light/dark contrast and reduced-motion checks pass.
- Executable local and deployed demo flows pass.

No claim that Plan Kept prevents future incidents will be made without a school-based study.

## 9. Four-minute demo spine

1. Open a fictional student's existing support plan and show quote-grounded commitments.
2. Enter the student view; answer one question, skip another, correct a term, and keep one response private.
3. Add a staff account that conflicts with room availability.
4. Show the partner ask one precise follow-up rather than generating a generic summary.
5. Enter facilitator view; inspect the promise-to-reality ledger and source evidence.
6. Approve a bounded repair action and assign an owner.
7. Advance time; show the follow-up wake and student-visible completion check.
8. Open privacy proof, prohibited-action test, adaptation history, and Cloud deployment evidence.

## 10. Release gates

- Product remains an accommodation-implementation workspace, not an incident-reporting clone.
- Every perspective has explicit sharing state and role enforcement.
- Every AI finding is reviewable, correctable, and source-bearing.
- Prohibited-action tests are public and green.
- Competitor differentiation and clinical-to-school research limitations are explicit.
- Public Cloud Run service, architecture diagram, README, validation report, differentiation
  document, and submission kit are complete.

