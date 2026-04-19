<template>
  <div class="monitor-container">

    <div class="monitor-header">
   
    </div>

    <div class="selector-section">
      <div class="selector-card">
        <div class="selector-header">
          <label>Select F11 feeder</label>
        </div>
        <div class="selector-wrapper">
          <select v-model="selectedFeederId" @change="fetchHistory" class="feeder-select">
            <option value="" disabled selected>— Select F11 feeder —</option>
            <option v-for="feeder in feeders" :key="feeder.id" :value="feeder.id">
              {{ feeder.name }} (ID: {{ feeder.id }})
            </option>
          </select>
          <div class="select-arrow">▼</div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading data...</p>
    </div>

    <div v-else-if="dailyData.length > 0" class="content">
      <div class="days-grid">
        <div 
          v-for="day in dailyData" 
          :key="day.date" 
          class="day-card"
          :class="getDayCardClass(day)"
        >
          <div class="day-header">
            <span class="day-date">{{ day.date }}</span>
            <div class="day-status-dot" :class="getStatusDot(day.status)"></div>
          </div>
          
          <div class="day-stats">
            <div class="day-stat">
              <div class="stat-info">
                <span class="stat-label">Max</span>
                <span class="stat-value" :class="getLoadClass(day.maxLoad)">
                  {{ day.maxLoad }}%
                </span>
              </div>
            </div>

            <div class="day-stat">
              <div class="stat-info">
                <span class="stat-label">Missing</span>
                <span class="stat-value">{{ day.missingCount }}</span>
              </div>
            </div>
            <div class="day-stat">
              <div class="stat-info">
                <span class="stat-label">Status</span>
                <span class="status-badge" :class="getStatusClass(day.status)">
                  {{ getStatusIcon(day.status) }} {{ day.status }}
                </span>
              </div>
            </div>
          </div>

          <div class="load-bar-container">
            <div class="load-bar-header">
              <span class="load-bar-label">Maximum load</span>
              <span class="load-bar-value">{{ day.maxLoad }}%</span>
            </div>
            <div class="load-bar">
              <div 
                class="load-fill" 
                :style="{ width: Math.min(day.maxLoad, 135) + '%', background: getLoadGradient(day.maxLoad) }"
              ></div>
            </div>
          </div>

          <div class="hours-section">
            <div class="halfhours-grid">
              <div 
                v-for="slot in day.halfHours" 
                :key="slot.slot"
                class="hour-slot"
                :class="slot.isMissing ? 'hour-missing' : getHourClass(slot.load)"
                :title="slot.isMissing ? `Missing measurement at ${slot.timeLabel}` : `${slot.timeLabel} - ${slot.load}%`"
              >
                <span class="hour-label">{{ slot.hour }}h<span class="minute">{{ slot.minute === 30 ? '30' : '' }}</span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary statistics -->
      <div class="summary-card">
        <div class="summary-header">
          <h3> Summary Statistics (3 days)</h3>
        </div>
        <div class="summary-stats">
          <div class="summary-stat">
            <div class="stat-content">
              <span class="summary-label">Peak load</span>
              <span class="summary-value" :class="getLoadClass(overallStats.absoluteMax)">
                {{ overallStats.absoluteMax }}%
              </span>
            </div>
          </div>
          <div class="summary-stat">
            <div class="stat-content">
              <span class="summary-label">Overloads</span>
              <span class="summary-value">{{ overallStats.totalOverloads }}</span>
            </div>
          </div>
          <div class="summary-stat">
            <div class="stat-content">
              <span class="summary-label">Stressed periods</span>
              <span class="summary-value">{{ overallStats.totalStressed }}</span>
            </div>
          </div>
          <div class="summary-stat">
            <div class="stat-content">
              <span class="summary-label">Missing readings</span>
              <span class="summary-value">{{ overallStats.totalMissing }}</span>
            </div>
          </div>
          <div class="summary-stat">
            <div class="stat-content">
              <span class="summary-label">Average load</span>
              <span class="summary-value">{{ overallStats.avgOverall }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading && selectedFeederId" class="no-data">
      <div class="no-data-icon">📭</div>
      <h3>No data available</h3>
      <p>No measurements found for the selected feeder in the last 3 days.</p>
    </div>

    <div v-else class="welcome-state">
      <div class="welcome-icon">⚡</div>
      <h2>Select an F11 feeder to analyze</h2>
      <p>Overload detection monitoring system</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const selectedFeederId = ref('')
const feeders = ref([])
const dailyData = ref([])
const loading = ref(false)

const overallStats = ref({
  absoluteMax: 0,
  totalOverloads: 0,
  totalStressed: 0,
  totalMissing: 0,
  avgOverall: 0
})

async function loadFeeders() {
  try {
    const response = await axios.get('http://localhost:8080/feeders/all')
    feeders.value = response.data
    console.log(`✅ Loaded ${feeders.value.length} feeders`)
  } catch (error) {
    console.error('Error loading feeders:', error)
  }
}

function generateDayData(date, baseLoad) {
  const halfHours = []
  let maxLoad = 0
  let totalLoad = 0
  let overloadCount = 0
  let stressedCount = 0
  let missingCount = 0
  
  for (let slot = 0; slot < 48; slot++) {
    const hour = Math.floor(slot / 2)
    const minute = (slot % 2) * 30
    const hourOfDay = hour + minute / 60
    
    const isMissing = Math.random() < 0.05
    
    let dailyFactor = 0.7
    if (hourOfDay >= 8 && hourOfDay <= 17) dailyFactor = 1.2
    if (hourOfDay >= 18 && hourOfDay <= 21) dailyFactor = 1.1
    
    let loadPercent = baseLoad * dailyFactor * (0.85 + Math.random() * 0.3)
    
    if (Math.random() < 0.08 && hour >= 10 && hour <= 18) {
      loadPercent = 105 + Math.random() * 25
    }
    
    loadPercent = Math.min(loadPercent, 135)
    loadPercent = Math.round(loadPercent)
    
    const finalLoad = isMissing ? -1 : loadPercent
    
    halfHours.push({ 
      slot, 
      hour, 
      minute, 
      load: finalLoad,
      isMissing: isMissing,
      timeLabel: `${hour.toString().padStart(2,'0')}:${minute.toString().padStart(2,'0')}`
    })
    
    if (!isMissing) {
      if (loadPercent > maxLoad) maxLoad = loadPercent
      totalLoad += loadPercent
      if (loadPercent >= 100) overloadCount++
      else if (loadPercent >= 80) stressedCount++
    } else {
      missingCount++
    }
  }
  
  const validCount = 48 - missingCount
  const avgLoad = validCount > 0 ? Math.round(totalLoad / validCount) : 0
  
  let status = 'NORMAL'
  if (overloadCount > 6) status = 'OVERLOAD'
  else if (stressedCount > 10) status = 'STRESSED'
  else if (overloadCount > 0) status = 'WARNING'
  
  return { halfHours, maxLoad, avgLoad, overloadCount, stressedCount, missingCount, status }
}

function generateAllDays(feederId) {
  const now = new Date()
  const seed = feederId % 3
  const baseLoads = [45, 60, 75]
  const baseLoad = baseLoads[seed]
  
  const days = []
  
  let totalMax = 0
  let totalOverloads = 0
  let totalStressed = 0
  let totalMissing = 0
  let totalAvgSum = 0
  
  for (let i = 2; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(now.getDate() - i)
    date.setHours(0, 0, 0, 0)
    
    const dayVariation = i === 0 ? 1.0 : (i === 1 ? 0.95 : 0.9)
    const dayData = generateDayData(date, baseLoad * dayVariation)
    
    days.push({
      date: date.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }),
      ...dayData
    })
    
    if (dayData.maxLoad > totalMax) totalMax = dayData.maxLoad
    totalOverloads += dayData.overloadCount
    totalStressed += dayData.stressedCount
    totalMissing += dayData.missingCount
    totalAvgSum += dayData.avgLoad
  }
  
  overallStats.value = {
    absoluteMax: totalMax,
    totalOverloads: totalOverloads,
    totalStressed: totalStressed,
    totalMissing: totalMissing,
    avgOverall: Math.round(totalAvgSum / 3)
  }
  
  return days
}

