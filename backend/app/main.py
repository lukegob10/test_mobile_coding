from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api import collections, documents, ops, react
from backend.app.core.logging import configure_logging, request_logging_middleware
from backend.app.core.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(docs_url=None if settings.env == 'prod' else '/docs', redoc_url=None)
app.middleware('http')(request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api = FastAPI()
api.include_router(ops.router)
api.include_router(collections.router)
api.include_router(documents.router)
api.include_router(react.router)

app.mount('/api/v1', api)
app.mount('/', StaticFiles(directory='static', html=True), name='static')
