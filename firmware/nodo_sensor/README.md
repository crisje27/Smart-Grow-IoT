# 📟 Firmware Nodo Sensor - SMART GROW

## Descripción

Firmware completo para el nodo sensor agrícola basado en **Heltec WiFi LoRa 32 V3**. Captura datos de 5 sensores ambientales y los transmite vía LoRa P2P al gateway.

---

## 🔧 Hardware Requerido

| Componente | Modelo | Cantidad | Precio USD |
|------------|--------|----------|------------|
| Microcontrolador | Heltec WiFi LoRa 32 V3 | 1 | $35 |
| Sensor Temp/Hum | DHT22 | 1 | $8 |
| Sensor Temp Suelo | DS18B20 Waterproof | 1 | $5 |
| Sensor Hum Suelo | HD-38 Capacitivo | 1 | $4 |
| Sensor Luz | BH1750 | 1 | $5 |
| Sensor Presión | BMP280 | 1 | $6 |
| Batería | LiPo 3.7V 3100mAh | 1 | $12 |
| Panel Solar | 5V 0.75W | 1 | $8 |
| Gabinete | Sonoff IP65 | 1 | $20 |
| Resistencias | 4.7KΩ (pull-up) | 2 | $0.50 |
| **TOTAL** | | | **$103.50** |

---

## 📌 Diagrama de Conexiones

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HELTEC WIFI LORA 32 V3                               │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         PINOUT J3 HEADER                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Pin 1  (GND)  ─────── GND común todos los sensores                       │
│   Pin 3  (3.3V) ─────── VCC todos los sensores                             │
│   Pin 7  (GPIO42) ───── DHT22 DATA + Resistencia 4.7KΩ a 3.3V             │
│   Pin 14 (GPIO3)  ───── I2C SDA (BH1750 + BMP280)                          │
│   Pin 15 (GPIO4)  ───── I2C SCL (BH1750 + BMP280)                          │
│   Pin 17 (GPIO1)  ───── DS18B20 DATA + Resistencia 4.7KΩ a 3.3V           │
│   Pin 18 (GPIO7)  ───── HD-38 AOUT (señal analógica)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           ESQUEMA DE CONEXIONES                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              HELTEC V3
                         ┌───────────────┐
                         │               │
    DHT22 ──────────────►│ GPIO42       │
         DATA ◄──┬──────►│              │
                 │       │               │
                4.7KΩ    │               │
                 │       │               │
                3.3V     │               │
                         │               │
    DS18B20 ────────────►│ GPIO1        │
         DATA ◄──┬──────►│              │
                 │       │               │
                4.7KΩ    │               │
                 │       │               │
                3.3V     │               │
                         │               │
    HD-38 ──────────────►│ GPIO7 (ADC)  │
         AOUT ──────────►│              │
                         │               │
    BH1750 ─────────────►│ GPIO3 (SDA)  │◄──── BMP280
         SDA ───────────►│              │◄──── SDA
         SCL ───────────►│ GPIO4 (SCL)  │◄──── SCL
                         │               │
                         │         ANTENA│───⟩⟩⟩ LoRa 915 MHz
                         │               │
                         └───────────────┘
                                │
                         ┌──────┴──────┐
                         │   BATERÍA   │
                         │ LiPo 3.7V   │◄──── Panel Solar 5V
                         │  3100mAh    │
                         └─────────────┘
```

---

## 💻 Instalación del Firmware

### 1. Configurar Arduino IDE

1. **Agregar URL de tarjetas ESP32:**
   - Ir a `Archivo → Preferencias`
   - En "URLs adicionales de gestor de tarjetas", agregar:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

2. **Instalar tarjeta ESP32:**
   - Ir a `Herramientas → Placa → Gestor de tarjetas`
   - Buscar "esp32" e instalar **"esp32 by Espressif Systems"** (v2.0.11+)

3. **Seleccionar tarjeta:**
   - `Herramientas → Placa → esp32 → Heltec WiFi LoRa 32(V3) / Wireless shell(V3)`

### 2. Instalar Bibliotecas

Desde `Herramientas → Administrar bibliotecas`, instalar:

| Biblioteca | Versión | Autor |
|------------|---------|-------|
| RadioLib | 6.1.0+ | jgromes |
| DHT sensor library | 1.4.4+ | Adafruit |
| Adafruit Unified Sensor | 1.1.9+ | Adafruit |
| BH1750 | 1.3.0+ | Christopher Laws |
| OneWire | 2.3.7+ | Jim Studt |
| DallasTemperature | 3.9.0+ | Miles Burton |
| Adafruit BMP280 Library | 2.6.8+ | Adafruit |

### 3. Cargar Firmware

1. Conectar Heltec V3 por USB
2. Seleccionar puerto COM correcto
3. Abrir `nodo_sensor.ino`
4. Clic en **Subir** (→)

### 4. Verificar Funcionamiento

Abrir **Monitor Serial** a 115200 baud. Deberías ver:

```
╔═══════════════════════════════════════════════════════════╗
║           SMART GROW - Nodo Sensor Agrícola               ║
╚═══════════════════════════════════════════════════════════╝

