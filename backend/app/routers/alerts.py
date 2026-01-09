"""
Router de Alertas - SMART GROW API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════
# MODELOS
# ═══════════════════════════════════════════════════════════════════════════

class AlertType(str, Enum):
    FROST = "frost"
    DISEASE = "disease"
    SOIL_DRY = "soil_dry"
    HIGH_TEMP = "high_temp"
    SENSOR_OFFLINE = "sensor_offline"
    LOW_BATTERY = "low_battery"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Alerta del sistema"""
    id: str
    type: AlertType
    severity: Severity
    message: str
    value: Optional[float]
    threshold: Optional[float]
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class AlertConfig(BaseModel):
    """Configuración de alertas"""
    alert_type: AlertType
    enabled: bool
    threshold_warning: Optional[float]
    threshold_critical: Optional[float]
    notify_email: bool
    notify_push: bool


# ═══════════════════════════════════════════════════════════════════════════
# DATOS DE EJEMPLO (En producción usar base de datos)
# ═══════════════════════════════════════════════════════════════════════════

# Simulación de alertas activas
_active_alerts = []


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/active", response_model=List[Alert])
async def get_active_alerts(
    severity: Optional[Severity] = None,
    alert_type: Optional[AlertType] = None
):
    """
    Obtiene las alertas activas no reconocidas.
    
    Args:
        severity: Filtrar por severidad
        alert_type: Filtrar por tipo de alerta
        
    Returns:
        Lista de alertas activas
    """
    alerts = [a for a in _active_alerts if not a.get("acknowledged", False)]
    
    if severity:
        alerts = [a for a in alerts if a.get("severity") == severity]
    
    if alert_type:
        alerts = [a for a in alerts if a.get("type") == alert_type]
    
    return alerts


@router.get("/history")
async def get_alert_history(
    hours: int = Query(default=24, ge=1, le=168),
    alert_type: Optional[AlertType] = None,
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Obtiene el histórico de alertas.
    
    Args:
        hours: Período en horas
        alert_type: Filtrar por tipo
        limit: Máximo de resultados
        
    Returns:
        Histórico de alertas
    """
    # En producción: consultar InfluxDB o base de datos
    return {
        "hours": hours,
        "count": 0,
        "alerts": []
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Reconoce una alerta (marca como leída).
    
    Args:
        alert_id: ID de la alerta
        
    Returns:
        Confirmación
    """
    for alert in _active_alerts:
        if alert.get("id") == alert_id:
            alert["acknowledged"] = True
            alert["acknowledged_at"] = datetime.now().isoformat()
            return {"status": "acknowledged", "alert_id": alert_id}
    
    raise HTTPException(status_code=404, detail="Alerta no encontrada")


@router.get("/config", response_model=List[AlertConfig])
async def get_alert_config():
    """
    Obtiene la configuración actual de alertas.
    
    Returns:
        Lista de configuraciones por tipo de alerta
    """
    return [
        AlertConfig(
            alert_type=AlertType.FROST,
            enabled=True,
            threshold_warning=5.0,
            threshold_critical=0.0,
            notify_email=True,
            notify_push=True
        ),
        AlertConfig(
            alert_type=AlertType.DISEASE,
            enabled=True,
            threshold_warning=70.0,
            threshold_critical=85.0,
            notify_email=True,
            notify_push=True
        ),
        AlertConfig(
            alert_type=AlertType.SOIL_DRY,
            enabled=True,
            threshold_warning=30.0,
            threshold_critical=20.0,
            notify_email=False,
            notify_push=True
        ),
        AlertConfig(
            alert_type=AlertType.HIGH_TEMP,
            enabled=True,
            threshold_warning=35.0,
            threshold_critical=40.0,
            notify_email=False,
            notify_push=True
        ),
        AlertConfig(
            alert_type=AlertType.SENSOR_OFFLINE,
            enabled=True,
            threshold_warning=None,
            threshold_critical=None,
            notify_email=True,
            notify_push=True
        )
    ]


@router.put("/config/{alert_type}")
async def update_alert_config(
    alert_type: AlertType,
    config: AlertConfig
):
    """
    Actualiza la configuración de un tipo de alerta.
    
    Args:
        alert_type: Tipo de alerta a configurar
        config: Nueva configuración
        
    Returns:
        Configuración actualizada
    """
    # En producción: guardar en base de datos
    return {
        "status": "updated",
        "config": config
    }
