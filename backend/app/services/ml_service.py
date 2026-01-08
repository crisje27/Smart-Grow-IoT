"""
SMART GROW - Servicio de Machine Learning
==========================================
Predicción de heladas y enfermedades usando modelos pre-entrenados.
"""

import os
import logging
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class MLService:
    """Servicio de predicción con Machine Learning."""
    
    def __init__(self, models_path: str = "/app/ml_models"):
        """
        Inicializa el servicio cargando los modelos.
        
        Args:
            models_path: Ruta a los archivos de modelos
        """
        self.models_path = models_path
        self.frost_model = None
        self.disease_model = None
        
        self._load_models()
    
    def _load_models(self):
        """Carga los modelos pre-entrenados."""
        try:
            frost_path = os.path.join(self.models_path, "frost_model.joblib")
            if os.path.exists(frost_path):
                self.frost_model = joblib.load(frost_path)
                logger.info("✓ Modelo de heladas cargado")
            else:
                logger.warning(f"Modelo de heladas no encontrado: {frost_path}")
        except Exception as e:
            logger.error(f"Error cargando modelo de heladas: {e}")
        
        try:
            disease_path = os.path.join(self.models_path, "disease_model.joblib")
            if os.path.exists(disease_path):
                self.disease_model = joblib.load(disease_path)
                logger.info("✓ Modelo de enfermedades cargado")
            else:
                logger.warning(f"Modelo de enfermedades no encontrado: {disease_path}")
        except Exception as e:
            logger.error(f"Error cargando modelo de enfermedades: {e}")
    
    def calculate_dew_point(self, temperature: float, humidity: float) -> float:
        """
        Calcula el punto de rocío usando la fórmula de Magnus-Tetens.
        
        Args:
            temperature: Temperatura en °C
            humidity: Humedad relativa en %
            
        Returns:
            Punto de rocío en °C
        """
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return round(dew_point, 2)
    
    def prepare_frost_features(self, sensor_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> np.ndarray:
        """
        Prepara las features para el modelo de heladas.
        
        Features:
        1. temperature - Temperatura actual del aire
        2. humidity - Humedad relativa
        3. soil_temp - Temperatura del suelo
        4. temp_differential - Diferencial térmico aire-suelo
        5. dew_point - Punto de rocío calculado
        6. pressure - Presión barométrica
        7. pressure_change_12h - Cambio de presión en 12h
        8. light - Intensidad lumínica
        9. hour_of_day - Hora del día (0-23)
        10. month - Mes del año (1-12)
        
        Args:
            sensor_data: Datos actuales de sensores
            historical_data: Datos históricos para calcular tendencias
            
        Returns:
            Array de features para el modelo
        """
        temperature = sensor_data.get('temperature', 15.0)
        humidity = sensor_data.get('humidity', 60.0)
        soil_temp = sensor_data.get('soil_temp', temperature - 2)
        pressure = sensor_data.get('pressure', 1013.25)
        light = sensor_data.get('light', 0)
        
        # Calcular features derivadas
        temp_differential = temperature - soil_temp
        dew_point = self.calculate_dew_point(temperature, humidity)
        
        # Cambio de presión (usar histórico si está disponible)
        pressure_change = 0.0
        if historical_data and len(historical_data) >= 72:  # 12h con datos cada 10min
            old_pressure = historical_data[0].get('pressure', pressure)
            pressure_change = pressure - old_pressure
        
        # Hora y mes actuales
        now = datetime.now()
        hour = now.hour
        month = now.month
        
        features = np.array([[
            temperature,
            humidity,
            soil_temp,
            temp_differential,
            dew_point,
            pressure,
            pressure_change,
            light,
            hour,
            month
        ]])
        
        return features
    
    def predict_frost(self, sensor_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Predice el riesgo de helada.
        
        Args:
            sensor_data: Datos actuales de sensores
            historical_data: Datos históricos
            
        Returns:
            Predicción con probabilidad y recomendaciones
        """
        features = self.prepare_frost_features(sensor_data, historical_data)
        
        # Si el modelo no está cargado, usar heurísticas
        if self.frost_model is None:
            return self._frost_heuristic(sensor_data)
        
        try:
            # Predicción con probabilidad
            probability = self.frost_model.predict_proba(features)[0][1] * 100
            prediction = self.frost_model.predict(features)[0]
            
            # Determinar nivel de riesgo
            if probability < 30:
                risk_level = "low"
                recommendation = "Condiciones normales. No se requieren medidas preventivas."
            elif probability < 70:
                risk_level = "medium"
                recommendation = "Riesgo moderado. Considere preparar medidas de protección."
            else:
                risk_level = "high"
                recommendation = "Alto riesgo de helada. Activar medidas de protección inmediatamente."
            
            # Factores contribuyentes
            factors = self._analyze_frost_factors(sensor_data)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "probability": round(probability, 1),
                "risk_level": risk_level,
                "confidence": 87.0,  # Basado en métricas de entrenamiento
                "hours_ahead": 12,
                "contributing_factors": factors,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Error en predicción de heladas: {e}")
            return self._frost_heuristic(sensor_data)
    
    def _frost_heuristic(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción heurística cuando el modelo no está disponible."""
        temp = sensor_data.get('temperature', 15.0)
        humidity = sensor_data.get('humidity', 60.0)
        dew_point = self.calculate_dew_point(temp, humidity)
        
        # Heurística simple basada en temperatura y punto de rocío
        if temp <= 2:
            probability = 90.0
            risk_level = "high"
        elif temp <= 5 and dew_point <= 0:
            probability = 70.0
            risk_level = "high"
        elif temp <= 8 and dew_point <= 2:
            probability = 45.0
            risk_level = "medium"
        elif temp <= 10:
            probability = 20.0
            risk_level = "low"
        else:
            probability = 5.0
            risk_level = "low"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "probability": probability,
            "risk_level": risk_level,
            "confidence": 60.0,  # Menor confianza para heurística
            "hours_ahead": 12,
            "contributing_factors": self._analyze_frost_factors(sensor_data),
            "recommendation": self._get_frost_recommendation(risk_level),
            "note": "Predicción heurística - modelo ML no disponible"
        }
    
    def _analyze_frost_factors(self, sensor_data: Dict[str, Any]) -> List[str]:
        """Analiza factores que contribuyen al riesgo de helada."""
        factors = []
        
        temp = sensor_data.get('temperature', 15.0)
        humidity = sensor_data.get('humidity', 60.0)
        light = sensor_data.get('light', 10000)
        pressure = sensor_data.get('pressure', 1013.25)
        
        if temp < 5:
            factors.append(f"Temperatura baja ({temp:.1f}°C)")
        if humidity > 80:
            factors.append(f"Humedad alta ({humidity:.1f}%)")
        if light < 100:
            factors.append("Cielo despejado (radiación nocturna)")
        if pressure > 1020:
            factors.append("Alta presión (cielo despejado probable)")
        
        if not factors:
            factors.append("Sin factores de riesgo significativos")
        
        return factors
    
    def _get_frost_recommendation(self, risk_level: str) -> str:
        """Obtiene recomendación según nivel de riesgo."""
        recommendations = {
            "low": "Condiciones normales. No se requieren medidas preventivas.",
            "medium": "Riesgo moderado. Considere preparar medidas de protección.",
            "high": "Alto riesgo de helada. Activar medidas de protección inmediatamente."
        }
        return recommendations.get(risk_level, "Monitorear condiciones.")
    
    def prepare_disease_features(self, sensor_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> np.ndarray:
        """
        Prepara features para el modelo de enfermedades.
        
        Features:
        1. temperature - Temperatura
        2. humidity - Humedad relativa
        3. soil_humidity - Humedad del suelo
        4. humidity_duration - Horas con humedad >85%
        5. temp_in_range - Temperatura en rango óptimo fúngico (15-25°C)
        6. light - Intensidad lumínica
        """
        temperature = sensor_data.get('temperature', 20.0)
        humidity = sensor_data.get('humidity', 60.0)
        soil_humidity = sensor_data.get('soil_humidity', 50.0)
        light = sensor_data.get('light', 10000)
        
        # Calcular duración de humedad alta
        humidity_duration = 0
        if historical_data:
            for data in historical_data:
                if data.get('humidity', 0) > 85:
                    humidity_duration += 1  # Cada registro = ~10 min
            humidity_duration = humidity_duration / 6  # Convertir a horas
        
        # Temperatura en rango óptimo para hongos
        temp_in_range = 1 if 15 <= temperature <= 25 else 0
        
        features = np.array([[
            temperature,
            humidity,
            soil_humidity,
            humidity_duration,
            temp_in_range,
            light
        ]])
        
        return features
    
    def predict_disease(self, sensor_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Predice riesgo de condiciones favorables para enfermedades fúngicas.
        
        Args:
            sensor_data: Datos actuales de sensores
            historical_data: Datos históricos
            
        Returns:
            Predicción de riesgo de enfermedades
        """
        features = self.prepare_disease_features(sensor_data, historical_data)
        
        humidity = sensor_data.get('humidity', 60.0)
        temperature = sensor_data.get('temperature', 20.0)
        
        # Si el modelo no está cargado, usar heurísticas
        if self.disease_model is None:
            return self._disease_heuristic(sensor_data, features[0])
        
        try:
            probability = self.disease_model.predict_proba(features)[0][1] * 100
            
            if probability < 30:
                risk_level = "low"
            elif probability < 70:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            favorable = humidity > 85 and 15 <= temperature <= 25
            
            return {
                "timestamp": datetime.now().isoformat(),
                "risk_level": risk_level,
                "probability": round(probability, 1),
                "favorable_conditions": favorable,
                "humidity_factor": round(humidity / 100, 2),
                "temperature_factor": round(1.0 if 15 <= temperature <= 25 else 0.5, 2),
                "duration_hours": int(features[0][3]),
                "recommendation": self._get_disease_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error en predicción de enfermedades: {e}")
            return self._disease_heuristic(sensor_data, features[0])
    
    def _disease_heuristic(self, sensor_data: Dict[str, Any], features: np.ndarray) -> Dict[str, Any]:
        """Predicción heurística para enfermedades."""
        humidity = sensor_data.get('humidity', 60.0)
        temperature = sensor_data.get('temperature', 20.0)
        
        favorable = humidity > 85 and 15 <= temperature <= 25
        
        if favorable and features[3] > 6:  # >6 horas de humedad alta
            risk_level = "high"
            probability = 85.0
        elif favorable:
            risk_level = "medium"
            probability = 55.0
        elif humidity > 75:
            risk_level = "low"
            probability = 25.0
        else:
            risk_level = "low"
            probability = 10.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "risk_level": risk_level,
            "probability": probability,
            "favorable_conditions": favorable,
            "humidity_factor": round(humidity / 100, 2),
            "temperature_factor": round(1.0 if 15 <= temperature <= 25 else 0.5, 2),
            "duration_hours": int(features[3]),
            "recommendation": self._get_disease_recommendation(risk_level),
            "note": "Predicción heurística - modelo ML no disponible"
        }
    
    def _get_disease_recommendation(self, risk_level: str) -> str:
        """Obtiene recomendación para enfermedades."""
        recommendations = {
            "low": "Condiciones no favorables para enfermedades fúngicas.",
            "medium": "Monitorear humedad foliar. Considerar aplicación preventiva.",
            "high": "Condiciones muy favorables. Aplicar fungicida preventivo."
        }
        return recommendations.get(risk_level, "Monitorear condiciones.")
    
    def get_feature_importance(self, model_type: str = "frost") -> List[Dict[str, Any]]:
        """
        Obtiene la importancia de features del modelo.
        
        Args:
            model_type: 'frost' o 'disease'
            
        Returns:
            Lista de features con su importancia
        """
        if model_type == "frost":
            model = self.frost_model
            feature_names = [
                "temperature", "humidity", "soil_temp", "temp_differential",
                "dew_point", "pressure", "pressure_change_12h", "light",
                "hour_of_day", "month"
            ]
        else:
            model = self.disease_model
            feature_names = [
                "temperature", "humidity", "soil_humidity",
                "humidity_duration", "temp_in_range", "light"
            ]
        
        if model is None:
            return []
        
        try:
            importances = model.feature_importances_
            
            result = []
            for name, importance in zip(feature_names, importances):
                result.append({
                    "feature": name,
                    "importance": round(float(importance), 4)
                })
            
            # Ordenar por importancia
            result.sort(key=lambda x: x["importance"], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo importancia de features: {e}")
            return []
