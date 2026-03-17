# 🌱 SMART GROW

## Sistema IoT LoRa con Machine Learning para Agricultura de Precisión

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-ESP32--S3-blue.svg)](https://www.espressif.com/)
[![LoRa](https://img.shields.io/badge/LoRa-915MHz-orange.svg)](https://lora-alliance.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)

---

## 📋 Descripción

**SMART GROW** es un sistema IoT de bajo costo para monitoreo agrícola y predicción de eventos climáticos adversos mediante Machine Learning. Diseñado específicamente para pequeños y medianos productores de la región NOA de Argentina.

### 🎯 Problema que Resuelve

- **Pérdidas por heladas**: Detección anticipada 12-24 horas antes del evento
- **Enfermedades fúngicas**: Identificación de condiciones favorables para patógenos
- **Alto costo de soluciones comerciales**: Alternativa 83% más económica
- **Falta de conectividad rural**: Operación autónoma sin internet

### ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 📡 **LoRa P2P** | Comunicación de largo alcance (3.5+ km urbano, 8-12 km rural) |
| 🌡️ **5 Sensores** | Temperatura aire/suelo, humedad aire/suelo, luz, presión |
| 🤖 **Machine Learning** | XGBoost (heladas 87% precisión) + Random Forest (enfermedades 99%) |
| 📱 **PWA Responsive** | Acceso desde cualquier dispositivo, instalable como app |
| ☀️ **Solar Autónomo** | >500 días de operación con panel de 0.75W |
| 🔒 **Acceso Remoto Seguro** | Cloudflare Tunnel sin exponer puertos |
| 💰 **Bajo Costo** | USD 270 total (83% menos que comerciales) |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARQUITECTURA SMART GROW                            │
└─────────────────────────────────────────────────────────────────────────────┘

 CAPA EDGE                    CAPA GATEWAY                    CAPA CLOUD
 ──────────                   ────────────                    ──────────

┌─────────────┐              ┌─────────────────────────────┐
│ NODO SENSOR │              │      RASPBERRY PI 4         │
│             │   LoRa P2P   │                             │
│ ┌─────────┐ │   915 MHz    │  ┌───────────────────────┐  │
│ │ DHT22   │ │ ═══════════► │  │   Docker Containers   │  │
│ │ DS18B20 │ │   3.5+ km    │  │                       │  │
│ │ HD-38   │ │              │  │  ┌─────┐ ┌─────────┐  │  │    Cloudflare
│ │ BH1750  │ │              │  │  │Influx│ │ FastAPI │  │  │     Tunnel
│ │ BMP280  │ │              │  │  │ DB   │ │  + ML   │  │  │ ════════════►
│ └─────────┘ │              │  │  └─────┘ └─────────┘  │  │
│             │              │  │  ┌─────┐ ┌─────────┐  │  │   ┌─────────┐
│ ┌─────────┐ │              │  │  │MQTT │ │ Grafana │  │  │   │ Usuario │
│ │ ESP32-S3│ │              │  │  └─────┘ └─────────┘  │  │   │ Remoto  │
│ │ SX1262  │ │              │  │  ┌─────┐ ┌─────────┐  │  │   └─────────┘
│ └─────────┘ │              │  │  │Node │ │   PWA   │  │  │
│             │              │  │  │-RED │ │ Vue.js  │  │  │
│ ┌─────────┐ │              │  │  └─────┘ └─────────┘  │  │
│ │ Solar   │ │              │  └───────────────────────┘  │
│ │ + LiPo  │ │              │                             │
│ └─────────┘ │              │  ┌───────────────────────┐  │
└─────────────┘              │  │   Waveshare SX1262    │  │
                             │  │        HAT            │  │
   USD 103                   │  └───────────────────────┘  │
                             └─────────────────────────────┘
                                        USD 167

                             ════════════════════════════════
                                    COSTO TOTAL: USD 270
                                   (83% menos que comercial)
```

---

## 📦 Estructura del Repositorio

```
SMART-GROW/
├── 📁 firmware/                    # Código del nodo sensor ESP32
│   └── nodo_sensor/
│       ├── nodo_sensor.ino         # Firmware principal
│       ├── config.h                # Configuración de pines y LoRa
│       └── README.md               # Instrucciones de instalación
│
├── 📁 gateway/                     # Software del gateway Raspberry Pi
│   ├── lora_receiver/
│   │   ├── lora_receiver.py        # Receptor LoRa principal
│   │   ├── mqtt_bridge.py          # Puente MQTT-InfluxDB
│   │   └── requirements.txt
│   ├── docker/
│   │   ├── docker-compose.yml      # Stack completo de servicios
│   │   └── .env.example            # Variables de entorno
│   ├── config/
│   │   ├── mosquitto/              # Configuración MQTT
│   │   └── grafana/                # Datasources y dashboards
│   └── scripts/
│       ├── install.sh              # Script de instalación
│       ├── start.sh                # Iniciar servicios
│       └── backup.sh               # Backup de datos
│
├── 📁 backend/                     # API REST FastAPI
│   ├── app/
│   │   ├── main.py                 # Punto de entrada
│   │   ├── config.py               # Configuración
│   │   ├── routers/                # Endpoints API
│   │   │   ├── sensors.py
│   │   │   ├── predictions.py
│   │   │   ├── alerts.py
│   │   │   └── system.py
│   │   ├── services/               # Lógica de negocio
│   │   │   ├── influx_service.py
│   │   │   ├── ml_service.py
│   │   │   └── alert_service.py
│   │   └── models/                 # Schemas Pydantic
│   │       └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 frontend/                    # PWA Vue.js 3
│   ├── src/
│   │   ├── components/             # Componentes reutilizables
│   │   ├── views/                  # Páginas principales
│   │   ├── services/               # Cliente API
│   │   └── store/                  # Estado global (Pinia)
│   ├── public/
│   │   └── manifest.json           # Configuración PWA
│   ├── Dockerfile
│   └── package.json
│
├── 📁 ml-models/                   # Machine Learning
│   ├── notebooks/
│   │   ├── 01_data_generation.ipynb
│   │   ├── 02_frost_model.ipynb
│   │   └── 03_disease_model.ipynb
│   ├── models/
│   │   ├── frost_model.joblib      # Modelo XGBoost entrenado
│   │   └── disease_model.joblib    # Modelo Random Forest
│   └── data/
│       └── synthetic_dataset.csv   # Dataset de entrenamiento
│
├── 📁 hardware/                    # Diseño de hardware
│   └── kicad/
│       ├── schematic.kicad_sch
│       └── pcb.kicad_pcb
│
├── 📁 docs/                        # Documentación
│   ├── instalacion.md
│   ├── configuracion.md
│   ├── api-reference.md
│   └── troubleshooting.md
│
├── 📁 tests/                       # Tests automatizados
│   ├── test_api.py
│   └── test_ml_service.py
│
├── .gitignore
├── LICENSE                         # MIT License
├── CONTRIBUTING.md
└── README.md                       # Este archivo
```

---

## 🔧 Hardware Requerido

### Nodo Sensor (USD 103)

| Componente | Modelo | Interfaz | Precio |
|------------|--------|----------|--------|
| Microcontrolador | Heltec WiFi LoRa 32 V3 | - | $35 |
| Temp/Hum Aire | DHT22 | GPIO 42 | $8 |
| Temp Suelo | DS18B20 (waterproof) | GPIO 1 (1-Wire) | $5 |
| Humedad Suelo | HD-38 (capacitivo) | GPIO 7 (ADC) | $4 |
| Luz | BH1750 | I2C (0x23) | $5 |
| Presión | BMP280 | I2C (0x76) | $6 |
| Batería | LiPo 3.7V 3100mAh | JST | $12 |
| Panel Solar | 5V 0.75W | Cable | $8 |
| Gabinete | Sonoff IP65 | - | $20 |

### Gateway (USD 167)

| Componente | Modelo | Precio |
|------------|--------|--------|
| SBC | Raspberry Pi 4 (4GB) | $85 |
| Módulo LoRa | Waveshare SX1262 HAT | $45 |
| Almacenamiento | microSD 64GB C10 | $15 |
| Fuente | 5V/3A USB-C | $10 |
| Gabinete | Case con ventilación | $12 |

---

## 🚀 Instalación Rápida

### Prerequisitos

- **Nodo**: Arduino IDE 2.x con soporte ESP32
- **Gateway**: Raspberry Pi OS Lite 64-bit, Docker

### 1. Clonar Repositorio

```bash
git clone https://github.com/crisje27/SMART-GROW-SISTEMA-IoT-LoRa-CON-MACHINE-LEARNING-PARA-AGRICULTURA-DE-PRECISI-N.git
cd SMART-GROW-*
```

### 2. Firmware del Nodo Sensor

```bash
# Abrir en Arduino IDE
# Instalar bibliotecas (ver firmware/nodo_sensor/README.md)
# Seleccionar: Heltec WiFi LoRa 32(V3)
# Subir: firmware/nodo_sensor/nodo_sensor.ino
```

### 3. Gateway Raspberry Pi

```bash
# Ejecutar script de instalación
cd gateway/scripts
chmod +x install.sh
./install.sh

# Iniciar servicios
./start.sh
```

### 4. Verificar Funcionamiento

```bash
# Ver estado de contenedores
docker compose ps

# Ver logs del receptor LoRa
journalctl -u smartgrow-lora -f

# Acceder a interfaces
# Grafana: http://IP:3000 (admin/smartgrow2025)
# API Docs: http://IP:8000/docs
# PWA: http://IP
```

---

## 📊 Métricas de Rendimiento

| Métrica | Valor | Condiciones |
|---------|-------|-------------|
| Tasa éxito TX LoRa | **96%** | 3 meses operación |
| Uptime sistema | **99.5%** | Incluye reinicios programados |
| Latencia local | **<10 ms** | API REST |
| Latencia remota | **<85 ms** | Desde Buenos Aires |
| Alcance urbano | **3.5 km** | Con obstáculos |
| Alcance rural | **8-12 km** | Línea de vista |
| Autonomía solar | **>500 días** | Panel 0.75W + batería 3100mAh |
| Consumo promedio | **0.18 mA** | TX cada 15 min |

---

## 🤖 Modelos de Machine Learning

### Predicción de Heladas (XGBoost)

| Métrica | Valor |
|---------|-------|
| Accuracy | 91% |
| Precision | 87% |
| Recall | 93% |
| F1-Score | 90% |
| AUC-ROC | 95% |

**Features principales:**
1. Cambio de presión barométrica (12h)
2. Diferencial térmico aire-suelo
3. Punto de rocío calculado
4. Intensidad lumínica (proxy nubosidad)
5. Hora del día

### Predicción de Enfermedades (Random Forest)

| Métrica | Valor |
|---------|-------|
| Accuracy | 99% |
| Precision | 98% |
| Recall | 99% |

**Condiciones detectadas:**
- Humedad >85% sostenida >6 horas
- Temperatura en rango 15-25°C
- Baja radiación solar

> ⚠️ **Nota**: Modelos entrenados con datos sintéticos calibrados para Tucumán. Se requiere validación en campo antes de uso en producción.

---

## 💰 Análisis Económico

### Comparación de Costos

| Solución | CAPEX | OPEX/mes | TCO 3 años |
|----------|-------|----------|------------|
| **SMART GROW** | **USD 270** | **USD 3** | **USD 378** |
| Davis Vantage Pro2 | USD 1,500 | USD 15 | USD 2,040 |
| Solución IoT comercial | USD 2,500 | USD 40 | USD 3,940 |

### Retorno de Inversión

- **VAN (5 años, 12%)**: USD 3,206
- **TIR**: 356%
- **Payback**: 3.4 meses
- **Punto de equilibrio**: 0.28 heladas prevenidas/año

---

## 📚 Documentación

- [📦 Guía de Instalación Completa](docs/instalacion.md)
- [⚙️ Configuración del Sistema](docs/configuracion.md)
- [🔌 Referencia de API](docs/api-reference.md)
- [🔧 Solución de Problemas](docs/troubleshooting.md)

---

## 🎓 Proyecto Final de Carrera

Este proyecto fue desarrollado como **Proyecto Final de Carrera** para la obtención del título de **Ingeniero Electrónico** en la **Universidad Tecnológica Nacional - Facultad Regional Tucumán (UTN-FRT)**.

**Autor:** Cristian Rodríguez  
**Director:** Ing. Ruben Egea  
**Año:** 2025

### Citar este trabajo

```bibtex
@thesis{rodriguez2025smartgrow,
  author  = {Rodríguez, Cristian},
  title   = {SMART GROW: Sistema IoT LoRa con Machine Learning para Agricultura de Precisión},
  school  = {Universidad Tecnológica Nacional - Facultad Regional Tucumán},
  year    = {2025},
  type    = {Proyecto Final de Carrera},
  address = {San Miguel de Tucumán, Argentina}
}
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar un Pull Request.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📧 Contacto

- **GitHub:** [@crisje27](https://github.com/crisje27)
- **LinkedIn:** https://www.linkedin.com/in/cristianfernando27
- **Email:** fernando270397@gmail.com

---

<p align="center">
  <b>Hecho en Tucumán, Argentina 🇦🇷</b>
  <br>
  <i>Democratizando la agricultura de precisión</i>
</p>
