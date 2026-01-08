#!/usr/bin/env python3
"""
SMART GROW - Receptor LoRa para Gateway
========================================
Recibe paquetes del nodo sensor vía LoRa P2P y los publica en MQTT.

Hardware:
- Raspberry Pi 4
- Waveshare SX1262 HAT

Autor: Cristian Rodríguez
Versión: 1.0.0
Licencia: MIT
"""

import struct
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Waveshare SX1262 HAT library
from SX1262 import SX1262

# MQTT client
import paho.mqtt.client as mqtt

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Configuración LoRa (DEBE coincidir con el nodo sensor)
LORA_CONFIG = {
    'frequency': 915.0,      # MHz (ISM Argentina)
    'bandwidth': 125.0,      # kHz
    'spreading_factor': 10,  # SF10
    'coding_rate': 5,        # 4/5
    'sync_word': 0xF3,       # Palabra de sincronización
    'power': 22,             # dBm (no usado en RX)
}

# Configuración MQTT
MQTT_CONFIG = {
    'broker': 'localhost',
    'port': 1883,
    'topic_data': 'smartgrow/sensors/node1/data',
    'topic_status': 'smartgrow/gateway/status',
    'client_id': 'smartgrow-gateway',
}

# Configuración de pines SX1262 HAT para Raspberry Pi
SX1262_CONFIG = {
    'spi_bus': 0,
    'clk': 11,
    'mosi': 10,
    'miso': 9,
    'cs': 8,
    'irq': 24,
    'rst': 22,
    'gpio': 23,
}

# ============================================================================
# ESTRUCTURA DE DATOS (debe coincidir con el nodo sensor)
# ============================================================================

SENSOR_DATA_FORMAT = '<ffffffH'  # 6 floats + 1 uint16 = 26 bytes
SENSOR_DATA_SIZE = 26

FIELD_NAMES = [
    'temperature',      # °C - Temperatura del aire
    'humidity',         # % - Humedad relativa
    'soil_humidity',    # % - Humedad del suelo
    'soil_temp',        # °C - Temperatura del suelo
    'light',            # lux - Intensidad lumínica
    'pressure',         # hPa - Presión barométrica
    'counter',          # Contador de paquetes
]

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES
# ============================================================================

def decode_sensor_packet(payload: bytes) -> Optional[Dict[str, Any]]:
    """
    Decodifica un paquete binario de datos de sensores.
    
    Args:
        payload: Bytes recibidos del nodo sensor (26 bytes)
        
    Returns:
        Diccionario con datos decodificados o None si hay error
    """
    if len(payload) != SENSOR_DATA_SIZE:
        logger.warning(f"Tamaño de paquete inválido: {len(payload)} bytes (esperado: {SENSOR_DATA_SIZE})")
        return None
    
    try:
        # Desempaquetar estructura binaria
        values = struct.unpack(SENSOR_DATA_FORMAT, bytes(payload))
        
        # Crear diccionario con nombres de campos
        data = {}
        for i, name in enumerate(FIELD_NAMES):
            value = values[i]
            # Redondear floats para mejor legibilidad
            if isinstance(value, float):
                data[name] = round(value, 2)
            else:
                data[name] = value
        
        return data
        
    except struct.error as e:
        logger.error(f"Error al decodificar paquete: {e}")
        return None


def create_mqtt_client() -> mqtt.Client:
    """Crea y configura el cliente MQTT."""
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("✓ Conectado a broker MQTT")
            # Publicar estado online
            client.publish(
                MQTT_CONFIG['topic_status'],
                json.dumps({'status': 'online', 'timestamp': datetime.now().isoformat()}),
                retain=True
            )
        else:
            logger.error(f"Error de conexión MQTT: {rc}")
    
    def on_disconnect(client, userdata, rc):
        logger.warning(f"Desconectado de MQTT (rc={rc})")
    
    client = mqtt.Client(client_id=MQTT_CONFIG['client_id'])
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    # Configurar mensaje de última voluntad (LWT)
    client.will_set(
        MQTT_CONFIG['topic_status'],
        json.dumps({'status': 'offline', 'timestamp': datetime.now().isoformat()}),
        retain=True
    )
    
    return client


