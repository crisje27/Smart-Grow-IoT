"""
SMART GROW - Router de Sensores
================================
Endpoints para consulta de datos de sensores.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()


# ==========================================================================
# MODELOS
# ==========================================================================

class SensorReading(BaseModel):
    """Lectura de sensores."""
    timestamp: datetime
    temperature: float
    humidity: float
    soil_humidity: float
    soil_temp: float
    light: float
    pressure: float
    rssi: Optional[int] = None
    snr: Optional[float] = None


class SensorStats(BaseModel):
    """Estadísticas de sensores."""
    field: str
    min: float
    max: float
    mean: float
    count: int


# ==========================================================================
# ENDPOINTS
# ==========================================================================

@router.get("/latest", response_model=SensorReading)
async def get_latest_data():
    """
    Obtiene la última lectura de todos los sensores.
    
    Returns:
        Última lectura de sensores con timestamp
    """
    # TODO: Implementar consulta real a InfluxDB
    # Por ahora retorna datos de ejemplo
    return SensorReading(
        timestamp=datetime.now(),
        temperature=22.5,
        humidity=65.0,
        soil_humidity=45.0,
        soil_temp=18.5,
        light=12500.0,
        pressure=1013.25,
        rssi=-85,
        snr=7.5
    )


@router.get("/history", response_model=List[SensorReading])
async def get_history(
    hours: int = Query(default=24, ge=1, le=168, description="Horas de histórico (1-168)"),
    interval: str = Query(default="10m", description="Intervalo de agregación (1m, 5m, 10m, 1h)")
):
    """
    Obtiene histórico de datos con agregación.
    
    Args:
        hours: Cantidad de horas hacia atrás
        interval: Intervalo de agregación temporal
        
    Returns:
        Lista de lecturas agregadas
    """
    # TODO: Implementar consulta real a InfluxDB
    return []


@router.get("/stats")
async def get_stats(
    hours: int = Query(default=24, ge=1, le=168),
    field: Optional[str] = Query(default=None, description="Campo específico")
):
    """
    Obtiene estadísticas de los datos de sensores.
    
    Args:
        hours: Período de cálculo
        field: Campo específico (opcional)
        
    Returns:
        Estadísticas (min, max, mean) por campo
    """
    fields = ['temperature', 'humidity', 'soil_humidity', 'soil_temp', 'light', 'pressure']
    
    if field and field not in fields:
        raise HTTPException(status_code=400, detail=f"Campo inválido. Opciones: {fields}")
    
    # TODO: Implementar cálculo real desde InfluxDB
    stats = []
    for f in (fields if not field else [field]):
        stats.append(SensorStats(
            field=f,
            min=0.0,
            max=100.0,
            mean=50.0,
            count=1000
        ))
    
    return stats


@router.get("/node/{node_id}")
async def get_node_data(
    node_id: str,
    hours: int = Query(default=24, ge=1, le=168)
):
    """
    Obtiene datos de un nodo específico.
    
    Args:
        node_id: Identificador del nodo sensor
        hours: Horas de histórico
        
    Returns:
        Datos del nodo especificado
    """
    # TODO: Implementar soporte multi-nodo
    return {
        "node_id": node_id,
        "status": "online",
        "last_seen": datetime.now().isoformat(),
        "packet_count": 1500
    }
