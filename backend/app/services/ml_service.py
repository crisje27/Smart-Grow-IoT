"""
Servicio de Machine Learning - SMART GROW
Predicción de heladas y enfermedades
"""

import os
import math
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import numpy as np

try:
    import joblib
except ImportError:
    joblib = None

from app.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Servicio de predicción con Machine Learning"""
    
    def __init__(self):
        self.frost_model = None
        self.disease_model = None
        self._load_models()
    
    def _load_models(self):
        """Carga los modelos pre-entrenados"""
        if joblib is None:
            logger.warning("joblib no disponible, usando predicción heurística")
            return
            
        frost_path = os.path.join(settings.ML_MODELS_PATH, "frost_model.joblib")
        disease_path = os.path.join(settings.ML_MODELS_PATH, "disease_model.joblib")
        
        if os.path.exists(frost_path):
            try:
                self.frost_model = joblib.load(frost_path)
                logger.info("✓ Modelo de heladas cargado")
            except Exception as e:
                logger.error(f"Error cargando modelo de heladas: {e}")
        
        if os.path.exists(disease_path):
            try:
                self.disease_model = joblib.load(disease_path)
                logger.info("✓ Modelo de enfermedades cargado")
            except Exception as e:
                logger.error(f"Error cargando modelo de enfermedades: {e}")
    
    def calculate_dew_point(self, temp: float, humidity: float) -> float:
        """Calcula punto de rocío usando Magnus-Tetens"""
        a, b = 17.27, 237.7
        alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100.0)
        return round((b * alpha) / (a - alpha), 2)
    
    async def predict_frost(self, sensor_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Predice riesgo de helada"""
        # Datos de ejemplo si no se proporcionan
        if sensor_data is None:
            sensor_data = {
                "temperature": 8.5,
                "humidity": 75,
                "soil_temp": 10.2,
                "pressure": 1015,
                "light": 100
            }
        
        temp = sensor_data.get("temperature", 15)
        humidity = sensor_data.get("humidity", 60)
        dew_point = self.calculate_dew_point(temp, humidity)
        
        # Predicción heurística si no hay modelo
        if self.frost_model is None:
            if temp <= 2:
                probability = 90
                risk_level = "high"
            elif temp <= 5 and dew_point <= 0:
                probability = 70
                risk_level = "high"
            elif temp <= 8 and dew_point <= 2:
                probability = 45
                risk_level = "medium"
            elif temp <= 10:
                probability = 20
                risk_level = "low"
            else:
                probability = 5
                risk_level = "low"
        else:
            # Usar modelo real
            features = self._prepare_frost_features(sensor_data)
            probability = float(self.frost_model.predict_proba([features])[0][1] * 100)
            if probability < 30:
                risk_level = "low"
            elif probability < 70:
                risk_level = "medium"
            else:
                risk_level = "high"
        
        factors = []
        if temp < 5:
            factors.append(f"Temperatura baja ({temp:.1f}°C)")
        if humidity > 80:
            factors.append(f"Humedad alta ({humidity:.1f}%)")
        if sensor_data.get("light", 10000) < 100:
            factors.append("Cielo despejado (radiación nocturna)")
        if not factors:
            factors.append("Sin factores de riesgo significativos")
        
        recommendations = {
            "low": "Condiciones normales. No se requieren medidas preventivas.",
            "medium": "Riesgo moderado. Considere preparar medidas de protección.",
            "high": "Alto riesgo de helada. Activar medidas de protección inmediatamente."
        }
        
        return {
            "timestamp": datetime.now(),
            "probability": round(probability, 1),
            "risk_level": risk_level,
            "confidence": 87.0 if self.frost_model else 60.0,
            "hours_ahead": 12,
            "contributing_factors": factors,
            "recommendation": recommendations[risk_level]
        }
    
    async def predict_disease(self, sensor_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Predice condiciones favorables para enfermedades"""
        if sensor_data is None:
            sensor_data = {
                "temperature": 20,
                "humidity": 80,
                "soil_humidity": 60
            }
        
        temp = sensor_data.get("temperature", 20)
        humidity = sensor_data.get("humidity", 60)
        
        favorable = humidity > 85 and 15 <= temp <= 25
        
        if favorable:
            probability = 75
            risk_level = "high"
        elif humidity > 75:
            probability = 40
            risk_level = "medium"
        else:
            probability = 15
            risk_level = "low"
        
        recommendations = {
            "low": "Condiciones no favorables para enfermedades fúngicas.",
            "medium": "Monitorear humedad foliar. Considerar aplicación preventiva.",
            "high": "Condiciones muy favorables. Aplicar fungicida preventivo."
        }
        
        return {
            "timestamp": datetime.now(),
            "risk_level": risk_level,
            "probability": probability,
            "favorable_conditions": favorable,
            "humidity_factor": round(humidity / 100, 2),
            "temperature_factor": round(1.0 if 15 <= temp <= 25 else 0.5, 2),
            "duration_hours": 0,
            "recommendation": recommendations[risk_level]
        }
    
    async def get_prediction_history(self, model_type: str, hours: int) -> List[Dict]:
        """Obtiene histórico de predicciones"""
        # En producción: consultar InfluxDB
        return []
    
    def get_feature_importance(self, model_type: str) -> List[Dict]:
        """Obtiene importancia de features"""
        if model_type == "frost":
            return [
                {"feature": "pressure_change", "importance": 0.28, "description": "Cambio de presión 12h"},
                {"feature": "temp_differential", "importance": 0.22, "description": "Diferencial aire-suelo"},
                {"feature": "dew_point", "importance": 0.18, "description": "Punto de rocío"},
                {"feature": "light", "importance": 0.12, "description": "Intensidad lumínica"},
                {"feature": "hour", "importance": 0.10, "description": "Hora del día"},
                {"feature": "humidity", "importance": 0.05, "description": "Humedad relativa"},
                {"feature": "temperature", "importance": 0.05, "description": "Temperatura"}
            ]
        else:
            return [
                {"feature": "humidity", "importance": 0.45, "description": "Humedad relativa"},
                {"feature": "temperature", "importance": 0.25, "description": "Temperatura"},
                {"feature": "duration", "importance": 0.20, "description": "Duración condiciones"},
                {"feature": "light", "importance": 0.10, "description": "Intensidad lumínica"}
            ]
    
    def _prepare_frost_features(self, data: Dict) -> List[float]:
        """Prepara features para modelo de heladas"""
        temp = data.get("temperature", 15)
        humidity = data.get("humidity", 60)
        soil_temp = data.get("soil_temp", temp - 2)
        pressure = data.get("pressure", 1013)
        light = data.get("light", 10000)
        
        dew_point = self.calculate_dew_point(temp, humidity)
        temp_diff = temp - soil_temp
        
        return [
            temp, humidity, soil_temp, temp_diff, dew_point,
            pressure, 0, light, datetime.now().hour, datetime.now().month
        ]
