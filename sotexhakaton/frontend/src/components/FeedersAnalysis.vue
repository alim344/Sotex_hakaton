<template>
  <div class="feeders-container">


    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="feeders-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Status</th>
            <th>Risk</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="feeder in feeders" :key="feeder.id">
            <td>{{ feeder.id }}</td>
            <td class="feeder-name">{{ feeder.name }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(feeder.status)">
                {{ feeder.status || '—' }}
              </span>
            </td>
            <td>
              <div class="risk-bar-container">
                <div class="risk-bar" :style="{ width: (feeder.riskScore || 0) * 100 + '%', background: getRiskColor(feeder.riskScore) }"></div>
                <span>{{ ((feeder.riskScore || 0) * 100).toFixed(0) }}%</span>
              </div>
            </td>
            <td>
              <button class="analyze-btn" @click="analyzeFeeder(feeder)" :disabled="analyzingId === feeder.id">
                {{ analyzingId === feeder.id ? '...' : 'Analyze' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Simple modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedFeeder?.name }}</h3>
          <button class="close-btn" @click="closeModal">✖</button>
        </div>
        <div class="modal-body">
          <div v-if="analysisResult">
            <p><strong>Status:</strong> {{ analysisResult.status }}</p>
            <p><strong>Risk Score:</strong> {{ ((analysisResult.risk_score || 0) * 100).toFixed(0) }}%</p>
            <p><strong>Anomalies:</strong> {{ analysisResult.anomaly_count || 0 }}</p>
            <p><strong>Data Gaps:</strong> {{ analysisResult.total_outages || 0 }}</p>
          </div>
          <div v-else class="modal-loading">
            <div class="spinner-small"></div>
            <p>Loading analysis...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const feeders = ref([])
const loading = ref(false)
const scanning = ref(false)
const analyzingId = ref(null)
const showModal = ref(false)
const selectedFeeder = ref(null)
const analysisResult = ref(null)

async function loadFeeders() {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8001/feeders')
    feeders.value = response.data.map(f => ({
      id: f.Id,
      name: f.Name,
      status: '—',
      riskScore: 0
    }))
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

async function scanNetwork() {
  scanning.value = true
  try {
    const response = await axios.post('http://localhost:8001/network/scan', {
      hours: 168,
      top_n: 100
    })
    
    const scanResults = response.data.feeders || []
    feeders.value = feeders.value.map(f => {
      const scan = scanResults.find(s => s.feeder11_id === f.id)
      if (scan) {
        return {
          ...f,
          status: scan.status,
          riskScore: scan.risk_score
        }
      }
      return f
    })
  } catch (error) {
    console.error('Scan error:', error)
  } finally {
    scanning.value = false
  }
}

async function analyzeFeeder(feeder) {
  analyzingId.value = feeder.id
  selectedFeeder.value = feeder
  showModal.value = true
  analysisResult.value = null

  try {
    const response = await axios.post('http://localhost:8001/analyze', {
      feeder11_id: feeder.id,
      hours: 168
    })
    analysisResult.value = response.data
    
    // Ažuriraj tabelu
    feeder.status = response.data.status
    feeder.riskScore = response.data.risk_score
    
  } catch (error) {
    console.error('Analysis error:', error)
    analysisResult.value = { error: 'Failed to load analysis' }
  } finally {
    analyzingId.value = null
  }
}

function closeModal() {
  showModal.value = false
  selectedFeeder.value = null
  analysisResult.value = null
}

function getStatusClass(status) {
  if (status === 'CRITICAL') return 'status-critical'
  if (status === 'WARNING') return 'status-warning'
  return 'status-ok'
}

function getRiskColor(risk) {
  if (risk >= 0.65) return '#e94560'
  if (risk >= 0.35) return '#ffa500'
  return '#22c55e'
}

onMounted(() => {
  loadFeeders()
})
</script>

<style scoped>
.feeders-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  overflow-y: auto;
  padding: 80px 20px 20px 20px;
}

.feeders-header {
  text-align: center;
  margin-bottom: 25px;
}

.feeders-header h1 {
  color: white;
  font-size: 1.5rem;
}

.feeders-header p {
  color: rgba(255,255,255,0.5);
  font-size: 0.8rem;
  margin-bottom: 15px;
}

.scan-btn {
  background: #e94560;
  border: none;
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.8rem;
}

.scan-btn:hover {
  background: #c92a4a;
}

.table-wrapper {
  overflow-x: auto;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
}

.feeders-table {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

.feeders-table th,
.feeders-table td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  font-size: 0.8rem;
}

.feeders-table th {
  background: rgba(0,0,0,0.3);
  font-weight: 600;
}

.feeder-name {
  max-width: 250px;
  white-space: nowrap;
  overflow-x: auto;
}

.risk-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-bar {
  width: 50px;
  height: 6px;
  border-radius: 3px;
}

.analyze-btn {
  background: rgba(233,69,96,0.2);
  border: 1px solid #e94560;
  color: #e94560;
  padding: 4px 10px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.7rem;
}

.analyze-btn:hover {
  background: #e94560;
  color: white;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
}

.status-critical { background: rgba(233,69,96,0.2); color: #e94560; }
.status-warning { background: rgba(255,165,0,0.2); color: #ffa500; }
.status-ok { background: rgba(34,197,94,0.2); color: #22c55e; }

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: #1a1a2e;
  border-radius: 12px;
  width: 350px;
  border: 1px solid #e94560;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.modal-header h3 {
  color: white;
  font-size: 1rem;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 1.2rem;
  cursor: pointer;
}

.modal-body {
  padding: 15px;
}

.modal-body p {
  color: white;
  margin: 8px 0;
  font-size: 0.85rem;
}

.modal-loading {
  text-align: center;
  padding: 20px;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(233,69,96,0.2);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(233,69,96,0.2);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: white;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .feeders-container {
    padding: 70px 10px 10px 10px;
  }
  
  .feeder-name {
    max-width: 120px;
  }
  
  .feeders-table th,
  .feeders-table td {
    font-size: 0.7rem;
    padding: 8px 5px;
  }
}
</style>