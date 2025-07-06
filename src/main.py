import uvicorn
from fastapi import FastAPI

from api.v1 import router as api_router
from core.config import get_settings

settings = get_settings()

app = FastAPI()
app.include_router(
    api_router,
    prefix=settings.api.prefix,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
            host=settings.run.host,
            port=settings.run.port,
            reload=True,
        )
