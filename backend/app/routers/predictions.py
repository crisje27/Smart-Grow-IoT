"""
Router de Predicciones ML - SMART GROW API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()


# ═══════════════════════════════════════════════════════════════════════════
# MODELOS
# ═══════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FrostPrediction(BaseModel):
    """Predicción de heladas"""
    timestamp: datetime
    probability: float  # 0-100%
    risk_level: RiskLevel
    confidence: float  # Confianza del modelo
    hours_ahead: int  # Horizonte de predicción
    contributing_factors: List[str]
    recommendation: str


class DiseasePrediction(BaseModel):
    """Predicción de enfermedades"""
    timestamp: datetime
    risk_level: RiskLevel
    probability: float
    favorable_conditions: bool
    humidity_factor: float
    temperature_factor: float
    duration_hours: int
    recommendation: str


class FeatureImportance(BaseModel):
    """Importancia de features del modelo"""
    feature: str
    importance: float
    description: str


class ModelInfo(BaseModel):
    """Información del modelo"""
    name: str
    version: str
    algorithm: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float]
    training_date: str
    features_count: int


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/frost", response_model=FrostPrediction)
async def get_frost_prediction():
    """
    Obtiene la predicción actual de riesgo de heladas.
    
    El modelo XGBoost analiza las condiciones actuales y predice
    la probabilidad de helada en las próximas 12-24 horas.
    
    Returns:
        Predicción con probabilidad, nivel de riesgo y recomendaciones
    """
    try:
        prediction = await ml_service.predict_frost()
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disease", response_model=DiseasePrediction)
async def get_disease_prediction():
    """
    Obtiene la predicción de condiciones favorables para enfermedades.
    
    El modelo Random Forest evalúa si las condiciones actuales
    son propicias para el desarrollo de patógenos fúngicos.
    
    Returns:
        Predicción de riesgo de enfermedades fúngicas
    """
    try:
        prediction = await ml_service.predict_disease()
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/frost/history")
async def get_frost_prediction_history(
    hours: int = 24
):
    """
    Obtiene el histórico de predicciones de heladas.
    
    Args:
        hours: Horas de histórico (máximo 168)
        
    Returns:
        Lista de predicciones históricas
    """
    try:
        history = await ml_service.get_prediction_history("frost", hours)
        return {
            "model": "frost",
            "hours": hours,
            "count": len(history),
            "predictions": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features/importance", response_model=List[FeatureImportance])
async def get_feature_importance(
    model: str = "frost"
):
    """
    Obtiene la importancia de las variables para un modelo.
    
    Args:
        model: Nombre del modelo (frost o disease)
        
    Returns:
        Lista de features ordenadas por importancia
    """
    if model not in ["frost", "disease"]:
        raise HTTPException(
            status_code=400,
            detail="Modelo debe ser 'frost' o 'disease'"
        )
    
    try:
        importance = ml_service.get_feature_importance(model)
        return importance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/info", response_model=ModelInfo)
async def get_model_info(
    model: str = "frost"
):
    """
    Obtiene información y métricas del modelo.
    
    Args:
        model: Nombre del modelo (frost o disease)
        
    Returns:
        Métricas de rendimiento del modelo
    """
    models_info = {
        "frost": ModelInfo(
            name="Frost Prediction Model",
            version="1.0.0",
            algorithm="XGBoost",
            accuracy=0.91,
            precision=0.87,
            recall=0.93,
            f1_score=0.90,
            auc_roc=0.95,
            training_date="2025-01-15",
            features_count=10
        ),
        "disease": ModelInfo(
            name="Disease Risk Model",
            version="1.0.0",
            algorithm="Random Forest",
            accuracy=0.99,
            precision=0.98,
            recall=0.99,
            f1_score=0.985,
            auc_roc=0.99,
            training_date="2025-01-15",
            features_count=6
        )
    }
    
    if model not in models_info:
        raise HTTPException(
            status_code=400,
            detail="Modelo debe ser 'frost' o 'disease'"
        )
    
    return models_info[model]
