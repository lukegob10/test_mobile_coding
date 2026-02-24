from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.core.auth import require_api_key
from backend.app.deps import repo

router = APIRouter(prefix='/collections', tags=['collections'], dependencies=[Depends(require_api_key)])


class CollectionCreate(BaseModel):
    name: str
    config: dict | None = None


@router.post('')
def create_collection(payload: CollectionCreate):
    c = repo.create_collection(payload.name, payload.config)
    return {'id': c.id}


@router.get('')
def list_collections():
    return [{'id': c.id, 'name': c.name, 'config': c.config} for c in repo.list_collections()]


@router.delete('/{collection_id}')
def delete_collection(collection_id: str):
    if collection_id not in {c.id for c in repo.list_collections()}:
        raise HTTPException(status_code=404, detail='Collection not found')
    repo.delete_collection(collection_id)
    return {'ok': True}
