<template>
  <div class="space-y-6">
    <!-- Resumen de Alertas -->
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-red-50 rounded-lg p-4 border border-red-200">
        <div class="text-3xl font-bold text-red-600">{{ criticalCount }}</div>
        <div class="text-sm text-red-700">Críticas</div>
      </div>
      <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
        <div class="text-3xl font-bold text-yellow-600">{{ warningCount }}</div>
        <div class="text-sm text-yellow-700">Advertencias</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div class="text-3xl font-bold text-blue-600">{{ infoCount }}</div>
        <div class="text-sm text-blue-700">Informativas</div>
      </div>
    </div>

    <!-- Lista de Alertas Activas -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-6 border-b">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-800">🚨 Alertas Activas</h2>
          <button 
            @click="acknowledgeAll"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            Marcar todas como leídas
          </button>
        </div>
      </div>
      
      <div v-if="activeAlerts.length === 0" class="p-12 text-center">
        <span class="text-6xl">✅</span>
        <p class="text-gray-500 mt-4">No hay alertas activas</p>
        <p class="text-sm text-gray-400">El sistema está funcionando correctamente</p>
      </div>

      <div v-else class="divide-y">
        <div 
          v-for="alert in activeAlerts" 
          :key="alert.id"
          class="p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <span class="text-2xl">{{ getAlertIcon(alert.type) }}</span>
              <div>
                <div class="flex items-center space-x-2">
                  <span 
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :class="getSeverityClass(alert.severity)"
                  >
                    {{ alert.severity.toUpperCase() }}
                  </span>
                  <span class="text-sm text-gray-500">{{ formatTime(alert.timestamp) }}</span>
                </div>
                <p class="text-gray-800 mt-1">{{ alert.message }}</p>
                <p v-if="alert.value" class="text-sm text-gray-500">
                  Valor: {{ alert.value }} | Umbral: {{ alert.threshold }}
                </p>
              </div>
            </div>
            <button 
              @click="acknowledgeAlert(alert.id)"
              class="text-gray-400 hover:text-gray-600"
              title="Marcar como leída"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuración de Alertas -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">⚙️ Configuración de Umbrales</h2>
      
      <div class="space-y-4">
        <div 
          v-for="config in alertConfigs" 
          :key="config.type"
          class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <span class="text-2xl">{{ config.icon }}</span>
            <div>
              <div class="font-medium text-gray-800">{{ config.name }}</div>
              <div class="text-sm text-gray-500">
                Advertencia: {{ config.warning }} | Crítico: {{ config.critical }}
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <label class="flex items-center space-x-2">
              <input 
                type="checkbox" 
                :checked="config.enabled"
                class="rounded text-green-600"
              >
              <span class="text-sm text-gray-600">Activo</span>
            </label>
            <button class="text-blue-600 hover:text-blue-800 text-sm">
              Editar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Histórico -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">📜 Histórico de Alertas (24h)</h2>
      <div class="text-center text-gray-500 py-8">
        <span class="text-4xl">📋</span>
        <p class="mt-2">El histórico de alertas estará disponible próximamente</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Alerts',
  props: {
    alerts: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      alertConfigs: [
        { type: 'frost', name: 'Heladas', icon: '❄️', warning: '5°C', critical: '0°C', enabled: true },
        { type: 'disease', name: 'Enfermedades', icon: '🍄', warning: '70%', critical: '85%', enabled: true },
        { type: 'soil_dry', name: 'Suelo Seco', icon: '🏜️', warning: '30%', critical: '20%', enabled: true },
        { type: 'high_temp', name: 'Temperatura Alta', icon: '🔥', warning: '35°C', critical: '40°C', enabled: true },
        { type: 'sensor_offline', name: 'Sensor Offline', icon: '📡', warning: '15 min', critical: '30 min', enabled: true }
      ]
    }
  },
  computed: {
    activeAlerts() {
      return this.alerts.filter(a => !a.acknowledged)
    },
    criticalCount() {
      return this.activeAlerts.filter(a => a.severity === 'critical').length
    },
    warningCount() {
      return this.activeAlerts.filter(a => a.severity === 'warning').length
    },
    infoCount() {
      return this.activeAlerts.filter(a => a.severity === 'info').length
    }
  },
  methods: {
    getAlertIcon(type) {
      const icons = {
        frost: '❄️',
        disease: '🍄',
        soil_dry: '🏜️',
        high_temp: '🔥',
        sensor_offline: '📡',
        low_battery: '🔋'
      }
      return icons[type] || '⚠️'
    },
    getSeverityClass(severity) {
      const classes = {
        critical: 'bg-red-100 text-red-800',
        warning: 'bg-yellow-100 text-yellow-800',
        info: 'bg-blue-100 text-blue-800'
      }
      return classes[severity] || 'bg-gray-100 text-gray-800'
    },
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString()
    },
    acknowledgeAlert(id) {
      // En implementación real: llamar a API
      console.log('Acknowledging alert:', id)
    },
    acknowledgeAll() {
      // En implementación real: llamar a API
      console.log('Acknowledging all alerts')
    }
  }
}
</script>
