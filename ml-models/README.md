# 🤖 Modelos de Machine Learning - SMART GROW

## Descripción

Este directorio contiene los modelos de Machine Learning para predicción agrícola:

1. **Modelo de Heladas** (`frost_model.joblib`) - XGBoost
2. **Modelo de Enfermedades** (`disease_model.joblib`) - Random Forest

## Estructura

```
ml-models/
├── notebooks/
│   └── train_models.ipynb    # Notebook de entrenamiento
├── models/
│   ├── frost_model.joblib    # Modelo de heladas entrenado
│   └── disease_model.joblib  # Modelo de enfermedades entrenado
└── README.md
```

## Modelo de Heladas (XGBoost)

### Features de Entrada

| Feature | Descripción | Unidad |
|---------|-------------|--------|
| temperature | Temperatura del aire | °C |
| humidity | Humedad relativa | % |
| soil_temp | Temperatura del suelo | °C |
| temp_differential | Diferencial aire-suelo | °C |
| dew_point | Punto de rocío calculado | °C |
| pressure | Presión barométrica | hPa |
| pressure_change | Cambio de presión (12h) | hPa |
| light | Intensidad lumínica | lux |
| hour | Hora del día | 0-23 |
| month | Mes del año | 1-12 |

### Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| Accuracy | 91% |
| Precision | 87% |
| Recall | 93% |
| F1-Score | 90% |
| AUC-ROC | 95% |

### Importancia de Variables

1. `pressure_change` (28%) - Cambio de presión
2. `temp_differential` (22%) - Diferencial térmico
3. `dew_point` (18%) - Punto de rocío
4. `light` (12%) - Intensidad lumínica
5. `hour` (10%) - Hora del día

## Modelo de Enfermedades (Random Forest)

### Features de Entrada

| Feature | Descripción | Unidad |
|---------|-------------|--------|
| temperature | Temperatura del aire | °C |
| humidity | Humedad relativa | % |
| soil_humidity | Humedad del suelo | % |
| light | Intensidad lumínica | lux |
| hour | Hora del día | 0-23 |
| month | Mes del año | 1-12 |

### Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| Accuracy | 99% |
| Precision | 98% |
| Recall | 99% |
| F1-Score | 98.5% |

## Uso

### Cargar Modelo

```python
import joblib

# Cargar modelo de heladas
frost_model = joblib.load('models/frost_model.joblib')

# Preparar features (debe ser array 2D)
features = [[
    temperature,    # °C
    humidity,       # %
    soil_temp,      # °C
    temp_diff,      # °C
    dew_point,      # °C
    pressure,       # hPa
    pressure_change,# hPa
    light,          # lux
    hour,           # 0-23
    month           # 1-12
]]

# Predecir
probability = frost_model.predict_proba(features)[0][1]
prediction = frost_model.predict(features)[0]
```

### Cálculo del Punto de Rocío

```python
import math

def calculate_dew_point(temp, humidity):
    a, b = 17.27, 237.7
    alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100.0)
    return (b * alpha) / (a - alpha)
```

## Limitaciones

⚠️ **IMPORTANTE:**

1. **Datos Sintéticos:** Los modelos fueron entrenados con datos sintéticos calibrados para Tucumán
2. **Validación Requerida:** Se necesita validación en campo antes de uso en producción
3. **Reentrenamiento:** Recomendado reentrenar con 12+ meses de datos reales

## Reentrenamiento

Para reentrenar los modelos con datos reales:

1. Recolectar datos del sistema (mínimo 6 meses)
2. Etiquetar eventos de helada y enfermedades
3. Ejecutar `notebooks/train_models.ipynb` con datos reales
4. Validar métricas antes de desplegar

## Requisitos

```
scikit-learn>=1.3.0
xgboost>=2.0.0
joblib>=1.3.0
numpy>=1.26.0
pandas>=2.1.0
```

## Licencia

MIT License
