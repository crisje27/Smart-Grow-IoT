/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║                         SMART GROW - Nodo Sensor                          ║
 * ║              Sistema IoT LoRa para Agricultura de Precisión               ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * @file    nodo_sensor.ino
 * @brief   Firmware completo para nodo sensor agrícola con 5 sensores
 * @version 1.0.0
 * @date    2025-02-XX
 * @author  Cristian Rodríguez - UTN FRT
 * @license MIT
 * 
 * ┌─────────────────────────────────────────────────────────────────────────────┐
 * │ HARDWARE                                                                    │
 * ├─────────────────────────────────────────────────────────────────────────────┤
 * │ • Placa: Heltec WiFi LoRa 32 V3 (ESP32-S3 + SX1262)                        │
 * │ • Radio: SX1262 @ 915 MHz (ISM Argentina)                                  │
 * │ • Alimentación: LiPo 3.7V 3100mAh + Panel Solar 5V 0.75W                   │
 * └─────────────────────────────────────────────────────────────────────────────┘
 * 
 * ┌─────────────────────────────────────────────────────────────────────────────┐
 * │ SENSORES                                                                    │
 * ├──────────────┬─────────────────────┬────────────┬──────────────────────────┤
 * │ Sensor       │ Variable            │ Interfaz   │ Conexión                 │
 * ├──────────────┼─────────────────────┼────────────┼──────────────────────────┤
 * │ DHT22        │ Temp/Hum aire       │ Digital    │ GPIO 42 + Pull-up 4.7KΩ  │
 * │ DS18B20      │ Temp suelo          │ 1-Wire     │ GPIO 1 + Pull-up 4.7KΩ   │
 * │ HD-38        │ Humedad suelo       │ ADC        │ GPIO 7 (ADC1_CH6)        │
 * │ BH1750       │ Luz                 │ I2C        │ SDA:3, SCL:4 (0x23)      │
 * │ BMP280       │ Presión barométrica │ I2C        │ SDA:3, SCL:4 (0x76)      │
 * └──────────────┴─────────────────────┴────────────┴──────────────────────────┘
 * 
 * ┌─────────────────────────────────────────────────────────────────────────────┐
 * │ CONFIGURACIÓN LORA                                                          │
 * ├─────────────────────────────────────────────────────────────────────────────┤
 * │ • Frecuencia: 915.0 MHz        • Spreading Factor: 10                      │
 * │ • Bandwidth: 125 kHz           • Coding Rate: 4/5                          │
 * │ • Sync Word: 0xF3              • Potencia TX: 22 dBm                       │
 * │ • Alcance estimado: 3.5 km (urbano) / 8-12 km (rural LOS)                  │
 * └─────────────────────────────────────────────────────────────────────────────┘
 */

// ═══════════════════════════════════════════════════════════════════════════════
// BIBLIOTECAS
// ═══════════════════════════════════════════════════════════════════════════════
#include <RadioLib.h>           // Comunicación LoRa SX1262
#include <DHT.h>                // Sensor DHT22
#include <Wire.h>               // Bus I2C
#include <BH1750.h>             // Sensor de luz
#include <OneWire.h>            // Protocolo 1-Wire
#include <DallasTemperature.h>  // Sensor DS18B20
#include <Adafruit_BMP280.h>    // Sensor de presión

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN DE PINES - SENSORES
// ═══════════════════════════════════════════════════════════════════════════════

// DHT22 - Temperatura y Humedad del Aire
#define DHTPIN              42      // GPIO42 (J3 pin 7)
#define DHTTYPE             DHT22

// DS18B20 - Temperatura del Suelo (1-Wire)
#define DS18B20_PIN         1       // GPIO1 (J3 pin 17) - Requiere pull-up 4.7KΩ

// HD-38 - Humedad del Suelo (Capacitivo, Analógico)
#define SOIL_HUMIDITY_PIN   7       // GPIO7 (ADC1_CH6, J3 pin 18)

// I2C - Bus compartido para BH1750 y BMP280
#define I2C_SDA             3       // GPIO3 (J3 pin 14)
#define I2C_SCL             4       // GPIO4 (J3 pin 15)

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN DE PINES - LORA SX1262 (Internos Heltec V3, no modificar)
// ═══════════════════════════════════════════════════════════════════════════════
#define LORA_NSS            8       // Chip Select
#define LORA_DIO1           14      // DIO1 Interrupt
#define LORA_NRST           12      // Reset
#define LORA_BUSY           13      // Busy indicator

