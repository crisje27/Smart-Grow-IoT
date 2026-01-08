/**
 * @file nodo_sensor.ino
 * @brief SMART GROW - Nodo Sensor Agrícola con LoRa P2P
 * @version 1.0.0
 * @date 2025-02-XX
 * @author Cristian Rodríguez
 * @license MIT
 * 
 * @description
 * Sistema de telemetría agrícola de bajo costo para monitoreo ambiental
 * y transmisión de datos vía LoRa P2P. Diseñado para pequeños y medianos
 * productores de la región NOA de Argentina.
 * 
 * HARDWARE:
 * - Placa: Heltec WiFi LoRa 32 V3 (ESP32-S3 + SX1262)
 * - Radio: SX1262 (915 MHz ISM Argentina)
 * 
 * SENSORES:
 * - DHT22:   Temperatura y humedad ambiente (GPIO42)
 * - DS18B20: Temperatura del suelo (GPIO1, 1-Wire)
 * - HD-38:   Humedad del suelo capacitiva (GPIO7, ADC)
 * - BH1750:  Intensidad lumínica (I2C: SDA=GPIO3, SCL=GPIO4)
 * - BMP280:  Presión barométrica (I2C: dirección 0x76)
 * 
 * CONFIGURACIÓN LORA:
 * - Frecuencia: 915 MHz
 * - Spreading Factor: 10
 * - Bandwidth: 125 kHz
 * - Coding Rate: 4/5
 * - Potencia TX: 22 dBm
 * - Sync Word: 0xF3
 * - Alcance: 3.5 km (urbano), 8-12 km (rural LOS)
 */

// ============================================================================
// BIBLIOTECAS
// ============================================================================
#include <RadioLib.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_BMP280.h>

// ============================================================================
// CONFIGURACIÓN DE PINES
// ============================================================================

// DHT22 - Temperatura y Humedad Ambiente
#define DHTPIN          42
#define DHTTYPE         DHT22
DHT dht(DHTPIN, DHTTYPE);

// DS18B20 - Temperatura del Suelo (1-Wire)
#define ONE_WIRE_BUS    1
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature soilTempSensor(&oneWire);

// HD-38 - Humedad del Suelo (Analógico)
#define SOIL_HUM_PIN    7
#define SOIL_DRY_RAW    4095    // Valor ADC en aire seco
#define SOIL_WET_RAW    1500    // Valor ADC en agua saturada

// BH1750 - Sensor de Luz (I2C)
#define SDA_PIN         3
#define SCL_PIN         4
BH1750 lightMeter;

// BMP280 - Presión Barométrica (I2C)
Adafruit_BMP280 bmp;

// ============================================================================
// CONFIGURACIÓN LORA SX1262
// ============================================================================
#define LORA_NSS        8
#define LORA_DIO1       14
#define LORA_NRST       12
#define LORA_BUSY       13

SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_NRST, LORA_BUSY);

// Parámetros LoRa
#define LORA_FREQ       915.0   // MHz (banda ISM Argentina)
#define LORA_SF         10      // Spreading Factor
#define LORA_BW         125.0   // kHz
#define LORA_CR         5       // Coding Rate 4/5
#define LORA_SYNC       0xF3    // Sync Word personalizada
#define LORA_POWER      22      // dBm (máximo para SX1262)

// ============================================================================
// CONFIGURACIÓN DE OPERACIÓN
// ============================================================================
#define TX_INTERVAL_TEST    5000    // 5 segundos (pruebas)
#define TX_INTERVAL_PROD    900000  // 15 minutos (producción)
#define CURRENT_INTERVAL    TX_INTERVAL_TEST  // Cambiar según modo

// ============================================================================
// ESTRUCTURA DE DATOS PARA TRANSMISIÓN
// Tamaño total: 26 bytes (empaquetado sin padding)
// ============================================================================
struct SensorData {
    float temperature;      // 4 bytes - Temp aire (°C)
    float humidity;         // 4 bytes - Humedad relativa (%)
    float soilHumidity;     // 4 bytes - Humedad suelo (%)
    float soilTemp;         // 4 bytes - Temp suelo (°C)
    float lux;              // 4 bytes - Luz (lux)
    float pressure;         // 4 bytes - Presión (hPa)
    uint16_t counter;       // 2 bytes - Contador de paquetes
} __attribute__((packed));

SensorData sensorData;
uint16_t packetCounter = 0;

// ============================================================================
// VARIABLES DE ESTADO
// ============================================================================
bool loraOK = false;
bool dht22OK = false;
bool bh1750OK = false;
bool ds18b20OK = false;
bool bmp280OK = false;

