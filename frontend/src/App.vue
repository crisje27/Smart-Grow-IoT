<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <!-- Navbar -->
    <nav class="bg-green-600 text-white shadow-lg">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <span class="text-2xl">🌱</span>
            <span class="font-bold text-xl">SMART GROW</span>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm opacity-75">{{ lastUpdate }}</span>
            <div :class="connectionStatus.class" class="w-3 h-3 rounded-full"></div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Navigation Tabs -->
    <div class="bg-white shadow">
      <div class="container mx-auto px-4">
        <div class="flex space-x-1">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium transition-colors',
              activeTab === tab.id 
                ? 'text-green-600 border-b-2 border-green-600' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            {{ tab.icon }} {{ tab.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <Dashboard v-if="activeTab === 'dashboard'" :sensorData="sensorData" :predictions="predictions" />
      <Sensors v-else-if="activeTab === 'sensors'" :sensorData="sensorData" :history="history" />
      <Predictions v-else-if="activeTab === 'predictions'" :predictions="predictions" />
      <Alerts v-else-if="activeTab === 'alerts'" :alerts="alerts" />
      <Settings v-else-if="activeTab === 'settings'" />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-gray-400 text-center py-4 text-sm">
      SMART GROW v1.0.0 | UTN FRT | © 2025 Cristian Rodríguez
    </footer>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import Dashboard from './components/Dashboard.vue'
import Sensors from './components/Sensors.vue'
import Predictions from './components/Predictions.vue'
import Alerts from './components/Alerts.vue'
import Settings from './components/Settings.vue'
import { apiService } from './services/api'

export default {
  name: 'App',
  components: {
    Dashboard,
    Sensors,
    Predictions,
    Alerts,
    Settings
  },
  setup() {
    const activeTab = ref('dashboard')
    const lastUpdate = ref('--:--:--')
    const updateInterval = ref(null)

    const tabs = [
      { id: 'dashboard', name: 'Dashboard', icon: '📊' },
      { id: 'sensors', name: 'Sensores', icon: '🌡️' },
      { id: 'predictions', name: 'Predicciones', icon: '🤖' },
      { id: 'alerts', name: 'Alertas', icon: '🚨' },
      { id: 'settings', name: 'Ajustes', icon: '⚙️' }
    ]

    const sensorData = reactive({
      temperature: 0,
      humidity: 0,
      soilHumidity: 0,
      soilTemp: 0,
      light: 0,
      pressure: 0,
      rssi: 0,
      snr: 0
    })

    const predictions = reactive({
      frost: { probability: 0, riskLevel: 'low', recommendation: '' },
      disease: { probability: 0, riskLevel: 'low', recommendation: '' }
    })

    const alerts = ref([])
    const history = ref([])

    const connectionStatus = computed(() => {
      const now = new Date()
      const lastTime = new Date(lastUpdate.value)
      const diff = (now - lastTime) / 1000 / 60 // minutos

      if (diff < 5) return { class: 'bg-green-500', text: 'Conectado' }
      if (diff < 15) return { class: 'bg-yellow-500', text: 'Intermitente' }
      return { class: 'bg-red-500', text: 'Desconectado' }
    })

    const fetchData = async () => {
      try {
        // Obtener datos de sensores
        const latestData = await apiService.getLatestSensorData()
        if (latestData) {
          Object.assign(sensorData, {
            temperature: latestData.temperature || 0,
            humidity: latestData.humidity || 0,
            soilHumidity: latestData.soil_humidity || 0,
            soilTemp: latestData.soil_temp || 0,
            light: latestData.light || 0,
            pressure: latestData.pressure || 0,
            rssi: latestData.rssi || 0,
            snr: latestData.snr || 0
          })
        }

        // Obtener predicciones
        const frostPred = await apiService.getFrostPrediction()
        if (frostPred) {
          predictions.frost = {
            probability: frostPred.probability,
            riskLevel: frostPred.risk_level,
            recommendation: frostPred.recommendation,
            factors: frostPred.contributing_factors
          }
        }

        const diseasePred = await apiService.getDiseasePrediction()
        if (diseasePred) {
          predictions.disease = {
            probability: diseasePred.probability,
            riskLevel: diseasePred.risk_level,
            recommendation: diseasePred.recommendation
          }
        }

        // Obtener alertas activas
        const activeAlerts = await apiService.getActiveAlerts()
        alerts.value = activeAlerts || []

        // Actualizar timestamp
        lastUpdate.value = new Date().toLocaleTimeString()

      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    onMounted(() => {
      fetchData()
      updateInterval.value = setInterval(fetchData, 30000) // Cada 30 segundos
    })

    onUnmounted(() => {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
      }
    })

    return {
      activeTab,
      tabs,
      sensorData,
      predictions,
      alerts,
      history,
      lastUpdate,
      connectionStatus
    }
  }
}
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';
</style>
