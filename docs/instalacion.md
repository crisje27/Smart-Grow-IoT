# 📖 Guía de Instalación - SMART GROW

Esta guía detalla el proceso de instalación completo del sistema SMART GROW.

## Requisitos Previos

### Hardware
- **Nodo Sensor**: Heltec WiFi LoRa 32 V3 + sensores
- **Gateway**: Raspberry Pi 4 (2GB+ RAM) + Waveshare SX1262 HAT
- **Almacenamiento**: microSD 32GB+ (Class 10)

### Software
- Raspberry Pi OS Lite (64-bit)
- Docker + Docker Compose
- Python 3.11+
- Arduino IDE 2.x

---

## 1. Instalación del Gateway (Raspberry Pi)

### 1.1 Preparar Raspberry Pi OS

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y git python3-pip python3-venv curl
```

### 1.2 Habilitar SPI para LoRa HAT

```bash
sudo raspi-config
# Ir a: Interface Options → SPI → Enable

# O agregar manualmente:
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
sudo reboot
```

### 1.3 Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 1.4 Clonar Repositorio

```bash
cd ~
git clone https://github.com/crisje27/SMART-GROW.git
cd SMART-GROW
```

### 1.5 Instalar Dependencias Python

```bash
pip3 install -r gateway/lora_receiver/requirements.txt
```

### 1.6 Iniciar Stack Docker

```bash
cd gateway/docker
docker compose up -d
```

### 1.7 Verificar Servicios

```bash
docker compose ps
```

Deberías ver 6 servicios corriendo:
- `smartgrow-influxdb` (puerto 8086)
- `smartgrow-mosquitto` (puerto 1883)
- `smartgrow-api` (puerto 8000)
- `smartgrow-grafana` (puerto 3000)
- `smartgrow-nodered` (puerto 1880)
- `smartgrow-frontend` (puerto 80)

### 1.8 Iniciar Receptor LoRa

```bash
cd ~/SMART-GROW/gateway/lora_receiver
python3 lora_receiver.py
```

Para ejecutar en background:
```bash
nohup python3 lora_receiver.py > /var/log/smartgrow/lora.log 2>&1 &
```

---

## 2. Programación del Nodo Sensor (ESP32)

### 2.1 Configurar Arduino IDE

1. Abrir **Arduino IDE 2.x**
2. Ir a `File → Preferences`
3. En "Additional Boards Manager URLs" agregar:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
4. Ir a `Tools → Board → Boards Manager`
5. Buscar "esp32" e instalar **esp32 by Espressif** (v2.0.11+)

### 2.2 Instalar Bibliotecas

Ir a `Sketch → Include Library → Manage Libraries` e instalar:

| Biblioteca | Versión |
|------------|---------|
| RadioLib | 6.1.0+ |
| DHT sensor library | 1.4.4+ |
| BH1750 | 1.3.0+ |
| OneWire | 2.3.7+ |
| DallasTemperature | 3.9.0+ |
| Adafruit BMP280 | 2.6.8+ |

### 2.3 Configurar Board

`Tools → Board → esp32 → Heltec WiFi LoRa 32(V3)`

### 2.4 Cargar Firmware

1. Abrir `firmware/nodo_sensor/nodo_sensor.ino`
2. Conectar Heltec V3 por USB
3. Seleccionar puerto COM correcto
4. Click en **Upload**

### 2.5 Verificar Funcionamiento

Abrir **Serial Monitor** (115200 baud). Deberías ver:

```
╔═══════════════════════════════════════════════════════════════╗
║              SMART GROW - Nodo Sensor IoT LoRa                ║
╚═══════════════════════════════════════════════════════════════╝

[INIT] Iniciando sensores...
  ✓ DHT22: OK
  ✓ DS18B20: OK  
  ✓ BH1750: OK
  ✓ BMP280: OK
  ✓ HD-38: OK

[LORA] Configurando SX1262...
  ✓ LoRa inicializado correctamente
```

---

## 3. Acceso a Interfaces

Una vez todo funcionando, acceder desde el navegador:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **PWA** | http://[IP_GATEWAY] | - |
| **API Docs** | http://[IP_GATEWAY]:8000/docs | - |
| **Grafana** | http://[IP_GATEWAY]:3000 | admin / smartgrow2025 |
| **Node-RED** | http://[IP_GATEWAY]:1880 | - |
| **InfluxDB** | http://[IP_GATEWAY]:8086 | admin / smartgrow2025 |

---

## 4. Configurar Acceso Remoto (Cloudflare Tunnel)

### 4.1 Instalar cloudflared

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared
```

### 4.2 Autenticar

```bash
cloudflared tunnel login
```

### 4.3 Crear Tunnel

```bash
cloudflared tunnel create smartgrow
cloudflared tunnel route dns smartgrow tu-dominio.com
```

### 4.4 Configurar

Crear `/etc/cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: tu-dominio.com
    service: http://localhost:80
  - hostname: api.tu-dominio.com
    service: http://localhost:8000
  - service: http_status:404
```

### 4.5 Ejecutar como Servicio

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## 5. Verificación Final

### Checklist

- [ ] Raspberry Pi con Docker corriendo
- [ ] 6 contenedores activos (`docker compose ps`)
- [ ] Receptor LoRa recibiendo datos
- [ ] Nodo sensor transmitiendo cada 15 min
- [ ] PWA mostrando datos actuales
- [ ] Grafana con dashboards
- [ ] Acceso remoto funcionando (opcional)

### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Reiniciar un servicio específico
docker compose restart fastapi

# Ver uso de recursos
docker stats

# Verificar receptor LoRa
tail -f /var/log/smartgrow/lora.log
```

---

## Solución de Problemas

### El nodo no transmite
1. Verificar antena conectada (¡CRÍTICO!)
2. Verificar frecuencia (915 MHz)
3. Verificar Sync Word coincide (0xF3)

### Gateway no recibe
1. Verificar SPI habilitado
2. Verificar conexión del HAT
3. Ejecutar: `ls /dev/spidev*`

### Docker no inicia
```bash
sudo systemctl restart docker
docker compose down
docker compose up -d
```

### InfluxDB sin datos
1. Verificar receptor LoRa corriendo
2. Verificar conexión MQTT
3. Ver logs: `docker logs smartgrow-influxdb`

---

## Soporte

- **GitHub Issues**: [github.com/crisje27/SMART-GROW/issues](https://github.com/crisje27/SMART-GROW/issues)
- **Email**: cristianrodriguez@example.com

---

*SMART GROW v1.0.0 - UTN Facultad Regional Tucumán*
