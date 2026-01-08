"""
SMART GROW - Backend FastAPI
============================
API REST para sistema IoT agrícola con predicción ML.

Endpoints:
- /api/v1/sensors - Datos de sensores
- /api/v1/predictions - Predicciones ML
- /api/v1/alerts - Sistema de alertas
- /api/v1/system - Estado del sistema

Autor: Cristian Rodríguez
Versión: 1.0.0
Licencia: MIT
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routers import sensors, predictions, alerts, system
from app.services.influx import InfluxService
from app.services.ml_service import MLService

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Servicios globales
influx_service = None
ml_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    global influx_service, ml_service
    
    logger.info("🚀 Iniciando SMART GROW API...")
    
    # Inicializar servicios
    try:
        influx_service = InfluxService()
        logger.info("✓ InfluxDB conectado")
    except Exception as e:
        logger.error(f"✗ Error conectando InfluxDB: {e}")
    
    try:
        ml_service = MLService()
        logger.info("✓ Modelos ML cargados")
    except Exception as e:
        logger.error(f"✗ Error cargando modelos ML: {e}")
    
    logger.info("✓ API iniciada correctamente")
    
    yield
    
    # Limpieza al cerrar
    logger.info("🛑 Cerrando SMART GROW API...")
    if influx_service:
        influx_service.close()


# Crear aplicación FastAPI
app = FastAPI(
    title="SMART GROW API",
    description="""
    API REST para sistema IoT de agricultura de precisión.
    
    ## Características
    - 📊 Consulta de datos de sensores en tiempo real
    - 🤖 Predicciones de heladas y enfermedades con ML
    - 🔔 Sistema de alertas configurables
    - 📈 Históricos y estadísticas
    
    ## Autenticación
    Esta versión no requiere autenticación (uso en red local).
    """,
    version="1.0.0",
    contact={
        "name": "Cristian Rodríguez",
        "url": "https://github.com/crisje27/SMART-GROW-SISTEMA-IoT-LoRa-CON-MACHINE-LEARNING-PARA-AGRICULTURA-DE-PRECISI-N",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(
    sensors.router,
    prefix="/api/v1/sensors",
    tags=["Sensores"]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["Predicciones ML"]
)

app.include_router(
    alerts.router,
    prefix="/api/v1/alerts",
    tags=["Alertas"]
)

app.include_router(
    system.router,
    prefix="/api/v1/system",
    tags=["Sistema"]
)


# ==========================================================================
# ENDPOINTS RAÍZ
# ==========================================================================

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "service": "SMART GROW API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check para Docker y monitoreo."""
    return {
        "status": "healthy",
        "influxdb": influx_service is not None,
        "ml_models": ml_service is not None
    }


# ==========================================================================
# MAIN
# ==========================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
