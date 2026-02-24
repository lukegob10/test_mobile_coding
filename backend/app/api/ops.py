from fastapi import APIRouter

from backend.app.deps import vectordb

router = APIRouter(tags=['ops'])


@router.get('/healthz')
def healthz():
    return {'ok': True}


@router.get('/readyz')
def readyz():
    return {'ok': vectordb.ping()}


@router.get('/version')
def version():
    return {'git_sha': 'dev', 'build_time': 'dev'}


@router.get('/metrics')
def metrics():
    return {'metrics': 'not_enabled'}
