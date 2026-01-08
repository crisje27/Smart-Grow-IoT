"""
SMART GROW - Router de Alertas
==============================
Endpoints para configuración y consulta de alertas.
"""

from fastapi import APIRouter
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

router = APIRouter()


class AlertType(str, Enum):
    FROST = "frost"
    DISEASE = "disease"
    SOIL_DRY = "soil_dry"
    HIGH_TEMP = "high_temp"
    SENSOR_OFFLINE = "sensor_offline"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    id: str
    type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    acknowledged: bool = False


class AlertConfig(BaseModel):
    type: AlertType
    enabled: bool
    threshold: Optional[float] = None
    channels: List[str] = ["app"]


@router.get("/active", response_model=List[Alert])
async def get_active_alerts():
    """Obtiene alertas activas no reconocidas."""
    return []


@router.get("/history")
async def get_alert_history(days: int = 7):
    """Obtiene histórico de alertas."""
    return []


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Marca una alerta como reconocida."""
    return {"status": "acknowledged", "alert_id": alert_id}


@router.get("/config", response_model=List[AlertConfig])
async def get_alert_config():
    """Obtiene configuración de alertas."""
    return [
        AlertConfig(type=AlertType.FROST, enabled=True, threshold=70.0, channels=["app", "sms"]),
        AlertConfig(type=AlertType.DISEASE, enabled=True, threshold=80.0, channels=["app"]),
        AlertConfig(type=AlertType.SOIL_DRY, enabled=True, threshold=30.0, channels=["app"]),
        AlertConfig(type=AlertType.HIGH_TEMP, enabled=True, threshold=35.0, channels=["app"]),
        AlertConfig(type=AlertType.SENSOR_OFFLINE, enabled=True, channels=["app"]),
    ]


@router.put("/config/{alert_type}")
async def update_alert_config(alert_type: AlertType, config: AlertConfig):
    """Actualiza configuración de un tipo de alerta."""
    return {"status": "updated", "type": alert_type}