// ═══════════════════════════════════════════════════════════════════════════════
// PARÁMETROS LORA
// ═══════════════════════════════════════════════════════════════════════════════
#define LORA_FREQUENCY      915.0   // MHz (ISM Argentina/América)
#define LORA_BANDWIDTH      125.0   // kHz
#define LORA_SF             10      // Spreading Factor (7-12)
#define LORA_CR             5       // Coding Rate (5=4/5, 6=4/6, 7=4/7, 8=4/8)
#define LORA_SYNC_WORD      0xF3    // Sync Word (debe coincidir con gateway)
#define LORA_TX_POWER       22      // dBm (máximo para SX1262)
#define LORA_CURRENT_LIMIT  140     // mA

// ═══════════════════════════════════════════════════════════════════════════════
// PARÁMETROS DE OPERACIÓN
// ═══════════════════════════════════════════════════════════════════════════════
#define TX_INTERVAL_TEST    5000    // 5 segundos (modo pruebas)
#define TX_INTERVAL_PROD    900000  // 15 minutos (modo producción)

// *** SELECCIONAR MODO DE OPERACIÓN ***
#define TX_INTERVAL         TX_INTERVAL_TEST  // Cambiar a TX_INTERVAL_PROD para producción

// ═══════════════════════════════════════════════════════════════════════════════
// CALIBRACIÓN SENSOR HUMEDAD DE SUELO
// Ajustar estos valores según calibración real del sensor HD-38
// ═══════════════════════════════════════════════════════════════════════════════
#define SOIL_DRY_RAW        4095    // Valor ADC cuando el sensor está en aire seco
#define SOIL_WET_RAW        1500    // Valor ADC cuando el sensor está en agua saturada

// ═══════════════════════════════════════════════════════════════════════════════
// INSTANCIAS DE OBJETOS
// ═══════════════════════════════════════════════════════════════════════════════

// Radio LoRa
SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_NRST, LORA_BUSY);

// Sensores
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(DS18B20_PIN);
DallasTemperature ds18b20(&oneWire);
BH1750 bh1750;
Adafruit_BMP280 bmp280;

// ═══════════════════════════════════════════════════════════════════════════════
// ESTRUCTURA DE DATOS PARA TRANSMISIÓN
// Tamaño: 26 bytes (empaquetado sin padding)
// ═══════════════════════════════════════════════════════════════════════════════
struct __attribute__((packed)) SensorData {
    float temperature;      // 4 bytes - Temperatura aire (°C)
    float humidity;         // 4 bytes - Humedad relativa aire (%)
    float soilHumidity;     // 4 bytes - Humedad suelo (%)
    float soilTemp;         // 4 bytes - Temperatura suelo (°C)
    float lux;              // 4 bytes - Intensidad lumínica (lux)
    float pressure;         // 4 bytes - Presión barométrica (hPa)
    uint16_t counter;       // 2 bytes - Contador de paquetes
};                          // Total: 26 bytes

SensorData sensorData;
uint16_t packetCounter = 0;

// ═══════════════════════════════════════════════════════════════════════════════
// VARIABLES DE ESTADO
// ═══════════════════════════════════════════════════════════════════════════════
bool loraOK     = false;
bool dht22OK    = false;
bool ds18b20OK  = false;
bool bh1750OK   = false;
bool bmp280OK   = false;

// Estadísticas de transmisión
uint32_t txSuccess = 0;
uint32_t txFailed  = 0;

