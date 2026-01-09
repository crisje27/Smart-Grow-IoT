# 📚 API Reference - SMART GROW

Base URL: `http://localhost:8000/api/v1`

Documentación interactiva: `http://localhost:8000/docs`

---

## Sensores

### GET /sensors/latest
Obtiene la última lectura de todos los sensores.

**Response 200:**
```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "temperature": 22.5,
  "humidity": 65.2,
  "soil_humidity": 55.0,
  "soil_temp": 18.5,
  "light": 12500,
  "pressure": 1013.2,
  "rssi": -72,
  "snr": 9.5
}
```

### GET /sensors/history
Obtiene histórico de lecturas.

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| hours | int | 24 | Horas hacia atrás (1-168) |
| aggregation | string | "10m" | Intervalo (1m, 5m, 10m, 30m, 1h) |

**Response 200:**
```json
{
  "hours": 24,
  "aggregation": "10m",
  "count": 144,
  "data": [...]
}
```

### GET /sensors/stats
Obtiene estadísticas (min, max, mean).

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| hours | int | 24 | Período de cálculo |
| fields | string | null | Campos separados por coma |

---

## Predicciones

### GET /predictions/frost
Predicción actual de riesgo de helada.

**Response 200:**
```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "probability": 15.5,
  "risk_level": "low",
  "confidence": 87.0,
  "hours_ahead": 12,
  "contributing_factors": [
    "Temperatura estable",
    "Presión normal"
  ],
  "recommendation": "Condiciones normales."
}
```

### GET /predictions/disease
Predicción de condiciones favorables para enfermedades.

**Response 200:**
```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "risk_level": "medium",
  "probability": 45.0,
  "favorable_conditions": false,
  "humidity_factor": 0.75,
  "temperature_factor": 1.0,
  "duration_hours": 0,
  "recommendation": "Monitorear humedad."
}
```

### GET /predictions/model/info
Información y métricas del modelo.

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| model | string | "frost" | Modelo (frost, disease) |

---

## Alertas

### GET /alerts/active
Obtiene alertas activas no reconocidas.

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| severity | string | Filtrar (info, warning, critical) |
| alert_type | string | Filtrar por tipo |

### POST /alerts/{alert_id}/acknowledge
Marca una alerta como leída.

### GET /alerts/config
Obtiene configuración de umbrales.

### PUT /alerts/config/{alert_type}
Actualiza configuración de un tipo de alerta.

---

## Sistema

### GET /system/status
Estado de todos los componentes.

### GET /system/info
Información de hardware y software.

### GET /system/metrics
Métricas operacionales.

---

## Health Check

### GET /health
```json
{
  "status": "healthy",
  "service": "smartgrow-api",
  "version": "1.0.0"
}
```

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Parámetros inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error |

---

## Ejemplos con cURL

```bash
# Última lectura
curl http://localhost:8000/api/v1/sensors/latest

# Histórico 6 horas
curl "http://localhost:8000/api/v1/sensors/history?hours=6"

# Predicción heladas
curl http://localhost:8000/api/v1/predictions/frost

# Alertas activas
curl http://localhost:8000/api/v1/alerts/active
```

---

*SMART GROW API v1.0.0*
