"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         SMART GROW - Backend API                              ║
║                                                                               ║
║  API REST para sistema IoT agrícola con Machine Learning                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Endpoints principales:
- /api/v1/sensors     : Datos de sensores (actual e histórico)
- /api/v1/predictions : Predicciones ML (heladas y enfermedades)
- /api/v1/alerts      : Sistema de alertas
- /api/v1/system      : Estado del sistema

Autor: Cristian Rodríguez - UTN FRT
Versión: 1.0.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.routers import sensors, predictions, alerts, system
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando SMART GROW API...")
    logger.info(f"   Versión: {settings.VERSION}")
    logger.info(f"   InfluxDB: {settings.INFLUX_URL}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Deteniendo SMART GROW API...")


# Crear aplicación FastAPI
app = FastAPI(
    title="SMART GROW API",
    description="""
## Sistema IoT LoRa con Machine Learning para Agricultura de Precisión

### Funcionalidades

* 📊 **Sensores**: Consulta de datos actuales e históricos
* 🤖 **Predicciones**: Modelos ML para heladas y enfermedades
* 🚨 **Alertas**: Sistema de notificaciones por umbrales
* ⚙️ **Sistema**: Monitoreo y estado del gateway

### Autor
Cristian Rodríguez - UTN Facultad Regional Tucumán
    """,
    version=settings.VERSION,
    contact={
        "name": "Cristian Rodríguez",
        "url": "https://github.com/crisje27",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(
    sensors.router,
    prefix="/api/v1/sensors",
    tags=["📊 Sensores"]
)
app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["🤖 Predicciones ML"]
)
app.include_router(
    alerts.router,
    prefix="/api/v1/alerts",
    tags=["🚨 Alertas"]
)
app.include_router(
    system.router,
    prefix="/api/v1/system",
    tags=["⚙️ Sistema"]
)


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS RAÍZ
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz - Información del API"""
    return {
        "service": "SMART GROW API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "sensors": "/api/v1/sensors",
            "predictions": "/api/v1/predictions",
            "alerts": "/api/v1/alerts",
            "system": "/api/v1/system"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check para Docker y monitoreo"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "smartgrow-api",
            "version": settings.VERSION
        }
    )


# ═══════════════════════════════════════════════════════════════════════════
# MANEJO DE ERRORES
# ═══════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "Error interno del servidor"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
