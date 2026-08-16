from __future__ import annotations
from copy import deepcopy
from typing import Any,Protocol

class WorkspaceStore(Protocol):
    def put(self,workspace:dict[str,Any])->None:...
    def get(self,workspace_id:str)->dict[str,Any]|None:...
    def clear(self)->None:...

class MemoryWorkspaceStore:
    def __init__(self):self._items={}
    def put(self,workspace):self._items[workspace["workspace_id"]]=deepcopy(workspace)
    def get(self,workspace_id):
        item=self._items.get(workspace_id);return deepcopy(item) if item is not None else None
    def clear(self):self._items.clear()

class FirestoreWorkspaceStore:
    def __init__(self,client,collection="plan_kept_workspaces"):self._collection=client.collection(collection)
    def put(self,workspace):self._collection.document(workspace["workspace_id"]).set(workspace)
    def get(self,workspace_id):
        snap=self._collection.document(workspace_id).get();return snap.to_dict() if snap.exists else None
    def clear(self):
        for document in self._collection.stream():document.reference.delete()

