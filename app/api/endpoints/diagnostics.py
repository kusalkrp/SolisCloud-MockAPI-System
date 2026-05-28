from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    return {
        "status": "online",
        "system": "Production-Grade SolisCloud Platform API Mock System",
        "version": "2.0.0",
        "documentation": "/docs"
    }
