import psutil
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
def system_status() -> dict[str, float]:
    cpu_percent = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()

    ram_used_gb = round((mem.total - mem.available) / (1024**3), 2)
    ram_total_gb = round(mem.total / (1024**3), 2)

    return {
        "cpu_percent": cpu_percent,
        "ram_used_gb": ram_used_gb,
        "ram_total_gb": ram_total_gb,
        "ram_percent": mem.percent,
    }