# Plan Kept cloud infrastructure

The checked-in composite indexes support transactional follow-up wake scans. `provision_scheduler.ps1` creates or updates `plan-kept-wake-scan`, which calls `POST /internal/wakes/scan` every minute with a Google-signed OIDC token. The application verifies the dedicated scheduler identity before claiming Firestore work; actions are idempotent and retries are bounded.

Demo role tokens are deliberately labelled and must be replaced with organization identity claims before any real deployment. This repository contains no real education record.
