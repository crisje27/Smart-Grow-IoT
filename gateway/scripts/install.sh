#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#                    SMART GROW - Script de Instalación Gateway
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    SMART GROW - Instalación del Gateway                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que se ejecuta en Raspberry Pi
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo "⚠️  Advertencia: Este script está diseñado para Raspberry Pi"
    read -p "¿Continuar de todos modos? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. Actualizar sistema
echo "📦 [1/6] Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
echo "📦 [2/6] Instalando dependencias..."
sudo apt install -y \
    git \
    python3-pip \
    python3-venv \
    python3-spidev \
    curl

# 3. Habilitar SPI
echo "⚙️  [3/6] Habilitando SPI..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "   SPI habilitado (requiere reinicio)"
fi

# 4. Instalar Docker
echo "🐳 [4/6] Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "   Docker instalado"
else
    echo "   Docker ya instalado"
fi

# 5. Instalar dependencias Python para receptor LoRa
echo "🐍 [5/6] Instalando dependencias Python..."
pip3 install --user \
    paho-mqtt \
    spidev \
    RPi.GPIO

# 6. Crear directorio de logs
echo "📁 [6/6] Creando directorios..."
sudo mkdir -p /var/log/smartgrow
sudo chown $USER:$USER /var/log/smartgrow

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✓ Instalación completada"
echo ""
echo "Próximos pasos:"
echo "  1. Reiniciar Raspberry Pi: sudo reboot"
echo "  2. Iniciar servicios: ./start.sh"
echo "═══════════════════════════════════════════════════════════════════════════════"
