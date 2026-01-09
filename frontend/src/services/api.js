/**
 * SMART GROW - API Service
 * Cliente para comunicación con el backend FastAPI
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error)
      throw error
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SENSORES
  // ═══════════════════════════════════════════════════════════════════════════

  async getLatestSensorData() {
    try {
      return await this.request('/api/v1/sensors/latest')
    } catch (error) {
      // Devolver datos de ejemplo si el API no está disponible
      return {
        temperature: 22.5,
        humidity: 65,
        soil_humidity: 55,
        soil_temp: 18.5,
        light: 12500,
        pressure: 1013.2,
        rssi: -72,
        snr: 9.5,
        timestamp: new Date().toISOString()
      }
    }
  }

  async getSensorHistory(hours = 24, aggregation = '10m') {
    return await this.request(`/api/v1/sensors/history?hours=${hours}&aggregation=${aggregation}`)
  }

  async getSensorStats(hours = 24) {
    return await this.request(`/api/v1/sensors/stats?hours=${hours}`)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // PREDICCIONES
  // ═══════════════════════════════════════════════════════════════════════════

  async getFrostPrediction() {
    try {
      return await this.request('/api/v1/predictions/frost')
    } catch (error) {
      return {
        probability: 15,
        risk_level: 'low',
        confidence: 87,
        hours_ahead: 12,
        contributing_factors: ['Temperatura estable', 'Presión normal'],
        recommendation: 'Condiciones normales. No se requieren medidas preventivas.'
      }
    }
  }

  async getDiseasePrediction() {
    try {
      return await this.request('/api/v1/predictions/disease')
    } catch (error) {
      return {
        probability: 25,
        risk_level: 'low',
        favorable_conditions: false,
        recommendation: 'Condiciones no favorables para enfermedades fúngicas.'
      }
    }
  }

  async getFeatureImportance(model = 'frost') {
    return await this.request(`/api/v1/predictions/features/importance?model=${model}`)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // ALERTAS
  // ═══════════════════════════════════════════════════════════════════════════

  async getActiveAlerts() {
    try {
      return await this.request('/api/v1/alerts/active')
    } catch (error) {
      return []
    }
  }

  async getAlertHistory(hours = 24) {
    return await this.request(`/api/v1/alerts/history?hours=${hours}`)
  }

  async acknowledgeAlert(alertId) {
    return await this.request(`/api/v1/alerts/${alertId}/acknowledge`, {
      method: 'POST'
    })
  }

  async getAlertConfig() {
    return await this.request('/api/v1/alerts/config')
  }

  async updateAlertConfig(alertType, config) {
    return await this.request(`/api/v1/alerts/config/${alertType}`, {
      method: 'PUT',
      body: JSON.stringify(config)
    })
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SISTEMA
  // ═══════════════════════════════════════════════════════════════════════════

  async getSystemStatus() {
    return await this.request('/api/v1/system/status')
  }

  async getSystemInfo() {
    return await this.request('/api/v1/system/info')
  }

  async getSystemMetrics() {
    return await this.request('/api/v1/system/metrics')
  }

  async healthCheck() {
    try {
      await this.request('/health')
      return true
    } catch {
      return false
    }
  }
}

export const apiService = new ApiService()
export default apiService
