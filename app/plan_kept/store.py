from __future__ import annotations
from copy import deepcopy
from typing import Any,Protocol

class WorkspaceStore(Protocol):
    def put(self,workspace:dict[str,Any])->None:...
    def get(self,workspace_id:str)->dict[str,Any]|None:...
    def list_workspaces(self)->list[dict[str,Any]]:...
    def clear(self)->None:...

class MemoryWorkspaceStore:
    def __init__(self):self._items={}
    def put(self,workspace):self._items[workspace["workspace_id"]]=deepcopy(workspace)
    def get(self,workspace_id):
        item=self._items.get(workspace_id);return deepcopy(item) if item is not None else None
    def list_workspaces(self):return sorted((deepcopy(item) for item in self._items.values()),key=lambda item:item.get("created_at",""),reverse=True)
    def clear(self):self._items.clear()

class FirestoreWorkspaceStore:
    def __init__(self,client,collection="plan_kept_workspaces"):self._collection=client.collection(collection)
    def put(self,workspace):self._collection.document(workspace["workspace_id"]).set(workspace)
    def get(self,workspace_id):
        snap=self._collection.document(workspace_id).get();return snap.to_dict() if snap.exists else None
    def list_workspaces(self):return sorted((snap.to_dict() for snap in self._collection.stream()),key=lambda item:item.get("created_at",""),reverse=True)
    def clear(self):
        for document in self._collection.stream():document.reference.delete()