// ============================================================================
// SETUP - INICIALIZACIÓN DEL SISTEMA
// ============================================================================
void setup() {
    Serial.begin(115200);
    delay(2000);
    
    printHeader();
    
    // Inicializar I2C
    Wire.begin(SDA_PIN, SCL_PIN);
    delay(100);
    
    // Inicializar sensores
    initDHT22();
    initDS18B20();
    initBH1750();
    initBMP280();
    initSoilMoisture();
    initLoRa();
    
    printSummary();
    
    Serial.println("\n[SISTEMA] Iniciando operación...\n");
    delay(2000);
}

// ============================================================================
// LOOP - CICLO PRINCIPAL
// ============================================================================
void loop() {
    Serial.println("═══════════════════════════════════════════════");
    Serial.printf("[%lu] Nueva adquisición de datos\n", millis() / 1000);
    Serial.println("═══════════════════════════════════════════════");
    
    // Leer todos los sensores
    readSensors();
    
    // Mostrar datos
    printSensorData();
    
    // Transmitir por LoRa
    if (loraOK) {
        transmitData();
    }
    
    Serial.printf("\n[ESPERA] Próxima transmisión en %d segundos...\n\n", 
                  CURRENT_INTERVAL / 1000);
    
    delay(CURRENT_INTERVAL);
}

// ============================================================================
// FUNCIONES DE INICIALIZACIÓN
// ============================================================================

void printHeader() {
    Serial.println("\n╔═══════════════════════════════════════════════╗");
    Serial.println("║     SMART GROW - Nodo Sensor Agrícola         ║");
    Serial.println("║     Heltec WiFi LoRa 32 V3 + SX1262           ║");
    Serial.println("║     Versión 1.0.0 - UTN-FRT 2025              ║");
    Serial.println("╚═══════════════════════════════════════════════╝\n");
}

void initDHT22() {
    Serial.print("[INIT] DHT22.............. ");
    dht.begin();
    delay(2000);
    
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    
    if (!isnan(t) && !isnan(h)) {
        dht22OK = true;
        Serial.printf("OK (%.1f°C, %.1f%%)\n", t, h);
    } else {
        Serial.println("ERROR");
    }
}

void initDS18B20() {
    Serial.print("[INIT] DS18B20............ ");
    soilTempSensor.begin();
    
    if (soilTempSensor.getDeviceCount() > 0) {
        ds18b20OK = true;
        soilTempSensor.requestTemperatures();
        float t = soilTempSensor.getTempCByIndex(0);
        Serial.printf("OK (%.1f°C)\n", t);
    } else {
        Serial.println("NO DETECTADO");
    }
}

void initBH1750() {
    Serial.print("[INIT] BH1750............. ");
    
    if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
        bh1750OK = true;
        delay(200);
        float lux = lightMeter.readLightLevel();
        Serial.printf("OK (%.0f lux)\n", lux);
    } else {
        Serial.println("ERROR");
    }
}

void initBMP280() {
    Serial.print("[INIT] BMP280............. ");
    
    if (bmp.begin(0x76)) {
        bmp280OK = true;
        bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                        Adafruit_BMP280::SAMPLING_X2,
                        Adafruit_BMP280::SAMPLING_X16,
                        Adafruit_BMP280::FILTER_X16,
                        Adafruit_BMP280::STANDBY_MS_500);
        float p = bmp.readPressure() / 100.0F;
        Serial.printf("OK (%.1f hPa)\n", p);
    } else {
        Serial.println("ERROR");
    }
}

void initSoilMoisture() {
    Serial.print("[INIT] HD-38 (Suelo)...... ");
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);
    delay(100);
    
    int raw = analogRead(SOIL_HUM_PIN);
    Serial.printf("OK (ADC: %d)\n", raw);
}

void initLoRa() {
    Serial.print("[INIT] LoRa SX1262........ ");
    
    SPI.begin(9, 11, 10, 8);
    
    int state = radio.begin(LORA_FREQ);
    
    if (state == RADIOLIB_ERR_NONE) {
        radio.setSpreadingFactor(LORA_SF);
        radio.setBandwidth(LORA_BW);
        radio.setCodingRate(LORA_CR);
        radio.setSyncWord(LORA_SYNC);
        radio.setOutputPower(LORA_POWER);
        radio.setCurrentLimit(140);
        
        loraOK = true;
        Serial.println("OK");
        Serial.printf("       Frecuencia: %.1f MHz | SF%d | BW%.0f kHz | %d dBm\n",
                      LORA_FREQ, LORA_SF, LORA_BW, LORA_POWER);
    } else {
        Serial.printf("ERROR (código: %d)\n", state);
    }
}

