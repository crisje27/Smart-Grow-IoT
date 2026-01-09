<template>
  <div class="space-y-6">
    <!-- Información del Sistema -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">ℹ️ Información del Sistema</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Versión</span>
            <span class="font-medium">1.0.0</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Modo</span>
            <span class="font-medium text-green-600">Producción</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Uptime Gateway</span>
            <span class="font-medium">15 días 4 horas</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Última actualización</span>
            <span class="font-medium">{{ new Date().toLocaleString() }}</span>
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Intervalo TX</span>
            <span class="font-medium">15 minutos</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Frecuencia LoRa</span>
            <span class="font-medium">915 MHz</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Spreading Factor</span>
            <span class="font-medium">SF10</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span class="text-gray-600">Nodos activos</span>
            <span class="font-medium">1</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuración de Notificaciones -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">🔔 Notificaciones</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between py-2">
          <div>
            <div class="font-medium text-gray-800">Notificaciones Push</div>
            <div class="text-sm text-gray-500">Recibir alertas en el navegador</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.pushEnabled" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </div>
        
        <div class="flex items-center justify-between py-2">
          <div>
            <div class="font-medium text-gray-800">Solo alertas críticas</div>
            <div class="text-sm text-gray-500">Ignorar advertencias e info</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.criticalOnly" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </div>

        <div class="flex items-center justify-between py-2">
          <div>
            <div class="font-medium text-gray-800">Horario silencioso</div>
            <div class="text-sm text-gray-500">No notificar entre 22:00 y 06:00</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.quietHours" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Calibración de Sensores -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">🔧 Calibración de Sensores</h2>
      
      <div class="space-y-6">
        <!-- Humedad de Suelo -->
        <div>
          <h3 class="font-medium text-gray-700 mb-3">🪴 Sensor Humedad de Suelo (HD-38)</h3>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">Valor en seco (ADC)</label>
              <input 
                type="number" 
                v-model="calibration.soilDry"
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Valor en agua (ADC)</label>
              <input 
                type="number" 
                v-model="calibration.soilWet"
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
            </div>
          </div>
        </div>

        <!-- Offset de Temperatura -->
        <div>
          <h3 class="font-medium text-gray-700 mb-3">🌡️ Offset de Temperatura</h3>
          <div class="flex items-center space-x-4">
            <input 
              type="range" 
              v-model="calibration.tempOffset"
              min="-5" 
              max="5" 
              step="0.1"
              class="flex-1"
            >
            <span class="font-mono w-16 text-center">{{ calibration.tempOffset }}°C</span>
          </div>
        </div>
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <button class="px-4 py-2 text-gray-600 hover:text-gray-800">
          Restaurar valores
        </button>
        <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
          Guardar cambios
        </button>
      </div>
    </div>

    <!-- Conexión API -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">🔌 Conexión API</h2>
      <div class="space-y-3">
        <div>
          <label class="block text-sm text-gray-600 mb-1">URL del API</label>
          <input 
            type="url" 
            v-model="apiUrl"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            placeholder="http://localhost:8000"
          >
        </div>
        <div class="flex items-center space-x-2">
          <div 
            class="w-3 h-3 rounded-full"
            :class="apiConnected ? 'bg-green-500' : 'bg-red-500'"
          ></div>
          <span class="text-sm text-gray-600">
            {{ apiConnected ? 'Conectado' : 'Desconectado' }}
          </span>
          <button 
            @click="testConnection"
            class="ml-auto text-sm text-blue-600 hover:text-blue-800"
          >
            Probar conexión
          </button>
        </div>
      </div>
    </div>

    <!-- Acerca de -->
    <div class="bg-gray-50 rounded-lg p-6 text-center">
      <span class="text-4xl">🌱</span>
      <h3 class="text-xl font-bold text-gray-800 mt-2">SMART GROW</h3>
      <p class="text-gray-600">Sistema IoT LoRa con Machine Learning para Agricultura de Precisión</p>
      <p class="text-sm text-gray-500 mt-2">
        Desarrollado por Cristian Rodríguez<br>
        UTN - Facultad Regional Tucumán<br>
        © 2025
      </p>
      <div class="mt-4 flex justify-center space-x-4">
        <a href="https://github.com/crisje27" class="text-gray-400 hover:text-gray-600">
          GitHub
        </a>
        <a href="#" class="text-gray-400 hover:text-gray-600">
          Documentación
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      settings: {
        pushEnabled: true,
        criticalOnly: false,
        quietHours: true
      },
      calibration: {
        soilDry: 4095,
        soilWet: 1500,
        tempOffset: 0
      },
      apiUrl: 'http://localhost:8000',
      apiConnected: true
    }
  },
  methods: {
    testConnection() {
      // Simular test de conexión
      this.apiConnected = !this.apiConnected
    }
  }
}
</script>
