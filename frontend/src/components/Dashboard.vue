<template>
  <div class="space-y-6">
    <!-- Resumen de Estado -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">📊 Estado Actual del Cultivo</h2>
      
      <!-- Tarjetas de Sensores -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <SensorCard
          title="Temp. Aire"
          :value="sensorData.temperature"
          unit="°C"
          icon="🌡️"
          :status="getTempStatus(sensorData.temperature)"
        />
        <SensorCard
          title="Humedad"
          :value="sensorData.humidity"
          unit="%"
          icon="💧"
          :status="getHumidityStatus(sensorData.humidity)"
        />
        <SensorCard
          title="Temp. Suelo"
          :value="sensorData.soilTemp"
          unit="°C"
          icon="🌱"
          :status="getSoilTempStatus(sensorData.soilTemp)"
        />
        <SensorCard
          title="Hum. Suelo"
          :value="sensorData.soilHumidity"
          unit="%"
          icon="🪴"
          :status="getSoilHumidityStatus(sensorData.soilHumidity)"
        />
        <SensorCard
          title="Luz"
          :value="sensorData.light"
          unit="lux"
          icon="☀️"
          :status="'normal'"
        />
        <SensorCard
          title="Presión"
          :value="sensorData.pressure"
          unit="hPa"
          icon="🌀"
          :status="'normal'"
        />
      </div>
    </div>

    <!-- Panel de Predicciones -->
    <div class="grid md:grid-cols-2 gap-6">
      <!-- Predicción Heladas -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">❄️ Riesgo de Helada</h3>
        <div class="flex items-center justify-between mb-4">
          <RiskIndicator 
            :level="predictions.frost.riskLevel" 
            :probability="predictions.frost.probability"
          />
          <div class="text-right">
            <div class="text-3xl font-bold" :class="getRiskColor(predictions.frost.riskLevel)">
              {{ predictions.frost.probability }}%
            </div>
            <div class="text-sm text-gray-500">Probabilidad 12-24h</div>
          </div>
        </div>
        <div class="text-sm text-gray-600 bg-gray-50 rounded p-3">
          💡 {{ predictions.frost.recommendation || 'Sin recomendaciones' }}
        </div>
      </div>

      <!-- Predicción Enfermedades -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">🍄 Riesgo Enfermedades</h3>
        <div class="flex items-center justify-between mb-4">
          <RiskIndicator 
            :level="predictions.disease.riskLevel" 
            :probability="predictions.disease.probability"
          />
          <div class="text-right">
            <div class="text-3xl font-bold" :class="getRiskColor(predictions.disease.riskLevel)">
              {{ predictions.disease.probability }}%
            </div>
            <div class="text-sm text-gray-500">Condiciones favorables</div>
          </div>
        </div>
        <div class="text-sm text-gray-600 bg-gray-50 rounded p-3">
          💡 {{ predictions.disease.recommendation || 'Sin recomendaciones' }}
        </div>
      </div>
    </div>

    <!-- Información de Señal -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">📡 Estado de Conexión</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-700">{{ sensorData.rssi }}</div>
          <div class="text-sm text-gray-500">RSSI (dBm)</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-700">{{ sensorData.snr }}</div>
          <div class="text-sm text-gray-500">SNR (dB)</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">96%</div>
          <div class="text-sm text-gray-500">Tasa TX Éxito</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-600">15 min</div>
          <div class="text-sm text-gray-500">Intervalo TX</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SensorCard from './SensorCard.vue'
import RiskIndicator from './RiskIndicator.vue'

export default {
  name: 'Dashboard',
  components: {
    SensorCard,
    RiskIndicator
  },
  props: {
    sensorData: {
      type: Object,
      required: true
    },
    predictions: {
      type: Object,
      required: true
    }
  },
  methods: {
    getTempStatus(temp) {
      if (temp <= 0) return 'critical'
      if (temp < 5) return 'warning'
      if (temp > 35) return 'warning'
      return 'normal'
    },
    getHumidityStatus(hum) {
      if (hum > 85) return 'warning'
      if (hum < 30) return 'warning'
      return 'normal'
    },
    getSoilTempStatus(temp) {
      if (temp < 5) return 'warning'
      return 'normal'
    },
    getSoilHumidityStatus(hum) {
      if (hum < 30) return 'critical'
      if (hum < 40) return 'warning'
      return 'normal'
    },
    getRiskColor(level) {
      const colors = {
        low: 'text-green-600',
        medium: 'text-yellow-600',
        high: 'text-red-600'
      }
      return colors[level] || 'text-gray-600'
    }
  }
}
</script>
