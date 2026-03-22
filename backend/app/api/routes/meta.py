from fastapi import APIRouter


router = APIRouter()


@router.get("/health", tags=["meta"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
