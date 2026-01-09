<template>
  <div class="space-y-6">
    <!-- Selector de Sensor y Rango -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex flex-wrap gap-4 items-center justify-between">
        <div class="flex gap-2">
          <button
            v-for="sensor in sensors"
            :key="sensor.id"
            @click="selectedSensor = sensor.id"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              selectedSensor === sensor.id
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ sensor.icon }} {{ sensor.name }}
          </button>
        </div>
        <div class="flex gap-2">
          <button
            v-for="range in timeRanges"
            :key="range.value"
            @click="selectedRange = range.value"
            :class="[
              'px-3 py-1 rounded text-sm transition-colors',
              selectedRange === range.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ range.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Gráfico -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">
        {{ currentSensor.icon }} {{ currentSensor.name }}
        <span class="text-sm font-normal text-gray-500">(últimas {{ selectedRange }}h)</span>
      </h3>
      
      <!-- Área del gráfico -->
      <div class="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
        <canvas ref="chartCanvas" class="w-full h-full"></canvas>
      </div>

      <!-- Estadísticas -->
      <div class="grid grid-cols-4 gap-4 mt-4 pt-4 border-t">
        <div class="text-center">
          <div class="text-xl font-bold text-gray-700">{{ stats.current }}</div>
          <div class="text-xs text-gray-500">Actual</div>
        </div>
        <div class="text-center">
          <div class="text-xl font-bold text-blue-600">{{ stats.min }}</div>
          <div class="text-xs text-gray-500">Mínimo</div>
        </div>
        <div class="text-center">
          <div class="text-xl font-bold text-red-600">{{ stats.max }}</div>
          <div class="text-xs text-gray-500">Máximo</div>
        </div>
        <div class="text-center">
          <div class="text-xl font-bold text-green-600">{{ stats.avg }}</div>
          <div class="text-xs text-gray-500">Promedio</div>
        </div>
      </div>
    </div>

    <!-- Valores Actuales Detallados -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">📋 Valores Actuales Detallados</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left py-2 px-4">Sensor</th>
              <th class="text-center py-2 px-4">Valor</th>
              <th class="text-center py-2 px-4">Unidad</th>
              <th class="text-center py-2 px-4">Estado</th>
              <th class="text-left py-2 px-4">Rango Normal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sensor in sensorsTable" :key="sensor.id" class="border-b hover:bg-gray-50">
              <td class="py-3 px-4">{{ sensor.icon }} {{ sensor.name }}</td>
              <td class="text-center py-3 px-4 font-mono font-bold">{{ sensor.value }}</td>
              <td class="text-center py-3 px-4 text-gray-500">{{ sensor.unit }}</td>
              <td class="text-center py-3 px-4">
                <span 
                  class="px-2 py-1 rounded-full text-xs"
                  :class="getStatusClass(sensor.status)"
                >
                  {{ sensor.status }}
                </span>
              </td>
              <td class="py-3 px-4 text-gray-500">{{ sensor.range }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sensors',
  props: {
    sensorData: {
      type: Object,
      required: true
    },
    history: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedSensor: 'temperature',
      selectedRange: 24,
      sensors: [
        { id: 'temperature', name: 'Temp. Aire', icon: '🌡️', unit: '°C' },
        { id: 'humidity', name: 'Humedad', icon: '💧', unit: '%' },
        { id: 'soilTemp', name: 'Temp. Suelo', icon: '🌱', unit: '°C' },
        { id: 'soilHumidity', name: 'Hum. Suelo', icon: '🪴', unit: '%' },
        { id: 'light', name: 'Luz', icon: '☀️', unit: 'lux' },
        { id: 'pressure', name: 'Presión', icon: '🌀', unit: 'hPa' }
      ],
      timeRanges: [
        { value: 1, label: '1h' },
        { value: 6, label: '6h' },
        { value: 24, label: '24h' },
        { value: 168, label: '7d' }
      ]
    }
  },
  computed: {
    currentSensor() {
      return this.sensors.find(s => s.id === this.selectedSensor) || this.sensors[0]
    },
    stats() {
      const value = this.sensorData[this.selectedSensor] || 0
      return {
        current: value.toFixed(1),
        min: (value - 2).toFixed(1),
        max: (value + 3).toFixed(1),
        avg: value.toFixed(1)
      }
    },
    sensorsTable() {
      return [
        {
          id: 'temperature',
          icon: '🌡️',
          name: 'Temperatura Aire',
          value: this.sensorData.temperature?.toFixed(1) || '0.0',
          unit: '°C',
          status: this.getTempStatus(this.sensorData.temperature),
          range: '10°C - 30°C'
        },
        {
          id: 'humidity',
          icon: '💧',
          name: 'Humedad Relativa',
          value: this.sensorData.humidity?.toFixed(1) || '0.0',
          unit: '%',
          status: this.getHumStatus(this.sensorData.humidity),
          range: '40% - 80%'
        },
        {
          id: 'soilTemp',
          icon: '🌱',
          name: 'Temperatura Suelo',
          value: this.sensorData.soilTemp?.toFixed(1) || '0.0',
          unit: '°C',
          status: 'Normal',
          range: '15°C - 25°C'
        },
        {
          id: 'soilHumidity',
          icon: '🪴',
          name: 'Humedad Suelo',
          value: this.sensorData.soilHumidity?.toFixed(1) || '0.0',
          unit: '%',
          status: this.getSoilStatus(this.sensorData.soilHumidity),
          range: '40% - 70%'
        },
        {
          id: 'light',
          icon: '☀️',
          name: 'Intensidad Lumínica',
          value: Math.round(this.sensorData.light) || '0',
          unit: 'lux',
          status: 'Normal',
          range: '0 - 65000 lux'
        },
        {
          id: 'pressure',
          icon: '🌀',
          name: 'Presión Barométrica',
          value: this.sensorData.pressure?.toFixed(1) || '0.0',
          unit: 'hPa',
          status: 'Normal',
          range: '1000 - 1025 hPa'
        }
      ]
    }
  },
  methods: {
    getTempStatus(temp) {
      if (temp <= 0) return 'Crítico'
      if (temp < 5 || temp > 35) return 'Alerta'
      return 'Normal'
    },
    getHumStatus(hum) {
      if (hum > 85 || hum < 30) return 'Alerta'
      return 'Normal'
    },
    getSoilStatus(hum) {
      if (hum < 30) return 'Crítico'
      if (hum < 40) return 'Alerta'
      return 'Normal'
    },
    getStatusClass(status) {
      const classes = {
        'Normal': 'bg-green-100 text-green-800',
        'Alerta': 'bg-yellow-100 text-yellow-800',
        'Crítico': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>
