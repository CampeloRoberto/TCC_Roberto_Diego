from fastapi import FastAPI
from sqlalchemy import text

from api.routes.equivalencias import router as equivalencias_router
from api.routes.medicamentos import router as medicamentos_router
from pipeline.loaders.models import SessionLocal

app = FastAPI(title="SUS Med API")
app.include_router(medicamentos_router)
app.include_router(equivalencias_router)

# sync_router ainda não é registrado — ver TODO em api/routes/sync.py.


@app.get("/health")
def health() -> dict[str, str]:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unreachable"
    finally:
        session.close()
    return {"status": "ok", "database": db_status}
