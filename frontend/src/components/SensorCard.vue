<template>
  <div 
    class="bg-gray-50 rounded-lg p-4 border-l-4 transition-all hover:shadow-md"
    :class="borderColor"
  >
    <div class="flex items-center justify-between mb-2">
      <span class="text-2xl">{{ icon }}</span>
      <span 
        class="w-2 h-2 rounded-full"
        :class="statusColor"
      ></span>
    </div>
    <div class="text-2xl font-bold text-gray-800">
      {{ formattedValue }}
      <span class="text-sm font-normal text-gray-500">{{ unit }}</span>
    </div>
    <div class="text-xs text-gray-500 mt-1">{{ title }}</div>
  </div>
</template>

<script>
export default {
  name: 'SensorCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      default: 0
    },
    unit: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: '📊'
    },
    status: {
      type: String,
      default: 'normal',
      validator: (value) => ['normal', 'warning', 'critical'].includes(value)
    }
  },
  computed: {
    formattedValue() {
      if (this.unit === 'lux') {
        return Math.round(this.value)
      }
      return this.value.toFixed(1)
    },
    statusColor() {
      const colors = {
        normal: 'bg-green-500',
        warning: 'bg-yellow-500',
        critical: 'bg-red-500'
      }
      return colors[this.status]
    },
    borderColor() {
      const colors = {
        normal: 'border-green-500',
        warning: 'border-yellow-500',
        critical: 'border-red-500'
      }
      return colors[this.status]
    }
  }
}
</script>