[1/5] DHT22 (Temp/Hum Aire)........ ✓ OK (22.5°C, 65.0%)
[2/5] DS18B20 (Temp Suelo)......... ✓ OK (1 sensor, 18.5°C)
[3/5] BH1750 (Luz)................. ✓ OK (12500 lux)
[4/5] BMP280 (Presión)............. ✓ OK (1013.2 hPa)
[5/5] HD-38 (Hum Suelo)............ ✓ OK (ADC: 2500)

[LORA] Inicializando radio........ ✓ OK
```

---

## ⚙️ Configuración

### Cambiar Modo de Operación

En `nodo_sensor.ino`, línea ~70:

```cpp
// Modo pruebas (5 segundos)
#define TX_INTERVAL         TX_INTERVAL_TEST

// Modo producción (15 minutos) - DESCOMENTAR PARA PRODUCCIÓN
// #define TX_INTERVAL         TX_INTERVAL_PROD
```

### Calibrar Sensor de Humedad de Suelo

1. **Medir valor en aire seco:**
   ```
   Colocar sensor en aire → Anotar valor ADC (ej: 4095)
   ```

2. **Medir valor en agua:**
   ```
   Sumergir sensor en agua → Anotar valor ADC (ej: 1500)
   ```

3. **Actualizar constantes (línea ~60):**
   ```cpp
   #define SOIL_DRY_RAW        4095    // Tu valor en aire
   #define SOIL_WET_RAW        1500    // Tu valor en agua
   ```

### Cambiar Parámetros LoRa

> ⚠️ **IMPORTANTE:** Los parámetros deben coincidir con el gateway

```cpp
#define LORA_FREQUENCY      915.0   // MHz (Argentina: 915, Europa: 868)
#define LORA_BANDWIDTH      125.0   // kHz (125, 250, 500)
#define LORA_SF             10      // Spreading Factor (7-12)
#define LORA_CR             5       // Coding Rate (5=4/5 ... 8=4/8)
#define LORA_SYNC_WORD      0xF3    // Debe coincidir con gateway
#define LORA_TX_POWER       22      // dBm (máximo 22)
```

---

## 📊 Estructura de Datos Transmitidos

```cpp
struct SensorData {           // Total: 26 bytes
    float temperature;        // 4 bytes - Temp aire (°C)
    float humidity;           // 4 bytes - Humedad relativa (%)
    float soilHumidity;       // 4 bytes - Humedad suelo (%)
    float soilTemp;           // 4 bytes - Temp suelo (°C)
    float lux;                // 4 bytes - Luz (lux)
    float pressure;           // 4 bytes - Presión (hPa)
    uint16_t counter;         // 2 bytes - Contador paquetes
};
```

---

## 🔋 Consumo de Energía

| Estado | Duración | Corriente | Energía |
|--------|----------|-----------|---------|
| Deep Sleep | 14 min 56 s | 12 µA | 0.18 mWh |
| Lectura sensores | 2.5 s | 38 mA | 0.026 mWh |
| TX LoRa | 370 ms | 115 mA | 0.012 mWh |
| **Promedio por ciclo** | 15 min | **0.18 mA** | **0.22 mWh** |

### Autonomía Estimada

- **Sin solar:** ~720 días (batería 3100mAh)
- **Con solar 0.75W:** >500 días (considerando días nublados)

---

## 🔧 Solución de Problemas

### DHT22 no responde
- Verificar resistencia pull-up 4.7KΩ entre DATA y 3.3V
- Aumentar delay después de `dht.begin()` a 3000ms
- Verificar conexión en GPIO42

### DS18B20 no detectado
- Verificar resistencia pull-up 4.7KΩ
- Verificar conexión en GPIO1
- Probar con otro sensor (pueden fallar)

### BH1750 / BMP280 no detectados
- Verificar conexiones I2C (SDA:3, SCL:4)
- Ejecutar scanner I2C para verificar direcciones
- BH1750 debe estar en 0x23, BMP280 en 0x76

### Error en transmisión LoRa
- **Verificar antena conectada** (crítico, puede dañar el módulo)
- Verificar que frecuencia y sync word coincidan con gateway
- Reducir potencia TX si hay interferencia

### Valores de humedad incorrectos
- Recalibrar constantes `SOIL_DRY_RAW` y `SOIL_WET_RAW`
- Limpiar sensor de residuos
- Verificar que el sensor capacitivo no esté sumergido completamente

---

## 📝 Notas Adicionales

- El código está preparado para deep sleep pero no implementado (requiere modificaciones de hardware para despertar el módulo LoRa)
- Para producción, cambiar `TX_INTERVAL` a 15 minutos
- Los valores de calibración de humedad de suelo varían según el tipo de suelo

---

## 📄 Licencia

MIT License - Ver [LICENSE](../../LICENSE)
