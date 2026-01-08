# 📟 Firmware del Nodo Sensor - SMART GROW

## Descripción

Firmware para el nodo sensor agrícola basado en Heltec WiFi LoRa 32 V3. Lee datos de 5 sensores ambientales y los transmite vía LoRa P2P a un gateway.

## Hardware Requerido

| Componente | Modelo | GPIO/Interfaz |
|------------|--------|---------------|
| Microcontrolador | Heltec WiFi LoRa 32 V3 | - |
| Temp/Hum Aire | DHT22 | GPIO42 |
| Temp Suelo | DS18B20 | GPIO1 (1-Wire) |
| Humedad Suelo | HD-38 | GPIO7 (ADC) |
| Luz | BH1750 | I2C (SDA=3, SCL=4) |
| Presión | BMP280 | I2C (0x76) |

## Instalación

### 1. Configurar Arduino IDE

1. Agregar URL de tarjetas ESP32 en Preferencias:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

2. Instalar tarjeta **"esp32 by Espressif Systems"** versión 2.0.11+

3. Seleccionar tarjeta: **"Heltec WiFi LoRa 32(V3) / Wireless shell(V3)"**

### 2. Instalar Bibliotecas

Desde el Gestor de Bibliotecas de Arduino IDE:

| Biblioteca | Versión | Autor |
|------------|---------|-------|
| RadioLib | 6.1.0+ | jgromes |
| DHT sensor library | 1.4.4+ | Adafruit |
| BH1750 | 1.3.0+ | Christopher Laws |
| OneWire | 2.3.7+ | Jim Studt |
| DallasTemperature | 3.9.0+ | Miles Burton |
| Adafruit BMP280 | 2.6.8+ | Adafruit |

### 3. Conexiones de Hardware

```
HELTEC V3 PINOUT:
═══════════════════════════════════════════════════
          J3 HEADER                    
    ┌─────────────────┐
    │ 1  GND          │ ← Tierra común
    │ 3  3.3V         │ ← Alimentación sensores
    │ 7  GPIO42       │ ← DHT22 DATA (pull-up 4.7K)
    │ 14 GPIO3 (SDA)  │ ← I2C Data (BH1750, BMP280)
    │ 15 GPIO4 (SCL)  │ ← I2C Clock
    │ 17 GPIO1        │ ← DS18B20 DATA (pull-up 4.7K)
    │ 18 GPIO7 (ADC)  │ ← HD-38 Analog Out
    └─────────────────┘
═══════════════════════════════════════════════════
```

### 4. Diagrama de Conexiones

```
                    ┌─────────────────────┐
                    │  HELTEC LORA V3     │
                    │                     │
    DHT22 ──────────┤ GPIO42              │
                    │                     │
    DS18B20 ────────┤ GPIO1               │
                    │                     │
    HD-38 ──────────┤ GPIO7 (ADC)         │
                    │                     │
    BH1750 ─────┬───┤ GPIO3 (SDA)         │
                │   │                     │
    BMP280 ─────┘   ┤ GPIO4 (SCL)         │
                    │                     │
                    │              ANTENA │───⟩⟩⟩ LoRa 915 MHz
                    │                     │
                    └─────────────────────┘
                           │
                    ┌──────┴──────┐
                    │   BATERÍA   │
                    │ 3.7V 3100mAh│
                    └─────────────┘
```

### 5. Configuración LoRa

El firmware está preconfigurado para Argentina (915 MHz). Si necesitas modificar:

```cpp
// En nodo_sensor.ino
#define LORA_FREQ       915.0   // MHz
#define LORA_SF         10      // Spreading Factor (7-12)
#define LORA_BW         125.0   // Bandwidth (kHz)
#define LORA_CR         5       // Coding Rate (5-8 = 4/5 a 4/8)
#define LORA_SYNC       0xF3    // Sync Word (debe coincidir con gateway)
#define LORA_POWER      22      // Potencia TX (dBm, max 22)
```

### 6. Modos de Operación

```cpp
// Para pruebas (5 segundos entre transmisiones)
#define CURRENT_INTERVAL    TX_INTERVAL_TEST    // 5000 ms

// Para producción (15 minutos entre transmisiones)
#define CURRENT_INTERVAL    TX_INTERVAL_PROD    // 900000 ms
```

## Estructura de Datos Transmitidos

```cpp
struct SensorData {
    float temperature;      // 4 bytes - Temperatura aire (°C)
    float humidity;         // 4 bytes - Humedad relativa (%)
    float soilHumidity;     // 4 bytes - Humedad suelo (%)
    float soilTemp;         // 4 bytes - Temperatura suelo (°C)
    float lux;              // 4 bytes - Luz (lux)
    float pressure;         // 4 bytes - Presión (hPa)
    uint16_t counter;       // 2 bytes - Contador paquetes
} __attribute__((packed)); // Total: 26 bytes
```

## Calibración del Sensor de Humedad del Suelo

1. **En aire seco:** Anota el valor ADC mostrado (típico: ~4095)
2. **En agua:** Sumerge el sensor y anota el valor (típico: ~1500)
3. **Actualiza las constantes:**

```cpp
#define SOIL_DRY_RAW    4095    // Tu valor en aire
#define SOIL_WET_RAW    1500    // Tu valor en agua
```

## Consumo de Energía

| Estado | Consumo |
|--------|---------|
| Deep Sleep | ~12 µA |
| Lectura sensores | ~38 mA |
| Transmisión LoRa | ~115 mA |
| **Promedio (TX c/15min)** | **~0.18 mA** |

Con batería 3100 mAh + panel solar 0.75W: **>500 días de autonomía**

## Troubleshooting

### DHT22 no responde
- Verificar pull-up de 4.7KΩ en DATA
- Aumentar delay después de `dht.begin()`

### BH1750/BMP280 no detectados
- Verificar conexiones I2C (SDA/SCL)
- Probar con scanner I2C para verificar direcciones

### Error en transmisión LoRa
- Verificar antena conectada
- Comprobar que frecuencia coincide con gateway

### Valores de humedad de suelo incorrectos
- Recalibrar constantes SOIL_DRY_RAW y SOIL_WET_RAW

## Licencia

MIT License - Ver [LICENSE](../../LICENSE)
