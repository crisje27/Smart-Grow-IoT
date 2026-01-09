"""
Configuración del Backend SMART GROW
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Aplicación
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # InfluxDB
    INFLUX_URL: str = os.getenv("INFLUX_URL", "http://localhost:8086")
    INFLUX_TOKEN: str = os.getenv("INFLUX_TOKEN", "smartgrow-token-change-me")
    INFLUX_ORG: str = os.getenv("INFLUX_ORG", "smartgrow")
    INFLUX_BUCKET: str = os.getenv("INFLUX_BUCKET", "agricola")
    
    # MQTT
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    
    # Machine Learning
    ML_MODELS_PATH: str = os.getenv("ML_MODELS_PATH", "/app/ml_models")
    ML_CACHE_TTL: int = 600  # 10 minutos
    
    # Alertas
    FROST_THRESHOLD_WARNING: float = 5.0  # °C
    FROST_THRESHOLD_CRITICAL: float = 0.0  # °C
    SOIL_DRY_THRESHOLD: float = 30.0  # %
    DISEASE_HUMIDITY_THRESHOLD: float = 85.0  # %
    
    class Config:
        env_file = ".env"


settings = Settings()
