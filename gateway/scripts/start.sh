#!/bin/bash
# SMART GROW - Iniciar Servicios

echo "🚀 Iniciando SMART GROW Gateway..."

cd "$(dirname "$0")/../docker"

# Iniciar stack Docker
echo "📦 Iniciando contenedores Docker..."
docker compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando servicios..."
sleep 10

# Iniciar receptor LoRa
echo "📡 Iniciando receptor LoRa..."
cd ../lora_receiver
nohup python3 lora_receiver.py > /var/log/smartgrow/lora_receiver.log 2>&1 &

echo ""
echo "✓ Sistema iniciado"
echo ""
echo "Accesos:"
echo "  - PWA:     http://localhost"
echo "  - API:     http://localhost:8000/docs"
echo "  - Grafana: http://localhost:3000"
echo "  - Node-RED: http://localhost:1880"
