"""
Router de Sensores - SMART GROW API
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.services.influx_service import InfluxService

router = APIRouter()
influx = InfluxService()


# ═══════════════════════════════════════════════════════════════════════════
# MODELOS
# ═══════════════════════════════════════════════════════════════════════════

class SensorReading(BaseModel):
    """Lectura de sensores"""
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
    """Estadísticas de un sensor"""
    field: str
    min: float
    max: float
    mean: float
    count: int


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/latest", response_model=SensorReading)
async def get_latest_reading():
    """
    Obtiene la última lectura de todos los sensores.
    
    Returns:
        Última lectura con todos los valores de sensores
    """
    try:
        data = await influx.get_latest()
        if not data:
            raise HTTPException(
                status_code=404,
                detail="No hay datos disponibles"
            )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    hours: int = Query(default=24, ge=1, le=168, description="Horas de histórico (1-168)"),
    aggregation: str = Query(default="10m", description="Intervalo de agregación (1m, 5m, 10m, 1h)")
):
    """
    Obtiene el histórico de lecturas de sensores.
    
    Args:
        hours: Cantidad de horas hacia atrás (máximo 168 = 7 días)
        aggregation: Intervalo de agregación de datos
        
    Returns:
        Lista de lecturas agregadas
    """
    valid_aggregations = ["1m", "5m", "10m", "30m", "1h"]
    if aggregation not in valid_aggregations:
        raise HTTPException(
            status_code=400,
            detail=f"Agregación inválida. Usar: {valid_aggregations}"
        )
    
    try:
        data = await influx.get_history(hours=hours, aggregation=aggregation)
        return {
            "hours": hours,
            "aggregation": aggregation,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=List[SensorStats])
async def get_statistics(
    hours: int = Query(default=24, ge=1, le=168),
    fields: Optional[str] = Query(
        default=None,
        description="Campos separados por coma (ej: temperature,humidity)"
    )
):
    """
    Obtiene estadísticas de los sensores.
    
    Args:
        hours: Período de cálculo en horas
        fields: Campos específicos (opcional, todos por defecto)
        
    Returns:
        Estadísticas (min, max, mean) por campo
    """
    all_fields = ["temperature", "humidity", "soil_humidity", "soil_temp", "light", "pressure"]
    
    if fields:
        selected_fields = [f.strip() for f in fields.split(",")]
        invalid = [f for f in selected_fields if f not in all_fields]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Campos inválidos: {invalid}. Válidos: {all_fields}"
            )
    else:
        selected_fields = all_fields
    
    try:
        stats = await influx.get_stats(hours=hours, fields=selected_fields)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node/{node_id}")
async def get_node_data(
    node_id: str,
    hours: int = Query(default=24, ge=1, le=168)
):
    """
    Obtiene datos de un nodo específico.
    
    Args:
        node_id: Identificador del nodo (ej: node1)
        hours: Período en horas
        
    Returns:
        Datos del nodo especificado
    """
    try:
        data = await influx.get_by_node(node_id=node_id, hours=hours)
        return {
            "node_id": node_id,
            "hours": hours,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
