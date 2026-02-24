from backend.app.core.settings import get_settings
from backend.app.rag.react_agent import ReactAgent
from backend.app.repository import Repository
from backend.app.storage.local import LocalStorage
from backend.app.storage.s3 import S3Storage
from backend.app.vectordb.pgvector import PgVectorDB
from backend.app.vectordb.qdrant import InMemoryVectorDB

settings = get_settings()
repo = Repository()
vectordb = InMemoryVectorDB() if settings.vector_backend == 'qdrant' else PgVectorDB()
storage = LocalStorage(settings.data_dir) if settings.storage_backend == 'local' else S3Storage(settings.data_dir)
agent = ReactAgent(repo, vectordb)
