<template>
  <div class="flex flex-col items-center">
    <!-- Círculo de progreso -->
    <div class="relative w-24 h-24">
      <svg class="w-full h-full transform -rotate-90">
        <!-- Fondo -->
        <circle
          cx="48"
          cy="48"
          r="40"
          stroke-width="8"
          fill="none"
          class="stroke-gray-200"
        />
        <!-- Progreso -->
        <circle
          cx="48"
          cy="48"
          r="40"
          stroke-width="8"
          fill="none"
          :stroke="strokeColor"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          stroke-linecap="round"
          class="transition-all duration-500"
        />
      </svg>
      <!-- Icono central -->
      <div class="absolute inset-0 flex items-center justify-center">
        <span class="text-3xl">{{ riskIcon }}</span>
      </div>
    </div>
    <!-- Etiqueta -->
    <div 
      class="mt-2 px-3 py-1 rounded-full text-sm font-medium uppercase"
      :class="labelClass"
    >
      {{ levelLabel }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'RiskIndicator',
  props: {
    level: {
      type: String,
      default: 'low',
      validator: (value) => ['low', 'medium', 'high'].includes(value)
    },
    probability: {
      type: Number,
      default: 0
    }
  },
  computed: {
    circumference() {
      return 2 * Math.PI * 40 // r = 40
    },
    dashOffset() {
      const progress = this.probability / 100
      return this.circumference * (1 - progress)
    },
    strokeColor() {
      const colors = {
        low: '#22c55e',     // green-500
        medium: '#eab308',  // yellow-500
        high: '#ef4444'     // red-500
      }
      return colors[this.level]
    },
    riskIcon() {
      const icons = {
        low: '✅',
        medium: '⚠️',
        high: '🚨'
      }
      return icons[this.level]
    },
    levelLabel() {
      const labels = {
        low: 'Bajo',
        medium: 'Medio',
        high: 'Alto'
      }
      return labels[this.level]
    },
    labelClass() {
      const classes = {
        low: 'bg-green-100 text-green-800',
        medium: 'bg-yellow-100 text-yellow-800',
        high: 'bg-red-100 text-red-800'
      }
      return classes[this.level]
    }
  }
}
</script>
