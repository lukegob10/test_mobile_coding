from fastapi import Depends, Header, HTTPException, status

from backend.app.core.settings import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None, alias='X-API-Key')) -> None:
    settings = get_settings()
    keys = settings.api_keys
    if not keys:
        return
    if x_api_key not in keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid API key')


AuthDependency = Depends(require_api_key)