def init_lora() -> SX1262:
    """Inicializa el módulo LoRa SX1262."""
    
    logger.info("Inicializando módulo LoRa SX1262...")
    
    sx1262 = SX1262(
        spi_bus=SX1262_CONFIG['spi_bus'],
        clk=SX1262_CONFIG['clk'],
        mosi=SX1262_CONFIG['mosi'],
        miso=SX1262_CONFIG['miso'],
        cs=SX1262_CONFIG['cs'],
        irq=SX1262_CONFIG['irq'],
        rst=SX1262_CONFIG['rst'],
        gpio=SX1262_CONFIG['gpio']
    )
    
    # Configurar parámetros LoRa
    sx1262.begin(
        freq=LORA_CONFIG['frequency'],
        bw=LORA_CONFIG['bandwidth'],
        sf=LORA_CONFIG['spreading_factor'],
        cr=LORA_CONFIG['coding_rate'],
        syncWord=LORA_CONFIG['sync_word'],
        power=LORA_CONFIG['power']
    )
    
    logger.info(f"✓ LoRa inicializado en {LORA_CONFIG['frequency']} MHz")
    logger.info(f"  SF={LORA_CONFIG['spreading_factor']}, BW={LORA_CONFIG['bandwidth']} kHz")
    
    return sx1262


def main():
    """Función principal del receptor LoRa."""
    
    print("\n" + "="*60)
    print("  SMART GROW - Gateway LoRa")
    print("  Receptor de datos agrícolas")
    print("="*60 + "\n")
    
    # Inicializar LoRa
    try:
        radio = init_lora()
    except Exception as e:
        logger.error(f"Error al inicializar LoRa: {e}")
        return
    
    # Conectar a MQTT
    mqtt_client = create_mqtt_client()
    
    try:
        mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'])
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"Error al conectar MQTT: {e}")
        return
    
    # Contadores de estadísticas
    packets_received = 0
    packets_error = 0
    start_time = time.time()
    
    logger.info("📡 Esperando paquetes LoRa...\n")
    
    try:
        while True:
            # Recibir paquete (bloqueante)
            payload, rssi, snr = radio.receive()
            
            if payload:
                packets_received += 1
                
                # Decodificar datos
                data = decode_sensor_packet(payload)
                
                if data:
                    # Agregar metadatos de recepción
                    data['rssi'] = rssi
                    data['snr'] = round(snr, 1)
                    data['timestamp'] = datetime.now().isoformat()
                    data['gateway_uptime'] = int(time.time() - start_time)
                    
                    # Mostrar en consola
                    print(f"\n{'─'*50}")
                    print(f"📦 Paquete #{data['counter']} recibido")
                    print(f"{'─'*50}")
                    print(f"  🌡️  Temp Aire:     {data['temperature']:6.1f} °C")
                    print(f"  💧 Humedad Aire:  {data['humidity']:6.1f} %")
                    print(f"  🌱 Temp Suelo:    {data['soil_temp']:6.1f} °C")
                    print(f"  🪴 Hum Suelo:     {data['soil_humidity']:6.1f} %")
                    print(f"  ☀️  Luz:          {data['light']:6.0f} lux")
                    print(f"  🌀 Presión:       {data['pressure']:6.1f} hPa")
                    print(f"  📶 RSSI:          {rssi} dBm | SNR: {snr:.1f} dB")
                    
                    # Publicar en MQTT
                    mqtt_client.publish(
                        MQTT_CONFIG['topic_data'],
                        json.dumps(data)
                    )
                    logger.info(f"✓ Publicado en MQTT: {MQTT_CONFIG['topic_data']}")
                    
                else:
                    packets_error += 1
                    logger.warning("Paquete recibido pero no se pudo decodificar")
            
            # Pequeña pausa para no saturar CPU
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("  Deteniendo receptor...")
        print("="*60)
        
        # Estadísticas finales
        runtime = time.time() - start_time
        print(f"\n📊 Estadísticas de sesión:")
        print(f"   Tiempo de operación: {runtime/3600:.2f} horas")
        print(f"   Paquetes recibidos:  {packets_received}")
        print(f"   Paquetes con error:  {packets_error}")
        if packets_received > 0:
            success_rate = (packets_received - packets_error) / packets_received * 100
            print(f"   Tasa de éxito:       {success_rate:.1f}%")
        
        # Publicar estado offline
        mqtt_client.publish(
            MQTT_CONFIG['topic_status'],
            json.dumps({'status': 'offline', 'timestamp': datetime.now().isoformat()}),
            retain=True
        )
        
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        
        print("\n✓ Gateway detenido correctamente\n")


if __name__ == "__main__":
    main()
