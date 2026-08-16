from __future__ import annotations
import os
from spine.clock import MemoryClockStateStore, SimulatedClock
from spine.firestore_wakes import FirestoreClockStateStore, FirestoreWakeStore
from spine.wake import MemoryWakeStore, WakeScheduler


def build_runtime(project_id, use_firestore):
    if use_firestore:
        from google.cloud import firestore
        client = firestore.Client(project=project_id)
        clock = SimulatedClock(FirestoreClockStateStore(client, "plan-kept"))
        wake_store = FirestoreWakeStore(client, "plan_kept_wakes")
    else:
        clock = SimulatedClock(MemoryClockStateStore()); wake_store = MemoryWakeStore()
    return clock, WakeScheduler(wake_store, clock, lease_seconds=int(os.getenv("WAKE_LEASE_SECONDS", "90")), max_attempts=int(os.getenv("WAKE_MAX_ATTEMPTS", "5")))

