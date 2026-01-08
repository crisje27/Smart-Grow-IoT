# 🌱 SMART GROW - Sistema IoT LoRa con Machine Learning para Agricultura de Precisión

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-ESP32--S3-blue.svg)](https://www.espressif.com/)
[![LoRa](https://img.shields.io/badge/LoRa-915MHz-orange.svg)](https://lora-alliance.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

<p align="center">
  <img src="docs/images/smartgrow-banner.png" alt="SMART GROW Banner" width="600">
</p>

## 📋 Descripción

**SMART GROW** es un sistema IoT de bajo costo para monitoreo agrícola y predicción de eventos climáticos adversos, diseñado específicamente para pequeños y medianos productores de la región NOA de Argentina.

### 🎯 Características Principales

- 📡 **Comunicación LoRa P2P** - Alcance de 3.5+ km sin infraestructura adicional
- 🌡️ **5 sensores ambientales** - Temperatura, humedad, luz, presión y humedad de suelo
- 🤖 **Machine Learning integrado** - Predicción de heladas (12-24h) y enfermedades
- 📱 **PWA responsive** - Monitoreo desde cualquier dispositivo
- ☀️ **Autonomía solar** - Operación >500 días sin mantenimiento
- 💰 **Bajo costo** - 83% más económico que soluciones comerciales

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐         LoRa P2P          ┌─────────────────────────────────────┐
│   NODO SENSOR   │ ═══════════════════════►  │            GATEWAY                  │
│  Heltec V3      │        915 MHz            │         Raspberry Pi 4              │
│                 │        3.5+ km            │                                     │
│  • DHT22        │                           │  ┌─────────┐  ┌─────────────────┐  │
│  • DS18B20      │                           │  │InfluxDB │  │    FastAPI      │  │
│  • HD-38        │                           │  │   ⬇️    │  │   + ML Models   │  │
│  • BH1750       │                           │  │ Grafana │  │       ⬇️        │  │
│  • BMP280       │                           │  └─────────┘  │   Vue.js PWA    │  │
└─────────────────┘                           └───────────────┴─────────────────────┘
                                                        │
                                                        │ Cloudflare Tunnel
                                                        ▼
                                              ┌─────────────────────┐
                                              │   ACCESO GLOBAL     │
                                              │  app.iotagricola.org│
                                              └─────────────────────┘
```

---

## 📦 Estructura del Repositorio

```
smartgrow-iot/
├── firmware/                    # Código del nodo sensor
│   └── nodo_sensor/
│       └── nodo_sensor.ino      # Firmware Arduino ESP32
├── gateway/                     # Software del gateway
│   ├── lora_receiver/
│   │   └── lora_receiver.py     # Receptor LoRa Python
│   ├── docker/
│   │   └── docker-compose.yml   # Stack de servicios
│   └── config/                  # Configuraciones de servicios
├── backend/                     # API REST FastAPI
│   └── app/
│       ├── main.py
│       ├── routers/
│       ├── services/
│       └── models/
├── frontend/                    # PWA Vue.js
│   └── src/
│       ├── components/
│       └── services/
├── ml-models/                   # Modelos de Machine Learning
│   ├── notebooks/               # Jupyter notebooks de entrenamiento
│   └── models/                  # Modelos entrenados (.joblib)
├── hardware/                    # Diseño de hardware
│   └── kicad/                   # Esquemáticos y PCB
├── docs/                        # Documentación adicional
└── README.md
```

---

## 🔧 Requisitos de Hardware

### Nodo Sensor (USD 103)

| Componente | Modelo | Precio |
|------------|--------|--------|
| Microcontrolador | Heltec WiFi LoRa 32 V3 | $35 |
| Temp/Hum Aire | DHT22 | $8 |
| Temp Suelo | DS18B20 (waterproof) | $5 |
| Humedad Suelo | HD-38 (capacitivo) | $4 |
| Luz | BH1750 | $5 |
| Presión | BMP280 | $6 |
| Batería | LiPo 3.7V 3100mAh | $12 |
| Panel Solar | 5V 0.75W | $8 |
| Gabinete | Sonoff IP65 | $20 |

### Gateway (USD 167)

| Componente | Modelo | Precio |
|------------|--------|--------|
| SBC | Raspberry Pi 4 (4GB) | $85 |
| Módulo LoRa | Waveshare SX1262 HAT | $45 |
| Almacenamiento | microSD 64GB | $15 |
| Fuente | 5V/3A USB-C | $10 |
| Gabinete | Case con ventilación | $12 |

**💵 Costo Total del Sistema: USD 270**

---

## 🚀 Instalación Rápida

### 1. Nodo Sensor

```bash
# Clonar repositorio
git clone https://github.com/crisje27/SMART-GROW-SISTEMA-IoT-LoRa-CON-MACHINE-LEARNING-PARA-AGRICULTURA-DE-PRECISI-N.git

# Abrir en Arduino IDE
# Seleccionar: Heltec WiFi LoRa 32 V3
# Instalar bibliotecas requeridas (ver firmware/README.md)
# Cargar firmware/nodo_sensor/nodo_sensor.ino
```

### 2. Gateway

```bash
# En Raspberry Pi con Raspberry Pi OS Lite (64-bit)

# Clonar repositorio
git clone https://github.com/crisje27/SMART-GROW-SISTEMA-IoT-LoRa-CON-MACHINE-LEARNING-PARA-AGRICULTURA-DE-PRECISI-N.git
cd SMART-GROW-*/gateway

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Iniciar servicios
cd docker
docker compose up -d

# Iniciar receptor LoRa
cd ../lora_receiver
pip install -r requirements.txt
python lora_receiver.py
```

---

## 📊 Métricas de Desempeño Verificadas

| Métrica | Valor |
|---------|-------|
| Tasa de éxito TX LoRa | 96% |
| Uptime del sistema | 99.5% |
| Latencia local | <10 ms |
| Latencia remota | <85 ms |
| Alcance urbano | 3.5 km |
| Alcance rural (estimado) | 8-12 km |
| Autonomía (con solar) | >500 días |

---

## 🤖 Modelos de Machine Learning

### Predicción de Heladas (XGBoost)
- **Accuracy:** 91%
- **Precision:** 87%
- **Recall:** 93%
- **Ventana de predicción:** 12-24 horas

### Predicción de Enfermedades (Random Forest)
- **Accuracy:** 99%
- **Precision:** 98%
- **Recall:** 99%

> ⚠️ **Nota:** Modelos entrenados con datos sintéticos. Requieren validación en campo real.

---

## 📱 Capturas de Pantalla

<p align="center">
  <img src="docs/images/dashboard-grafana.png" alt="Dashboard Grafana" width="45%">
  <img src="docs/images/pwa-mobile.png" alt="PWA Mobile" width="45%">
</p>

---

## 📚 Documentación

- [Guía de Instalación Completa](docs/instalacion.md)
- [Configuración del Gateway](docs/configuracion-gateway.md)
- [API Reference](docs/api-reference.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 🎓 Proyecto Final de Carrera

Este proyecto fue desarrollado como **Proyecto Final de Carrera** para la obtención del título de **Ingeniero Electrónico** en la **Universidad Tecnológica Nacional - Facultad Regional Tucumán (UTN-FRT)**.

**Autor:** Cristian Rodríguez  
**Director:** [Nombre del Director]  
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

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📧 Contacto

- **Email:** [tu-email@example.com]
- **LinkedIn:** [tu-linkedin]
- **GitHub:** [@crisje27](https://github.com/crisje27)

---

<p align="center">
  <b>Hecho con ❤️ en Tucumán, Argentina 🇦🇷</b>
</p>
