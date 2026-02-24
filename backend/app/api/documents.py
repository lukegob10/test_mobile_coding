from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.app.core.auth import require_api_key
from backend.app.deps import repo, storage, vectordb
from backend.app.ingest.chunk import chunk_text
from backend.app.ingest.embed import embed_text
from backend.app.ingest.extract import extract_text
from backend.app.repository import sha256_bytes

router = APIRouter(prefix='/collections/{collection_id}/documents', tags=['documents'], dependencies=[Depends(require_api_key)])


@router.post('')
async def upload_document(collection_id: str, file: UploadFile = File(...), metadata_json: str | None = Form(default=None), force: bool = Form(default=False)):
    if collection_id not in {c.id for c in repo.list_collections()}:
        raise HTTPException(status_code=404, detail='Collection not found')
    data = await file.read()
    digest = sha256_bytes(data)
    existing = repo.find_doc_by_sha(collection_id, digest)
    if existing and not force:
        return {'doc_id': existing.doc_id, 'chunks_indexed': 0, 'sha256': existing.sha256}

    text = extract_text(file.filename or 'upload.txt', data)
    doc = repo.add_document(collection_id, file.filename or 'upload.txt', digest, storage.write_bytes(f'uploads/{uuid4()}-{file.filename}', data))
    chunks = chunk_text(text)
    for idx, ch in enumerate(chunks):
        c = repo.add_chunk(doc.doc_id, collection_id, doc.filename, idx, ch)
        vectordb.upsert(c.chunk_id, embed_text(ch), {
            'doc_id': c.doc_id,
            'collection_id': c.collection_id,
            'filename': c.filename,
            'chunk_index': c.chunk_index,
            'preview': ch[:120],
        })
    return {'doc_id': doc.doc_id, 'chunks_indexed': len(chunks), 'sha256': digest}


@router.get('')
def list_documents(collection_id: str):
    return [
        {'doc_id': d.doc_id, 'filename': d.filename, 'created_at': d.created_at.isoformat(), 'sha256': d.sha256}
        for d in repo.list_documents(collection_id)
    ]


@router.delete('/{doc_id}')
def delete_document(collection_id: str, doc_id: str):
    repo.delete_document(doc_id)
    return {'ok': True}
