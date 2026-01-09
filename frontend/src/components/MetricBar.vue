<template>
  <div class="flex items-center">
    <span class="w-20 text-sm text-gray-600">{{ label }}</span>
    <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden mx-2">
      <div 
        class="h-full rounded-full transition-all duration-500"
        :class="colorClass"
        :style="{ width: value + '%' }"
      ></div>
    </div>
    <span class="w-12 text-sm font-medium text-gray-700 text-right">{{ value }}%</span>
  </div>
</template>

<script>
export default {
  name: 'MetricBar',
  props: {
    label: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      required: true
    },
    color: {
      type: String,
      default: 'blue'
    }
  },
  computed: {
    colorClass() {
      const colors = {
        blue: 'bg-blue-500',
        green: 'bg-green-500',
        purple: 'bg-purple-500',
        orange: 'bg-orange-500',
        pink: 'bg-pink-500',
        red: 'bg-red-500'
      }
      return colors[this.color] || 'bg-blue-500'
    }
  }
}
</script>
