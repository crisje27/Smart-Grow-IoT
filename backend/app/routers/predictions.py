"""
SMART GROW - Router de Predicciones ML
=======================================
Endpoints para predicciones de heladas y enfermedades.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

router = APIRouter()


# ==========================================================================
# MODELOS
# ==========================================================================

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FrostPrediction(BaseModel):
    """Predicción de heladas."""
    timestamp: datetime
    probability: float  # 0-100%
    risk_level: RiskLevel
    confidence: float  # 0-100%
    hours_ahead: int
    contributing_factors: List[str]
    recommendation: str


class DiseasePrediction(BaseModel):
    """Predicción de condiciones favorables a enfermedades."""
    timestamp: datetime
    risk_level: RiskLevel
    favorable_conditions: bool
    humidity_factor: float
    temperature_factor: float
    duration_hours: int
    recommendation: str


class FeatureImportance(BaseModel):
    """Importancia de variables en el modelo."""
    feature: str
    importance: float
    description: str


# ==========================================================================
# ENDPOINTS
# ==========================================================================

@router.get("/frost", response_model=FrostPrediction)
async def get_frost_prediction():
    """
    Obtiene predicción de heladas para las próximas 12-24 horas.
    
    El modelo XGBoost analiza:
    - Cambio de presión barométrica (12h)
    - Diferencial térmico aire-suelo
    - Punto de rocío
    - Intensidad lumínica (proxy nubosidad)
    - Humedad relativa
    - Hora del día
    
    Returns:
        Predicción con probabilidad, nivel de riesgo y recomendaciones
    """
    # TODO: Implementar predicción real con modelo XGBoost
    return FrostPrediction(
        timestamp=datetime.now(),
        probability=25.5,
        risk_level=RiskLevel.LOW,
        confidence=87.0,
        hours_ahead=12,
        contributing_factors=[
            "Presión estable",
            "Cielo parcialmente nublado",
            "Temperatura nocturna > 5°C"
        ],
        recommendation="Condiciones normales. No se requieren medidas preventivas."
    )


@router.get("/disease", response_model=DiseasePrediction)
async def get_disease_prediction():
    """
    Obtiene predicción de condiciones favorables para enfermedades fúngicas.
    
    El modelo Random Forest evalúa:
    - Humedad relativa sostenida >85% por >6 horas
    - Temperatura en rango 15-25°C
    - Humedad de suelo
    
    Returns:
        Predicción con nivel de riesgo y recomendaciones
    """
    # TODO: Implementar predicción real con modelo Random Forest
    return DiseasePrediction(
        timestamp=datetime.now(),
        risk_level=RiskLevel.MEDIUM,
        favorable_conditions=True,
        humidity_factor=0.75,
        temperature_factor=0.60,
        duration_hours=8,
        recommendation="Condiciones parcialmente favorables. Monitorear humedad foliar."
    )


@router.get("/frost/history")
async def get_frost_history(days: int = 7):
    """
    Obtiene histórico de predicciones de heladas.
    
    Args:
        days: Días de histórico (1-30)
        
    Returns:
        Lista de predicciones históricas
    """
    # TODO: Implementar consulta de histórico
    return []


@router.get("/features/importance", response_model=List[FeatureImportance])
async def get_feature_importance(model: str = "frost"):
    """
    Obtiene la importancia de variables del modelo especificado.
    
    Args:
        model: Modelo a consultar ('frost' o 'disease')
        
    Returns:
        Lista de features ordenadas por importancia
    """
    if model not in ["frost", "disease"]:
        raise HTTPException(status_code=400, detail="Modelo debe ser 'frost' o 'disease'")
    
    if model == "frost":
        return [
            FeatureImportance(
                feature="pressure_change_12h",
                importance=0.28,
                description="Cambio de presión barométrica en 12 horas"
            ),
            FeatureImportance(
                feature="temp_differential",
                importance=0.22,
                description="Diferencial térmico aire-suelo"
            ),
            FeatureImportance(
                feature="dew_point",
                importance=0.18,
                description="Punto de rocío calculado"
            ),
            FeatureImportance(
                feature="light_intensity",
                importance=0.12,
                description="Intensidad lumínica (proxy nubosidad)"
            ),
            FeatureImportance(
                feature="hour_of_day",
                importance=0.10,
                description="Hora del día"
            ),
            FeatureImportance(
                feature="humidity",
                importance=0.10,
                description="Humedad relativa"
            ),
        ]
    else:
        return [
            FeatureImportance(
                feature="humidity_duration",
                importance=0.35,
                description="Duración de humedad >85%"
            ),
            FeatureImportance(
                feature="temperature_range",
                importance=0.30,
                description="Temperatura en rango óptimo fúngico"
            ),
            FeatureImportance(
                feature="soil_humidity",
                importance=0.20,
                description="Humedad del suelo"
            ),
            FeatureImportance(
                feature="light_hours",
                importance=0.15,
                description="Horas de luz diarias"
            ),
        ]


@router.get("/model/info")
async def get_model_info(model: str = "frost"):
    """
    Obtiene información del modelo ML.
    
    Returns:
        Métricas de rendimiento y metadata del modelo
    """
    if model == "frost":
        return {
            "name": "Frost Prediction Model",
            "algorithm": "XGBoost",
            "version": "1.0.0",
            "training_date": "2025-01-15",
            "metrics": {
                "accuracy": 0.91,
                "precision": 0.87,
                "recall": 0.93,
                "f1_score": 0.90,
                "auc_roc": 0.95
            },
            "training_samples": 52993,
            "features": 10,
            "note": "Entrenado con datos sintéticos calibrados para Tucumán"
        }
    else:
        return {
            "name": "Disease Risk Model",
            "algorithm": "Random Forest",
            "version": "1.0.0",
            "training_date": "2025-01-15",
            "metrics": {
                "accuracy": 0.99,
                "precision": 0.98,
                "recall": 0.99,
                "f1_score": 0.985
            },
            "training_samples": 52993,
            "features": 6,
            "note": "Entrenado con datos sintéticos - Requiere validación en campo"
        }
