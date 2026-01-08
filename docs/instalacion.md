# 📦 Guía de Instalación Completa - SMART GROW

Esta guía detalla la instalación completa del sistema SMART GROW.

## Requisitos Previos

### Hardware

**Nodo Sensor:**
- Heltec WiFi LoRa 32 V3
- Sensores (DHT22, DS18B20, BH1750, BMP280, HD-38)
- Batería LiPo 3.7V 3100mAh
- Panel solar 5V 0.75W
- Gabinete IP65

**Gateway:**
- Raspberry Pi 4 (4GB RAM recomendado)
- Waveshare SX1262 HAT
- MicroSD 64GB (Clase 10)
- Fuente 5V/3A

### Software

- Arduino IDE 2.x (nodo sensor)
- Raspberry Pi OS Lite 64-bit (gateway)
- Docker y Docker Compose

---

## Parte 1: Nodo Sensor

### 1.1 Configurar Arduino IDE

1. Abrir Arduino IDE
2. Ir a **Archivo → Preferencias**
3. En "URLs adicionales de gestor de tarjetas", agregar:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
4. Ir a **Herramientas → Placa → Gestor de tarjetas**
5. Buscar "esp32" e instalar **"esp32 by Espressif Systems"** (v2.0.11+)

### 1.2 Instalar Bibliotecas

Ir a **Herramientas → Administrar bibliotecas** e instalar:

| Biblioteca | Versión |
|------------|---------|
| RadioLib | 6.1.0+ |
| DHT sensor library | 1.4.4+ |
| BH1750 | 1.3.0+ |
| OneWire | 2.3.7+ |
| DallasTemperature | 3.9.0+ |
| Adafruit BMP280 | 2.6.8+ |

### 1.3 Conectar Hardware

```
HELTEC V3 → SENSORES
════════════════════════════
GPIO42 → DHT22 (DATA)
GPIO1  → DS18B20 (DATA)
GPIO7  → HD-38 (AOUT)
GPIO3  → BH1750/BMP280 (SDA)
GPIO4  → BH1750/BMP280 (SCL)
3.3V   → VCC sensores
GND    → GND sensores
```

**Pull-ups requeridos:**
- DHT22: 4.7KΩ entre DATA y VCC
- DS18B20: 4.7KΩ entre DATA y VCC

### 1.4 Cargar Firmware

1. Conectar Heltec V3 por USB
2. Seleccionar tarjeta: **Heltec WiFi LoRa 32(V3)**
3. Seleccionar puerto COM correcto
4. Abrir `firmware/nodo_sensor/nodo_sensor.ino`
5. Clic en **Subir**

### 1.5 Verificar Funcionamiento

Abrir Monitor Serial (115200 baud) y verificar:
- ✓ Todos los sensores inicializados
- ✓ LoRa operativo en 915 MHz
- ✓ Transmisiones exitosas

---

## Parte 2: Gateway (Raspberry Pi)

### 2.1 Preparar Raspberry Pi

1. Descargar [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Grabar **Raspberry Pi OS Lite (64-bit)** en microSD
3. Configurar WiFi y SSH en el imager
4. Insertar SD y encender

### 2.2 Configuración Inicial

```bash
# Conectar por SSH
ssh pi@raspberrypi.local

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Configurar zona horaria
sudo timedatectl set-timezone America/Argentina/Tucuman

# Habilitar SPI (para LoRa HAT)
sudo raspi-config
# → Interface Options → SPI → Enable

# Reiniciar
sudo reboot
```

### 2.3 Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y reconectar
exit
ssh pi@raspberrypi.local

# Verificar instalación
docker --version
docker compose version
```

### 2.4 Clonar Repositorio

```bash
# Instalar git
sudo apt install git -y

# Clonar repositorio
git clone https://github.com/crisje27/SMART-GROW-SISTEMA-IoT-LoRa-CON-MACHINE-LEARNING-PARA-AGRICULTURA-DE-PRECISI-N.git
cd SMART-GROW-*
```

### 2.5 Conectar Waveshare SX1262 HAT

1. Apagar Raspberry Pi
2. Conectar HAT en los pines GPIO
3. Encender y verificar conexión SPI:

```bash
ls /dev/spidev*
# Debe mostrar: /dev/spidev0.0  /dev/spidev0.1
```

### 2.6 Iniciar Stack Docker

```bash
cd gateway/docker

# Crear archivo de variables de entorno
echo "INFLUX_TOKEN=smartgrow-secret-token-$(openssl rand -hex 16)" > .env

# Iniciar servicios
docker compose up -d

# Verificar estado
docker compose ps
```

### 2.7 Instalar Dependencias del Receptor LoRa

```bash
cd ../lora_receiver

# Instalar dependencias Python
pip3 install -r requirements.txt

# Instalar driver SX1262
git clone https://github.com/waveshare/SX126X-LoRa-HAT.git
cd SX126X-LoRa-HAT
pip3 install .
cd ..
```

### 2.8 Iniciar Receptor LoRa

```bash
# Ejecutar receptor
python3 lora_receiver.py

# O como servicio en background
nohup python3 lora_receiver.py > lora.log 2>&1 &
```

---

## Parte 3: Verificación del Sistema

### 3.1 Verificar Servicios

```bash
# Estado de contenedores
docker compose ps

# Logs de servicios
docker compose logs -f influxdb
docker compose logs -f fastapi
```

### 3.2 Acceder a Interfaces

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Grafana | http://IP:3000 | admin / smartgrow2025 |
| InfluxDB | http://IP:8086 | admin / smartgrow2025 |
| API Docs | http://IP:8000/docs | - |
| Node-RED | http://IP:1880 | - |
| PWA | http://IP | - |

### 3.3 Verificar Recepción de Datos

1. Abrir Grafana (http://IP:3000)
2. Ir a Dashboard > SMART GROW
3. Verificar que llegan datos del nodo

---

## Parte 4: Configuración Avanzada (Opcional)

### 4.1 Cloudflare Tunnel (Acceso Remoto)

```bash
# Instalar cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Autenticar
cloudflared tunnel login

# Crear túnel
cloudflared tunnel create smartgrow

# Configurar
cat > ~/.cloudflared/config.yml << EOF
tunnel: <TUNNEL_ID>
credentials-file: /home/pi/.cloudflared/<TUNNEL_ID>.json
ingress:
  - hostname: app.tudominio.com
    service: http://localhost:80
  - hostname: api.tudominio.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# Ejecutar como servicio
cloudflared service install
```

### 4.2 Crear Servicio Systemd para Receptor

```bash
sudo tee /etc/systemd/system/smartgrow-lora.service << EOF
[Unit]
Description=SMART GROW LoRa Receiver
After=network.target docker.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SMART-GROW-*/gateway/lora_receiver
ExecStart=/usr/bin/python3 lora_receiver.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable smartgrow-lora
sudo systemctl start smartgrow-lora
```

---

## Solución de Problemas

### Nodo sensor no transmite
- Verificar antena conectada
- Revisar logs en Monitor Serial
- Comprobar alimentación (batería cargada)

### Gateway no recibe paquetes
- Verificar HAT SX1262 conectado correctamente
- Comprobar SPI habilitado (`ls /dev/spidev*`)
- Verificar frecuencia y sync word coinciden

### Docker no inicia
- Verificar espacio en disco: `df -h`
- Revisar logs: `docker compose logs`

### Grafana sin datos
- Verificar InfluxDB conectado
- Comprobar receptor LoRa funcionando
- Revisar logs de FastAPI

---

## Contacto

Si encuentras problemas, abre un Issue en GitHub.
