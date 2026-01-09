#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SMART GROW - Receptor LoRa Gateway                         ║
║                                                                               ║
║  Recibe paquetes del nodo sensor vía LoRa P2P y los publica en MQTT          ║
║  para su procesamiento por el stack de servicios Docker                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Hardware:
- Raspberry Pi 4 (4GB)
- Waveshare SX1262 HAT (915 MHz)

Autor: Cristian Rodríguez - UTN FRT
Versión: 1.0.0
Licencia: MIT
"""

import struct
import json
import time
import logging
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

# Waveshare SX1262 HAT library
try:
    from SX1262 import SX1262
except ImportError:
    print("ERROR: Biblioteca SX1262 no encontrada")
    print("Instalar: pip install spidev RPi.GPIO")
    print("Clonar driver: git clone https://github.com/waveshare/SX126X-LoRa-HAT")
    sys.exit(1)

# MQTT client
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERROR: paho-mqtt no encontrado")
    print("Instalar: pip install paho-mqtt")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LoRaConfig:
    """Configuración LoRa - DEBE coincidir con el nodo sensor"""
    frequency: float = 915.0      # MHz (ISM Argentina)
    bandwidth: float = 125.0      # kHz
    spreading_factor: int = 10    # SF10
    coding_rate: int = 5          # 4/5
    sync_word: int = 0xF3         # Palabra de sincronización
    power: int = 22               # dBm (no usado en RX)


@dataclass
class MQTTConfig:
    """Configuración del broker MQTT"""
    broker: str = "localhost"
    port: int = 1883
    topic_data: str = "smartgrow/sensors/node1/data"
    topic_status: str = "smartgrow/gateway/status"
    topic_alerts: str = "smartgrow/alerts"
    client_id: str = "smartgrow-gateway"
    keepalive: int = 60


@dataclass
class SX1262HATPins:
    """Pines del HAT Waveshare para Raspberry Pi"""
    spi_bus: int = 0
    clk: int = 11
    mosi: int = 10
    miso: int = 9
    cs: int = 8
    irq: int = 24
    rst: int = 22
    gpio: int = 23


# Instancias de configuración
LORA = LoRaConfig()
MQTT = MQTTConfig()
PINS = SX1262HATPins()

# ═══════════════════════════════════════════════════════════════════════════════
# ESTRUCTURA DE DATOS (debe coincidir EXACTAMENTE con el nodo sensor)
# ═══════════════════════════════════════════════════════════════════════════════

# Formato struct: < = little-endian, f = float (4 bytes), H = uint16 (2 bytes)
SENSOR_DATA_FORMAT = '<ffffffH'  # 6 floats + 1 uint16 = 26 bytes
SENSOR_DATA_SIZE = 26

FIELD_NAMES = [
    'temperature',      # Temperatura del aire (°C)
    'humidity',         # Humedad relativa (%)
    'soil_humidity',    # Humedad del suelo (%)
    'soil_temp',        # Temperatura del suelo (°C)
    'light',            # Intensidad lumínica (lux)
    'pressure',         # Presión barométrica (hPa)
    'counter',          # Contador de paquetes
]

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/smartgrow/lora_receiver.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CLASES
# ═══════════════════════════════════════════════════════════════════════════════

class LoRaReceiver:
    """Receptor LoRa para gateway SMART GROW"""
    
    def __init__(self):
        self.radio: Optional[SX1262] = None
        self.mqtt_client: Optional[mqtt.Client] = None
        self.running: bool = False
        
        # Estadísticas
        self.packets_received: int = 0
        self.packets_error: int = 0
        self.start_time: float = 0
        self.last_packet_time: float = 0
        
    def init_lora(self) -> bool:
        """Inicializa el módulo LoRa SX1262"""
        logger.info("Inicializando módulo LoRa SX1262...")
        
        try:
            self.radio = SX1262(
                spi_bus=PINS.spi_bus,
                clk=PINS.clk,
                mosi=PINS.mosi,
                miso=PINS.miso,
                cs=PINS.cs,
                irq=PINS.irq,
                rst=PINS.rst,
                gpio=PINS.gpio
            )
            
            # Configurar parámetros LoRa
            self.radio.begin(
                freq=LORA.frequency,
                bw=LORA.bandwidth,
                sf=LORA.spreading_factor,
                cr=LORA.coding_rate,
                syncWord=LORA.sync_word,
                power=LORA.power
            )
            
            logger.info(f"✓ LoRa inicializado en {LORA.frequency} MHz")
            logger.info(f"  SF={LORA.spreading_factor}, BW={LORA.bandwidth} kHz, CR=4/{LORA.coding_rate}")
            logger.info(f"  Sync Word: 0x{LORA.sync_word:02X}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error al inicializar LoRa: {e}")
            return False
    
    def init_mqtt(self) -> bool:
        """Inicializa el cliente MQTT"""
        logger.info(f"Conectando a broker MQTT ({MQTT.broker}:{MQTT.port})...")
        
        try:
            self.mqtt_client = mqtt.Client(client_id=MQTT.client_id)
            
            # Callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Mensaje de última voluntad (LWT)
            self.mqtt_client.will_set(
                MQTT.topic_status,
                json.dumps({
                    'status': 'offline',
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'unexpected_disconnect'
                }),
                retain=True
            )
            
            self.mqtt_client.connect(MQTT.broker, MQTT.port, MQTT.keepalive)
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error al conectar MQTT: {e}")
            return False
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback de conexión MQTT"""
        if rc == 0:
            logger.info("✓ Conectado a broker MQTT")
            
            # Publicar estado online
            client.publish(
                MQTT.topic_status,
                json.dumps({
                    'status': 'online',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }),
                retain=True
            )
        else:
            logger.error(f"Error de conexión MQTT: código {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback de desconexión MQTT"""
        if rc != 0:
            logger.warning(f"Desconexión inesperada de MQTT (rc={rc})")
    
    def decode_packet(self, payload: bytes) -> Optional[Dict[str, Any]]:
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
    
    def check_alerts(self, data: Dict[str, Any]) -> list:
        """Verifica condiciones de alerta"""
        alerts = []
        
        # Riesgo de helada
        if 0 < data['temperature'] < 5:
            alerts.append({
                'type': 'frost_warning',
                'severity': 'warning',
                'message': f"Riesgo de helada: {data['temperature']}°C"
            })
        
        # Helada en curso
        if data['temperature'] <= 0:
            alerts.append({
                'type': 'frost_critical',
                'severity': 'critical',
                'message': f"¡Helada en curso! {data['temperature']}°C"
            })
        
        # Suelo seco
        if 0 < data['soil_humidity'] < 30:
            alerts.append({
                'type': 'soil_dry',
                'severity': 'warning',
                'message': f"Suelo seco: {data['soil_humidity']}%"
            })
        
        # Condiciones favorables para enfermedades
        if (data['humidity'] > 85 and 
            15 <= data['temperature'] <= 25):
            alerts.append({
                'type': 'disease_risk',
                'severity': 'warning',
                'message': "Condiciones favorables para enfermedades fúngicas"
            })
        
        return alerts
    
    def publish_data(self, data: Dict[str, Any], rssi: int, snr: float):
        """Publica datos en MQTT"""
        # Agregar metadatos de recepción
        data['rssi'] = rssi
        data['snr'] = round(snr, 1)
        data['timestamp'] = datetime.now().isoformat()
        data['gateway_uptime'] = int(time.time() - self.start_time)
        
        # Publicar datos de sensores
        self.mqtt_client.publish(
            MQTT.topic_data,
            json.dumps(data)
        )
        
        # Verificar y publicar alertas
        alerts = self.check_alerts(data)
        for alert in alerts:
            alert['timestamp'] = data['timestamp']
            self.mqtt_client.publish(
                MQTT.topic_alerts,
                json.dumps(alert)
            )
            logger.warning(f"⚠️  ALERTA: {alert['message']}")
    
    def print_data(self, data: Dict[str, Any], rssi: int, snr: float):
        """Imprime datos en consola"""
        print(f"\n{'─'*60}")
        print(f"📦 Paquete #{data['counter']} recibido - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─'*60}")
        print(f"  🌡️  Temp Aire:     {data['temperature']:7.1f} °C")
        print(f"  💧 Humedad Aire:  {data['humidity']:7.1f} %")
        print(f"  🌱 Temp Suelo:    {data['soil_temp']:7.1f} °C")
        print(f"  🪴 Hum Suelo:     {data['soil_humidity']:7.1f} %")
        print(f"  ☀️  Luz:          {data['light']:7.0f} lux")
        print(f"  🌀 Presión:       {data['pressure']:7.1f} hPa")
        print(f"  📶 RSSI: {rssi} dBm | SNR: {snr:.1f} dB")
    
    def run(self):
        """Bucle principal de recepción"""
        self.running = True
        self.start_time = time.time()
        
        logger.info("📡 Esperando paquetes LoRa...")
        print("\n" + "="*60)
        print("  SMART GROW - Gateway LoRa Activo")
        print("  Presiona Ctrl+C para detener")
        print("="*60)
        
        try:
            while self.running:
                # Recibir paquete (timeout interno del módulo)
                payload, rssi, snr = self.radio.receive()
                
                if payload:
                    self.packets_received += 1
                    self.last_packet_time = time.time()
                    
                    # Decodificar datos
                    data = self.decode_packet(payload)
                    
                    if data:
                        # Mostrar en consola
                        self.print_data(data, rssi, snr)
                        
                        # Publicar en MQTT
                        self.publish_data(data, rssi, snr)
                        
                        logger.info(f"✓ Paquete #{data['counter']} procesado (RSSI: {rssi} dBm)")
                    else:
                        self.packets_error += 1
                        logger.warning("Paquete recibido pero no se pudo decodificar")
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Interrupción de usuario recibida")
        except Exception as e:
            logger.error(f"Error en bucle principal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el receptor"""
        self.running = False
        
        print("\n" + "="*60)
        print("  Deteniendo receptor...")
        print("="*60)
        
        # Estadísticas finales
        runtime = time.time() - self.start_time
        print(f"\n📊 Estadísticas de sesión:")
        print(f"   Tiempo de operación: {runtime/3600:.2f} horas")
        print(f"   Paquetes recibidos:  {self.packets_received}")
        print(f"   Paquetes con error:  {self.packets_error}")
        if self.packets_received > 0:
            success_rate = (self.packets_received - self.packets_error) / self.packets_received * 100
            print(f"   Tasa de éxito:       {success_rate:.1f}%")
        
        # Publicar estado offline
        if self.mqtt_client:
            self.mqtt_client.publish(
                MQTT.topic_status,
                json.dumps({
                    'status': 'offline',
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'graceful_shutdown',
                    'stats': {
                        'packets_received': self.packets_received,
                        'packets_error': self.packets_error,
                        'runtime_hours': round(runtime/3600, 2)
                    }
                }),
                retain=True
            )
            
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("✓ Gateway detenido correctamente")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("  SMART GROW - Gateway LoRa")
    print("  Sistema IoT para Agricultura de Precisión")
    print("  Versión 1.0.0")
    print("="*60 + "\n")
    
    # Crear instancia del receptor
    receiver = LoRaReceiver()
    
    # Configurar handler de señales para shutdown limpio
    def signal_handler(sig, frame):
        logger.info("Señal de terminación recibida")
        receiver.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Inicializar LoRa
    if not receiver.init_lora():
        logger.error("No se pudo inicializar LoRa. Abortando.")
        sys.exit(1)
    
    # Inicializar MQTT
    if not receiver.init_mqtt():
        logger.error("No se pudo conectar a MQTT. Abortando.")
        sys.exit(1)
    
    # Ejecutar bucle principal
    receiver.run()


if __name__ == "__main__":
    main()
