from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="AREP Triage MVP",
    version="0.1.0",
    summary="Plataforma academica de triaje medico con RAG y trazabilidad",
)

app.include_router(api_router)


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    return {
        "project": "AREP Triage MVP",
        "status": "ready",
        "docs": "/docs",
    }
