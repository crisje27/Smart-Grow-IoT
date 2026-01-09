<template>
  <div class="space-y-6">
    <!-- Predicción de Heladas -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">❄️ Predicción de Heladas</h2>
            <p class="text-blue-100 text-sm">Modelo XGBoost - Horizonte 12-24 horas</p>
          </div>
          <div class="text-right">
            <div class="text-4xl font-bold">{{ predictions.frost.probability }}%</div>
            <div class="text-blue-100 text-sm">Probabilidad</div>
          </div>
        </div>
      </div>
      
      <div class="p-6">
        <!-- Indicador de Riesgo -->
        <div class="flex justify-center mb-6">
          <RiskIndicator 
            :level="predictions.frost.riskLevel" 
            :probability="predictions.frost.probability"
          />
        </div>

        <!-- Factores Contribuyentes -->
        <div class="mb-6">
          <h3 class="font-semibold text-gray-700 mb-3">📊 Factores Contribuyentes</h3>
          <div class="space-y-2">
            <div 
              v-for="(factor, index) in frostFactors" 
              :key="index"
              class="flex items-center justify-between bg-gray-50 rounded p-3"
            >
              <span class="text-sm text-gray-700">{{ factor.name }}</span>
              <div class="flex items-center space-x-2">
                <div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-blue-500 rounded-full"
                    :style="{ width: factor.importance + '%' }"
                  ></div>
                </div>
                <span class="text-sm font-medium text-gray-600 w-10">{{ factor.importance }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recomendación -->
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <div class="flex items-start">
            <span class="text-2xl mr-3">💡</span>
            <div>
              <h4 class="font-semibold text-blue-800">Recomendación</h4>
              <p class="text-blue-700 text-sm">{{ predictions.frost.recommendation || 'Sin recomendaciones específicas.' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Predicción de Enfermedades -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">🍄 Riesgo de Enfermedades</h2>
            <p class="text-orange-100 text-sm">Modelo Random Forest - Patógenos fúngicos</p>
          </div>
          <div class="text-right">
            <div class="text-4xl font-bold">{{ predictions.disease.probability }}%</div>
            <div class="text-orange-100 text-sm">Probabilidad</div>
          </div>
        </div>
      </div>
      
      <div class="p-6">
        <!-- Indicador de Riesgo -->
        <div class="flex justify-center mb-6">
          <RiskIndicator 
            :level="predictions.disease.riskLevel" 
            :probability="predictions.disease.probability"
          />
        </div>

        <!-- Condiciones Actuales -->
        <div class="mb-6">
          <h3 class="font-semibold text-gray-700 mb-3">🌡️ Condiciones Actuales</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ diseaseConditions.humidity }}%</div>
              <div class="text-sm text-gray-500">Humedad Relativa</div>
              <div 
                class="text-xs mt-1"
                :class="diseaseConditions.humidity > 85 ? 'text-red-500' : 'text-green-500'"
              >
                {{ diseaseConditions.humidity > 85 ? '⚠️ Favorable' : '✅ Normal' }}
              </div>
            </div>
            <div class="bg-gray-50 rounded p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ diseaseConditions.temperature }}°C</div>
              <div class="text-sm text-gray-500">Temperatura</div>
              <div 
                class="text-xs mt-1"
                :class="diseaseConditions.tempFavorable ? 'text-red-500' : 'text-green-500'"
              >
                {{ diseaseConditions.tempFavorable ? '⚠️ Rango crítico (15-25°C)' : '✅ Fuera de rango' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Recomendación -->
        <div class="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
          <div class="flex items-start">
            <span class="text-2xl mr-3">💡</span>
            <div>
              <h4 class="font-semibold text-orange-800">Recomendación</h4>
              <p class="text-orange-700 text-sm">{{ predictions.disease.recommendation || 'Monitorear condiciones de humedad.' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Métricas de los Modelos -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">📈 Métricas de los Modelos</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <!-- Modelo Heladas -->
        <div>
          <h3 class="font-medium text-gray-700 mb-3">Modelo Heladas (XGBoost)</h3>
          <div class="space-y-2">
            <MetricBar label="Accuracy" :value="91" color="blue" />
            <MetricBar label="Precision" :value="87" color="green" />
            <MetricBar label="Recall" :value="93" color="purple" />
            <MetricBar label="F1-Score" :value="90" color="orange" />
            <MetricBar label="AUC-ROC" :value="95" color="pink" />
          </div>
        </div>
        <!-- Modelo Enfermedades -->
        <div>
          <h3 class="font-medium text-gray-700 mb-3">Modelo Enfermedades (Random Forest)</h3>
          <div class="space-y-2">
            <MetricBar label="Accuracy" :value="99" color="blue" />
            <MetricBar label="Precision" :value="98" color="green" />
            <MetricBar label="Recall" :value="99" color="purple" />
            <MetricBar label="F1-Score" :value="98.5" color="orange" />
          </div>
        </div>
      </div>
      <p class="text-xs text-gray-400 mt-4 text-center">
        ⚠️ Modelos entrenados con datos sintéticos. Validación en campo requerida.
      </p>
    </div>
  </div>
</template>

<script>
import RiskIndicator from './RiskIndicator.vue'
import MetricBar from './MetricBar.vue'

export default {
  name: 'Predictions',
  components: {
    RiskIndicator,
    MetricBar
  },
  props: {
    predictions: {
      type: Object,
      required: true
    }
  },
  computed: {
    frostFactors() {
      return [
        { name: 'Cambio de presión (12h)', importance: 28 },
        { name: 'Diferencial térmico aire-suelo', importance: 22 },
        { name: 'Punto de rocío', importance: 18 },
        { name: 'Intensidad lumínica', importance: 12 },
        { name: 'Hora del día', importance: 10 },
        { name: 'Otros factores', importance: 10 }
      ]
    },
    diseaseConditions() {
      // En una implementación real, estos vendrían de los datos del sensor
      return {
        humidity: 75,
        temperature: 20,
        tempFavorable: true
      }
    }
  }
}
</script>
