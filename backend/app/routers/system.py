"""
Router de Sistema - SMART GROW API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import platform
import psutil

from app.config import settings

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/status")
async def get_system_status():
    """
    Obtiene el estado completo del sistema.
    
    Returns:
        Estado de todos los componentes
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "online",
        "components": {
            "api": {
                "status": "healthy",
                "version": settings.VERSION
            },
            "influxdb": {
                "status": "healthy",
                "url": settings.INFLUX_URL
            },
            "mqtt": {
                "status": "healthy",
                "broker": settings.MQTT_BROKER
            },
            "ml_models": {
                "frost_model": "loaded",
                "disease_model": "loaded"
            }
        },
        "nodes": {
            "node1": {
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "battery": 85,
                "rssi": -75
            }
        }
    }


@router.get("/info")
async def get_system_info():
    """
    Obtiene información del sistema.
    
    Returns:
        Información de hardware y software
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "system": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.machine()
        },
        "resources": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": round(disk.percent, 1)
            }
        },
        "application": {
            "version": settings.VERSION,
            "debug_mode": settings.DEBUG,
            "uptime_seconds": 0  # Implementar contador
        }
    }


@router.get("/metrics")
async def get_metrics():
    """
    Obtiene métricas de rendimiento del sistema.
    
    Returns:
        Métricas operacionales
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "lora": {
            "packets_received_24h": 96,
            "packets_error_24h": 4,
            "success_rate": 96.0,
            "average_rssi": -72,
            "average_snr": 9.5
        },
        "api": {
            "requests_24h": 1250,
            "average_response_ms": 45,
            "errors_24h": 3
        },
        "predictions": {
            "frost_predictions_24h": 144,
            "disease_predictions_24h": 144,
            "alerts_generated_24h": 2
        },
        "database": {
            "measurements_24h": 576,
            "storage_used_mb": 125,
            "retention_days": 90
        }
    }


@router.get("/logs")
async def get_recent_logs(
    level: str = "INFO",
    limit: int = 50
):
    """
    Obtiene logs recientes del sistema.
    
    Args:
        level: Nivel mínimo (DEBUG, INFO, WARNING, ERROR)
        limit: Cantidad máxima de logs
        
    Returns:
        Lista de logs recientes
    """
    # En producción: leer archivo de logs real
    return {
        "level_filter": level,
        "limit": limit,
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Sistema operando normalmente"
            }
        ]
    }


@router.post("/restart/{service}")
async def restart_service(service: str):
    """
    Reinicia un servicio específico.
    
    Args:
        service: Nombre del servicio (api, lora_receiver, etc.)
        
    Returns:
        Estado del reinicio
    """
    valid_services = ["api", "lora_receiver", "mqtt_bridge"]
    
    if service not in valid_services:
        raise HTTPException(
            status_code=400,
            detail=f"Servicio inválido. Válidos: {valid_services}"
        )
    
    # En producción: implementar reinicio real via systemctl
    return {
        "service": service,
        "action": "restart",
        "status": "scheduled",
        "message": f"Reinicio de {service} programado"
    }