// ═══════════════════════════════════════════════════════════════════════════════
// PROTOTIPOS DE FUNCIONES
// ═══════════════════════════════════════════════════════════════════════════════
void printHeader();
void initSensors();
void initLoRa();
void printSystemStatus();
void readAllSensors();
void printSensorData();
void checkAlerts();
void transmitData();

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP - INICIALIZACIÓN DEL SISTEMA
// ═══════════════════════════════════════════════════════════════════════════════
void setup() {
    // Inicializar Serial
    Serial.begin(115200);
    delay(2000);  // Esperar estabilización
    
    printHeader();
    
    // Inicializar bus I2C con pines personalizados
    Wire.begin(I2C_SDA, I2C_SCL);
    delay(100);
    
    // Inicializar todos los sensores
    initSensors();
    
    // Inicializar comunicación LoRa
    initLoRa();
    
    // Mostrar resumen del sistema
    printSystemStatus();
    
    Serial.println("\n[SISTEMA] Iniciando ciclo de operación...");
    Serial.printf("[SISTEMA] Intervalo de transmisión: %d ms\n\n", TX_INTERVAL);
    
    delay(2000);
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOOP - CICLO PRINCIPAL
// ═══════════════════════════════════════════════════════════════════════════════
void loop() {
    Serial.println("\n════════════════════════════════════════════════════════════");
    Serial.printf("  CICLO #%u - %s\n", packetCounter + 1, 
                  loraOK ? "Sistema Operativo" : "LoRa NO disponible");
    Serial.println("════════════════════════════════════════════════════════════");
    
    // 1. Leer todos los sensores
    readAllSensors();
    
    // 2. Mostrar datos en consola
    printSensorData();
    
    // 3. Verificar alertas
    checkAlerts();
    
    // 4. Transmitir por LoRa
    if (loraOK) {
        transmitData();
    } else {
        Serial.println("\n⚠️  [LORA] Radio no disponible, omitiendo transmisión");
    }
    
    // 5. Mostrar estadísticas
    Serial.printf("\n📊 Estadísticas: TX OK=%lu | TX FAIL=%lu | Tasa=%.1f%%\n",
                  txSuccess, txFailed,
                  txSuccess + txFailed > 0 ? 
                  (float)txSuccess / (txSuccess + txFailed) * 100 : 0);
    
    // 6. Esperar siguiente ciclo
    Serial.printf("\n⏱️  Próxima lectura en %d segundos...\n", TX_INTERVAL / 1000);
    
    delay(TX_INTERVAL);
}

// ═══════════════════════════════════════════════════════════════════════════════
// FUNCIONES DE INICIALIZACIÓN
// ═══════════════════════════════════════════════════════════════════════════════

void printHeader() {
    Serial.println("\n");
    Serial.println("╔═══════════════════════════════════════════════════════════╗");
    Serial.println("║           SMART GROW - Nodo Sensor Agrícola               ║");
    Serial.println("║                                                           ║");
    Serial.println("║  Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + SX1262)    ║");
    Serial.println("║  Versión:  1.0.0                                          ║");
    Serial.println("║  Autor:    Cristian Rodríguez - UTN FRT                   ║");
    Serial.println("╚═══════════════════════════════════════════════════════════╝");
    Serial.println();
}

void initSensors() {
    Serial.println("┌─────────────────────────────────────────────────────────────┐");
    Serial.println("│              INICIALIZACIÓN DE SENSORES                     │");
    Serial.println("└─────────────────────────────────────────────────────────────┘");
    
    // ─────────────────────────────────────────────────────────────────────────
    // DHT22 - Temperatura y Humedad del Aire
    // ─────────────────────────────────────────────────────────────────────────
    Serial.print("[1/5] DHT22 (Temp/Hum Aire)........ ");
    dht.begin();
    delay(2000);  // DHT22 necesita tiempo para estabilizarse
    
    float testTemp = dht.readTemperature();
    float testHum = dht.readHumidity();
    
    if (!isnan(testTemp) && !isnan(testHum)) {
        dht22OK = true;
        Serial.printf("✓ OK (%.1f°C, %.1f%%)\n", testTemp, testHum);
    } else {
        Serial.println("✗ ERROR - Verificar conexión GPIO42");
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // DS18B20 - Temperatura del Suelo
    // ─────────────────────────────────────────────────────────────────────────
    Serial.print("[2/5] DS18B20 (Temp Suelo)......... ");
    ds18b20.begin();
    delay(100);
    
    int deviceCount = ds18b20.getDeviceCount();
    if (deviceCount > 0) {
        ds18b20OK = true;
        ds18b20.requestTemperatures();
        float soilT = ds18b20.getTempCByIndex(0);
        Serial.printf("✓ OK (%d sensor, %.1f°C)\n", deviceCount, soilT);
    } else {
        Serial.println("✗ NO DETECTADO - Verificar GPIO1 + pull-up");
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // BH1750 - Intensidad Lumínica
    // ─────────────────────────────────────────────────────────────────────────
    Serial.print("[3/5] BH1750 (Luz)................. ");
    
    if (bh1750.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
        bh1750OK = true;
        delay(200);
        float testLux = bh1750.readLightLevel();
        Serial.printf("✓ OK (%.0f lux)\n", testLux);
    } else {
        Serial.println("✗ ERROR - Verificar I2C (SDA:3, SCL:4)");
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // BMP280 - Presión Barométrica
    // ─────────────────────────────────────────────────────────────────────────
    Serial.print("[4/5] BMP280 (Presión)............. ");
    
    if (bmp280.begin(0x76)) {  // Dirección I2C por defecto
        bmp280OK = true;
        
        // Configurar oversampling y filtro
        bmp280.setSampling(
            Adafruit_BMP280::MODE_NORMAL,
            Adafruit_BMP280::SAMPLING_X2,     // Temperatura
            Adafruit_BMP280::SAMPLING_X16,    // Presión
            Adafruit_BMP280::FILTER_X16,
            Adafruit_BMP280::STANDBY_MS_500
        );
        
        float testPressure = bmp280.readPressure() / 100.0F;
        Serial.printf("✓ OK (%.1f hPa)\n", testPressure);
    } else {
        Serial.println("✗ ERROR - Verificar I2C dirección 0x76");
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // HD-38 - Humedad del Suelo (ADC)
    // ─────────────────────────────────────────────────────────────────────────
    Serial.print("[5/5] HD-38 (Hum Suelo)............ ");
    
    // Configurar ADC
    analogReadResolution(12);         // 12 bits (0-4095)
    analogSetAttenuation(ADC_11db);   // Rango completo 0-3.3V
    delay(100);
    
    int testADC = analogRead(SOIL_HUMIDITY_PIN);
    Serial.printf("✓ OK (ADC: %d)\n", testADC);
    
    Serial.println();
}

void initLoRa() {
    Serial.println("┌─────────────────────────────────────────────────────────────┐");
    Serial.println("│               INICIALIZACIÓN LORA SX1262                    │");
    Serial.println("└─────────────────────────────────────────────────────────────┘");
    
    // Inicializar SPI para el módulo LoRa
    SPI.begin(9, 11, 10, 8);  // SCK, MISO, MOSI, SS
    
    Serial.print("[LORA] Inicializando radio........ ");
    
    int state = radio.begin(LORA_FREQUENCY);
    
    if (state == RADIOLIB_ERR_NONE) {
        // Configurar parámetros LoRa
        radio.setSpreadingFactor(LORA_SF);
        radio.setBandwidth(LORA_BANDWIDTH);
        radio.setCodingRate(LORA_CR);
        radio.setSyncWord(LORA_SYNC_WORD);
        radio.setOutputPower(LORA_TX_POWER);
        radio.setCurrentLimit(LORA_CURRENT_LIMIT);
        
        loraOK = true;
        Serial.println("✓ OK");
        
        Serial.println("\n[LORA] Configuración:");
        Serial.printf("       • Frecuencia:      %.1f MHz\n", LORA_FREQUENCY);
        Serial.printf("       • Spreading Factor: SF%d\n", LORA_SF);
        Serial.printf("       • Bandwidth:        %.0f kHz\n", LORA_BANDWIDTH);
        Serial.printf("       • Coding Rate:      4/%d\n", LORA_CR);
        Serial.printf("       • Sync Word:        0x%02X\n", LORA_SYNC_WORD);
        Serial.printf("       • Potencia TX:      %d dBm\n", LORA_TX_POWER);
        Serial.printf("       • Alcance estimado: 3.5-12 km\n");
    } else {
        Serial.printf("✗ ERROR (código: %d)\n", state);
        Serial.println("       Verificar conexiones del módulo LoRa");
    }
    
    Serial.println();
}

void printSystemStatus() {
    Serial.println("┌─────────────────────────────────────────────────────────────┐");
    Serial.println("│                   RESUMEN DEL SISTEMA                       │");
    Serial.println("├─────────────────────────────────────────────────────────────┤");
    Serial.printf("│  DHT22 (Temp/Hum Aire):     %s                           │\n", 
                  dht22OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  DS18B20 (Temp Suelo):      %s                           │\n", 
                  ds18b20OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  BH1750 (Luz):              %s                           │\n", 
                  bh1750OK ? "✓ OK" : "✗ NO");
    Serial.printf("│  BMP280 (Presión):          %s                           │\n", 
                  bmp280OK ? "✓ OK" : "✗ NO");
    Serial.println("│  HD-38 (Hum Suelo):         ✓ OK                           │");
    Serial.printf("│  LoRa SX1262:               %s                           │\n", 
                  loraOK ? "✓ OK" : "✗ NO");
    Serial.println("├─────────────────────────────────────────────────────────────┤");
    
    int sensorsOK = (dht22OK ? 1 : 0) + (ds18b20OK ? 1 : 0) + 
                    (bh1750OK ? 1 : 0) + (bmp280OK ? 1 : 0) + 1;  // HD-38 siempre OK
    
    Serial.printf("│  Sensores activos: %d/5      LoRa: %s                   │\n",
                  sensorsOK, loraOK ? "LISTO" : "ERROR");
    Serial.println("└─────────────────────────────────────────────────────────────┘");
}

// ═══════════════════════════════════════════════════════════════════════════════
// FUNCIONES DE LECTURA
// ═══════════════════════════════════════════════════════════════════════════════

void readAllSensors() {
    // ─────────────────────────────────────────────────────────────────────────
    // DHT22 - Temperatura y Humedad del Aire
    // ─────────────────────────────────────────────────────────────────────────
    if (dht22OK) {
        sensorData.temperature = dht.readTemperature();
        sensorData.humidity = dht.readHumidity();
        
        // Validar lecturas
        if (isnan(sensorData.temperature)) {
            sensorData.temperature = 0.0;
            Serial.println("⚠️  [DHT22] Error en lectura de temperatura");
        }
        if (isnan(sensorData.humidity)) {
            sensorData.humidity = 0.0;
            Serial.println("⚠️  [DHT22] Error en lectura de humedad");
        }
    } else {
        sensorData.temperature = 0.0;
        sensorData.humidity = 0.0;
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // DS18B20 - Temperatura del Suelo
    // ─────────────────────────────────────────────────────────────────────────
    if (ds18b20OK) {
        ds18b20.requestTemperatures();
        sensorData.soilTemp = ds18b20.getTempCByIndex(0);
        
        // Validar (DEVICE_DISCONNECTED_C = -127)
        if (sensorData.soilTemp == DEVICE_DISCONNECTED_C) {
            sensorData.soilTemp = 0.0;
            Serial.println("⚠️  [DS18B20] Sensor desconectado");
        }
    } else {
        sensorData.soilTemp = 0.0;
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // BH1750 - Intensidad Lumínica
    // ─────────────────────────────────────────────────────────────────────────
    if (bh1750OK) {
        sensorData.lux = bh1750.readLightLevel();
        if (sensorData.lux < 0) {
            sensorData.lux = 0.0;
        }
    } else {
        sensorData.lux = 0.0;
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // BMP280 - Presión Barométrica
    // ─────────────────────────────────────────────────────────────────────────
    if (bmp280OK) {
        sensorData.pressure = bmp280.readPressure() / 100.0F;  // Pa a hPa
    } else {
        sensorData.pressure = 0.0;
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // HD-38 - Humedad del Suelo
    // ─────────────────────────────────────────────────────────────────────────
    int soilRaw = analogRead(SOIL_HUMIDITY_PIN);
    
    // Convertir ADC a porcentaje usando calibración
    sensorData.soilHumidity = map(soilRaw, SOIL_DRY_RAW, SOIL_WET_RAW, 0, 100);
    sensorData.soilHumidity = constrain(sensorData.soilHumidity, 0, 100);
    
    // ─────────────────────────────────────────────────────────────────────────
    // Contador de paquetes
    // ─────────────────────────────────────────────────────────────────────────
    sensorData.counter = packetCounter++;
}

void printSensorData() {
    Serial.println("\n┌─────────────────────────────────────────────────────────────┐");
    Serial.println("│                    DATOS DE SENSORES                        │");
    Serial.println("├─────────────────────────────────────────────────────────────┤");
    Serial.printf("│  🌡️  Temperatura Aire:    %7.1f °C                        │\n", 
                  sensorData.temperature);
    Serial.printf("│  💧 Humedad Relativa:    %7.1f %%                         │\n", 
                  sensorData.humidity);
    Serial.printf("│  🌱 Temperatura Suelo:   %7.1f °C                        │\n", 
                  sensorData.soilTemp);
    Serial.printf("│  🪴 Humedad Suelo:       %7.1f %%                         │\n", 
                  sensorData.soilHumidity);
    Serial.printf("│  ☀️  Intensidad Luz:     %7.0f lux                       │\n", 
                  sensorData.lux);
    Serial.printf("│  🌀 Presión Atmosférica: %7.1f hPa                       │\n", 
                  sensorData.pressure);
    Serial.println("├─────────────────────────────────────────────────────────────┤");
    Serial.printf("│  📦 Paquete #%u                                            │\n", 
                  sensorData.counter);
    Serial.println("└─────────────────────────────────────────────────────────────┘");
}

void checkAlerts() {
    bool hasAlert = false;
    
    // Alerta: Suelo seco
    if (sensorData.soilHumidity < 30 && sensorData.soilHumidity > 0) {
        Serial.println("⚠️  ALERTA: Suelo seco (<30%) - Considerar riego");
        hasAlert = true;
    }
    
    // Alerta: Temperatura alta
    if (sensorData.temperature > 35) {
        Serial.println("⚠️  ALERTA: Temperatura elevada (>35°C)");
        hasAlert = true;
    }
    
    // Alerta: Riesgo de helada
    if (sensorData.temperature > 0 && sensorData.temperature < 5) {
        Serial.println("❄️  ALERTA: Riesgo de helada (<5°C)");
        hasAlert = true;
    }
    
    // Alerta: Helada en curso
    if (sensorData.temperature <= 0) {
        Serial.println("🥶 ALERTA CRÍTICA: Temperatura bajo cero - Helada en curso");
        hasAlert = true;
    }
    
    // Alerta: Diferencial térmico (inversión)
    float tempDiff = sensorData.soilTemp - sensorData.temperature;
    if (tempDiff > 3 && sensorData.temperature < 10) {
        Serial.printf("❄️  ALERTA: Inversión térmica detectada (ΔT=%.1f°C)\n", tempDiff);
        hasAlert = true;
    }
    
    // Alerta: Condiciones favorables para enfermedades
    if (sensorData.humidity > 85 && sensorData.temperature >= 15 && sensorData.temperature <= 25) {
        Serial.println("🍄 ALERTA: Condiciones favorables para enfermedades fúngicas");
        hasAlert = true;
    }
    
    // Alerta: Caída de presión (posible mal tiempo)
    // Nota: Requiere histórico para detectar tendencia
    if (sensorData.pressure < 1000 && sensorData.pressure > 0) {
        Serial.println("🌧️  INFO: Presión baja - Posible mal tiempo");
        hasAlert = true;
    }
    
    if (!hasAlert) {
        Serial.println("✅ Sin alertas - Condiciones normales");
    }
}

void transmitData() {
    Serial.print("\n📡 [LORA] Transmitiendo... ");
    
    // Transmitir estructura binaria
    int state = radio.transmit((uint8_t*)&sensorData, sizeof(SensorData));
    
    if (state == RADIOLIB_ERR_NONE) {
        txSuccess++;
        Serial.println("✓ ÉXITO");
        Serial.printf("         Payload: %d bytes | Paquete #%u\n", 
                      sizeof(SensorData), sensorData.counter);
    } else {
        txFailed++;
        Serial.print("✗ ERROR: ");
        
        switch (state) {
            case RADIOLIB_ERR_PACKET_TOO_LONG:
                Serial.println("Paquete demasiado largo");
                break;
            case RADIOLIB_ERR_TX_TIMEOUT:
                Serial.println("Timeout en transmisión");
                break;
            default:
                Serial.printf("Código %d\n", state);
                break;
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FIN DEL FIRMWARE
// ═══════════════════════════════════════════════════════════════════════════════