void printSummary() {
    Serial.println("\n┌───────────────────────────────────────────────┐");
    Serial.println("│           RESUMEN DE INICIALIZACIÓN           │");
    Serial.println("├───────────────────────────────────────────────┤");
    Serial.printf("│  DHT22 (Temp/Hum Aire):    %s              │\n", dht22OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  DS18B20 (Temp Suelo):     %s              │\n", ds18b20OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  BH1750 (Luz):             %s              │\n", bh1750OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  BMP280 (Presión):         %s              │\n", bmp280OK ? "✓ OK" : "✗ NO");
    Serial.println("│  HD-38 (Hum Suelo):        ✓ OK              │");
    Serial.printf("│  LoRa SX1262:              %s              │\n", loraOK ? "✓ OK" : "✗ NO");
    Serial.println("└───────────────────────────────────────────────┘");
}

// ============================================================================
// FUNCIONES DE LECTURA DE SENSORES
// ============================================================================

void readSensors() {
    // DHT22: Temperatura y Humedad Ambiente
    if (dht22OK) {
        sensorData.temperature = dht.readTemperature();
        sensorData.humidity = dht.readHumidity();
        if (isnan(sensorData.temperature)) sensorData.temperature = 0.0;
        if (isnan(sensorData.humidity)) sensorData.humidity = 0.0;
    } else {
        sensorData.temperature = 0.0;
        sensorData.humidity = 0.0;
    }
    
    // DS18B20: Temperatura del Suelo
    if (ds18b20OK) {
        soilTempSensor.requestTemperatures();
        sensorData.soilTemp = soilTempSensor.getTempCByIndex(0);
        if (sensorData.soilTemp == DEVICE_DISCONNECTED_C) {
            sensorData.soilTemp = 0.0;
        }
    } else {
        sensorData.soilTemp = 0.0;
    }
    
    // BH1750: Intensidad de Luz
    if (bh1750OK) {
        sensorData.lux = lightMeter.readLightLevel();
        if (sensorData.lux < 0) sensorData.lux = 0.0;
    } else {
        sensorData.lux = 0.0;
    }
    
    // BMP280: Presión Barométrica
    if (bmp280OK) {
        sensorData.pressure = bmp.readPressure() / 100.0F;
    } else {
        sensorData.pressure = 0.0;
    }
    
    // HD-38: Humedad del Suelo
    int soilRaw = analogRead(SOIL_HUM_PIN);
    sensorData.soilHumidity = map(soilRaw, SOIL_DRY_RAW, SOIL_WET_RAW, 0, 100);
    sensorData.soilHumidity = constrain(sensorData.soilHumidity, 0, 100);
    
    // Contador de paquetes
    sensorData.counter = packetCounter++;
}

void printSensorData() {
    Serial.println("\n📊 DATOS DE SENSORES:");
    Serial.println("┌───────────────────────────────────────────────┐");
    Serial.printf("│  Temperatura Aire:    %6.1f °C              │\n", sensorData.temperature);
    Serial.printf("│  Humedad Relativa:    %6.1f %%               │\n", sensorData.humidity);
    Serial.printf("│  Temperatura Suelo:   %6.1f °C              │\n", sensorData.soilTemp);
    Serial.printf("│  Humedad Suelo:       %6.1f %%               │\n", sensorData.soilHumidity);
    Serial.printf("│  Intensidad Luz:      %6.0f lux             │\n", sensorData.lux);
    Serial.printf("│  Presión Atmosférica: %6.1f hPa             │\n", sensorData.pressure);
    Serial.printf("│  Paquete #:           %6u                 │\n", sensorData.counter);
    Serial.println("└───────────────────────────────────────────────┘");
    
    // Alertas
    if (sensorData.soilHumidity < 30) {
        Serial.println("⚠️  ALERTA: Suelo seco - considerar riego");
    }
    if (sensorData.temperature > 35) {
        Serial.println("⚠️  ALERTA: Temperatura elevada");
    }
    if (sensorData.temperature < 5 && sensorData.temperature > 0) {
        Serial.println("❄️  ALERTA: Riesgo de helada");
    }
}

// ============================================================================
// FUNCIÓN DE TRANSMISIÓN LORA
// ============================================================================

void transmitData() {
    Serial.print("\n📡 Transmitiendo por LoRa... ");
    
    int state = radio.transmit((uint8_t*)&sensorData, sizeof(SensorData));
    
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println("✓ OK");
        Serial.printf("   Payload: %d bytes | Paquete #%u\n", 
                      sizeof(SensorData), sensorData.counter);
    } else {
        Serial.printf("✗ ERROR (código: %d)\n", state);
    }
}