async function fetchHistory() {
  if (!selectedFeederId.value) return
  
  loading.value = true
  
  setTimeout(() => {
    dailyData.value = generateAllDays(selectedFeederId.value)
    loading.value = false
  }, 500)
}

function getLoadClass(load) {
  if (load >= 100) return 'load-danger'
  if (load >= 80) return 'load-warning'
  return 'load-normal'
}

function getLoadGradient(load) {
  if (load >= 100) return 'linear-gradient(90deg, #e94560, #ff6b81)'
  if (load >= 80) return 'linear-gradient(90deg, #ffa500, #ffc64a)'
  return 'linear-gradient(90deg, #22c55e, #4ade80)'
}

function getHourClass(load) {
  if (load >= 100) return 'hour-overload'
  if (load >= 80) return 'hour-stressed'
  return 'hour-normal'
}

function getDayCardClass(day) {
  if (day.status === 'OVERLOAD') return 'card-danger'
  if (day.status === 'STRESSED') return 'card-warning'
  if (day.status === 'WARNING') return 'card-warning-red'
  return 'card-normal'
}

function getStatusClass(status) {
  if (status === 'OVERLOAD') return 'status-overload'
  if (status === 'STRESSED') return 'status-stressed'
  if (status === 'WARNING') return 'status-warning-red'
  return 'status-normal'
}

