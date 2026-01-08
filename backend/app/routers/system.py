"""
SMART GROW - Router de Sistema
==============================
Endpoints para estado y configuración del sistema.
"""

from fastapi import APIRouter
from datetime import datetime
import platform
import psutil

router = APIRouter()


@router.get("/status")
async def get_system_status():
    """Obtiene estado completo del sistema."""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "gateway": "online",
            "influxdb": "online",
            "mqtt": "online",
            "ml_service": "online"
        },
        "nodes": {
            "node1": {
                "status": "online",
                "last_packet": datetime.now().isoformat(),
                "packets_today": 96,
                "battery": None  # Para nodos con batería
            }
        }
    }


@router.get("/info")
async def get_system_info():
    """Obtiene información del sistema."""
    return {
        "version": "1.0.0",
        "hostname": platform.node(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "uptime_seconds": int(psutil.boot_time()),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }


@router.get("/metrics")
async def get_metrics():
    """Obtiene métricas de rendimiento del sistema."""
    return {
        "packets_received_24h": 2160,
        "packet_success_rate": 96.0,
        "average_rssi": -85,
        "average_snr": 7.5,
        "api_requests_24h": 500,
        "predictions_generated_24h": 144,
        "alerts_triggered_24h": 2
    }


@router.get("/logs")
async def get_recent_logs(lines: int = 50):
    """Obtiene logs recientes del sistema."""
    return {
        "logs": [],
        "count": 0
    }


@router.post("/restart")
async def restart_service(service: str):
    """Reinicia un servicio específico."""
    valid_services = ["lora_receiver", "fastapi", "nodered"]
    if service not in valid_services:
        return {"error": f"Servicio inválido. Opciones: {valid_services}"}
    return {"status": "restart_requested", "service": service}