function getStatusDot(status) {
  if (status === 'OVERLOAD') return 'dot-danger'
  if (status === 'STRESSED') return 'dot-warning'
  if (status === 'WARNING') return 'dot-warning-red'
  return 'dot-normal'
}

function getStatusIcon(status) {
  if (status === 'OVERLOAD') return '🔴'
  if (status === 'STRESSED') return '🟠'
  if (status === 'WARNING') return '🔴'
  return '🟢'
}

onMounted(() => {
  loadFeeders()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.monitor-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  overflow-y: auto;
  padding: 30px;
  font-family: 'Segoe UI', 'Poppins', sans-serif;
}

.monitor-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.header-title .icon {
  font-size: 2rem;
}

.monitor-header h1 {
  font-size: 1.8rem;
  background: linear-gradient(135deg, #fff, #e94560);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.badge {
  background: rgba(233, 69, 96, 0.2);
  color: #e94560;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid rgba(233, 69, 96, 0.3);
}

.header-subtitle {
  color: rgba(255,255,255,0.5);
  font-size: 0.85rem;
}

.selector-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.selector-card {
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  padding: 20px 30px;
  min-width: 400px;
  border: 1px solid rgba(255,255,255,0.1);
}

.selector-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.selector-icon {
  font-size: 1.1rem;
}

.selector-header label {
  color: white;
  font-weight: 500;
  font-size: 0.85rem;
}

.selector-wrapper {
  position: relative;
}

.feeder-select {
  width: 100%;
  padding: 12px 18px;
  font-size: 14px;
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  color: white;
  cursor: pointer;
  appearance: none;
}

.feeder-select:focus {
  outline: none;
  border-color: #e94560;
}

.feeder-select option {
  background: #1a1a2e;
  color: white;
}

.select-arrow {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #e94560;
  pointer-events: none;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin-bottom: 40px;
}

.day-card {
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  padding: 20px;
  border: 1px solid rgba(255,255,255,0.1);
  transition: transform 0.2s;
}

.day-card:hover {
  transform: translateY(-5px);
}

.card-danger { border-top: 3px solid #e94560; }
.card-warning { border-top: 3px solid #ffa500; }
.card-warning-red { border-top: 3px solid #e94560; }
.card-normal { border-top: 3px solid #22c55e; }

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.day-date {
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.day-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-danger { background: #e94560; }
.dot-warning { background: #ffa500; }
.dot-warning-red { background: #e94560; }
.dot-normal { background: #22c55e; }

.day-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.day-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,0,0,0.3);
  padding: 8px 10px;
  border-radius: 12px;
}

.stat-icon {
  font-size: 1.1rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.55rem;
  color: rgba(255,255,255,0.5);
}

.stat-value {
  font-size: 1rem;
  font-weight: 700;
  color: white;
}

.load-danger { color: #e94560; }
.load-warning { color: #ffa500; }
.load-normal { color: #22c55e; }

.load-bar-container {
  margin: 15px 0;
}

.load-bar-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.load-bar-label {
  font-size: 0.65rem;
  color: rgba(255,255,255,0.5);
}

.load-bar-value {
  font-size: 0.65rem;
  font-weight: 600;
  color: white;
}

.load-bar {
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  overflow: hidden;
}

.load-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s;
}

.hours-section {
  margin-top: 15px;
}

.halfhours-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 2px;
}

.hour-slot {
  aspect-ratio: 1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.1s;
}

.hour-slot:hover {
  transform: scale(1.1);
  z-index: 10;
}

.hour-label {
  font-size: 0.55rem;
  font-weight: 500;
  color: white;
  text-align: center;
  line-height: 1;
}

.minute {
  font-size: 0.45rem;
  opacity: 0.8;
  margin-left: 1px;
}

.hour-missing {
  background: repeating-linear-gradient(
    45deg,
    rgba(100,100,100,0.4),
    rgba(100,100,100,0.4) 4px,
    rgba(80,80,80,0.4) 4px,
    rgba(80,80,80,0.4) 8px
  );
  border: 1px dashed rgba(255,255,255,0.2);
}

.hour-missing .hour-label {
  opacity: 0.5;
}

.hour-overload { background: #e94560; }
.hour-stressed { background: #ffa500; }
.hour-normal { background: #22c55e; }

.summary-card {
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  padding: 20px;
  border: 1px solid rgba(255,255,255,0.1);
}

.summary-header {
  margin-bottom: 20px;
}

.summary-header h3 {
  color: white;
  font-size: 1rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 15px;
}

.summary-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.3);
  border-radius: 16px;
}

.stat-circle {
  width: 40px;
  height: 40px;
  background: rgba(233,69,96,0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-emoji {
  font-size: 1.1rem;
}

.stat-content {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 0.6rem;
  color: rgba(255,255,255,0.5);
  margin-bottom: 3px;
}

.summary-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.65rem;
  font-weight: 500;
}

.status-overload { background: rgba(233,69,96,0.2); color: #e94560; }
.status-stressed { background: rgba(255,165,0,0.2); color: #ffa500; }
.status-warning-red { background: rgba(233,69,96,0.2); color: #e94560; }
.status-normal { background: rgba(34,197,94,0.2); color: #22c55e; }

.loading-state {
  text-align: center;
  padding: 60px;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.welcome-state, .no-data {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon, .no-data-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.welcome-state h2, .no-data h3 {
  color: white;
  font-size: 1.3rem;
  margin-bottom: 10px;
}

.welcome-state p, .no-data p {
  color: rgba(255,255,255,0.5);
  font-size: 0.9rem;
}

@media (max-width: 1200px) {
  .days-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .selector-card {
    min-width: auto;
    width: 100%;
  }
}

@media (max-width: 768px) {
  .monitor-container {
    padding: 15px;
  }
  
  .header-title h1 {
    font-size: 1.3rem;
  }
  
  .day-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .halfhours-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}
</style>