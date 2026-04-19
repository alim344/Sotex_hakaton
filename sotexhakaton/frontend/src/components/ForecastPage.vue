<template>
  <div class="forecast-container">

    <!-- Selector -->
    <div class="selector-section">
      <div class="selector-card">
        <div class="selector-header">
          <label>Select F11 feeder</label>
        </div>
        <div class="selector-wrapper">
          <select v-model="selectedFeederId" class="feeder-select">
            <option value="" disabled>— Select F11 feeder —</option>
            <option v-for="f in feeders" :key="f.Id" :value="f.Id">
              {{ f.Name }} (ID: {{ f.Id }})
            </option>
          </select>
          <div class="select-arrow">▼</div>
        </div>

        <div class="controls-row">
          <div class="control-group">
            <label class="control-label">History (hours)</label>
            <div class="number-input-wrap">
              <input type="number" v-model.number="hours" min="24" max="8760" step="24" class="number-input" />
            </div>
          </div>
          <div class="control-group">
            <label class="control-label">Forecast horizon (hours)</label>
            <div class="number-input-wrap">
              <input type="number" v-model.number="horizonHours" min="1" max="168" class="number-input" />
            </div>
          </div>
          <button class="run-btn" @click="runForecast" :disabled="!selectedFeederId || loading">
            <span v-if="loading" class="btn-spinner"></span>
            <span v-else>▶ Run forecast</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">
      ⚠ {{ error }}
    </div>

    <!-- Welcome -->
    <div v-if="!result && !loading && !error" class="welcome-state">
      <div class="welcome-icon">📈</div>
      <h2>Select a feeder and run forecast</h2>
      <p>SARIMA model · 90% confidence interval · high load detection</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Running SARIMA model…</p>
    </div>

    <!-- Results -->
    <div v-if="result && !loading" class="results">

      <!-- KPI strip -->
      <div class="kpi-strip">
        <div class="kpi-card">
          <span class="kpi-label">Method</span>
          <span class="kpi-value method-badge">{{ result.method_used.toUpperCase() }}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Horizon</span>
          <span class="kpi-value">{{ result.horizon_hours }}h</span>
        </div>
        <div class="kpi-card" :class="peakClass">
          <span class="kpi-label">Predicted peak</span>
          <span class="kpi-value">{{ result.predicted_peak.toFixed(1) }} <small>kWh/h</small></span>
        </div>
        <div class="kpi-card" :class="result.high_load_windows.length > 0 ? 'kpi-warn' : 'kpi-ok'">
          <span class="kpi-label">High-load windows</span>
          <span class="kpi-value">{{ result.high_load_windows.length }}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Total intervals</span>
          <span class="kpi-value">{{ result.forecast_points.length }}</span>
        </div>
      </div>

      <!-- High-load windows -->
      <div v-if="result.high_load_windows.length > 0" class="windows-section">
        <h3 class="section-title">⚡ High-load windows</h3>
        <div class="windows-grid">
          <div v-for="(w, i) in result.high_load_windows" :key="i" class="window-chip">
            <span class="window-dot"></span>
            <span>{{ formatTs(w.start) }}</span>
            <span class="window-arrow">→</span>
            <span>{{ formatTs(w.end) }}</span>
          </div>
        </div>
      </div>

      <!-- Chart -->
      <div class="chart-section">
        <h3 class="section-title">Consumption forecast</h3>
        <div class="chart-wrap">
          <svg class="chart-svg" :viewBox="`0 0 ${svgW} ${svgH}`" preserveAspectRatio="none">
            <!-- Grid lines -->
            <line v-for="y in gridYs" :key="'g'+y"
              :x1="padL" :y1="y" :x2="svgW - padR" :y2="y"
              stroke="rgba(255,255,255,0.06)" stroke-width="1"/>

            <!-- Y axis labels -->
            <text v-for="(tick, i) in yTicks" :key="'yt'+i"
              :x="padL - 8" :y="gridYs[i] + 4"
              fill="rgba(255,255,255,0.4)" font-size="11" text-anchor="end">
              {{ tick }}
            </text>

            <!-- X axis labels (every 4h) -->
            <text v-for="(pt, i) in xLabelPoints" :key="'xl'+i"
              :x="pt.x" :y="svgH - padB + 16"
              fill="rgba(255,255,255,0.4)" font-size="10" text-anchor="middle">
              {{ pt.label }}
            </text>

            <!-- CI band -->
            <polygon :points="ciPolygon" fill="rgba(233,69,96,0.12)"/>

            <!-- High-load zones -->
            <rect v-for="(z, i) in highLoadZones" :key="'z'+i"
              :x="z.x1" :y="padT" :width="z.x2 - z.x1" :height="chartH"
              fill="rgba(233,69,96,0.15)"/>

            <!-- Lower bound -->
            <polyline :points="lowerLine" fill="none"
              stroke="rgba(233,69,96,0.3)" stroke-width="1" stroke-dasharray="4 3"/>

            <!-- Upper bound -->
            <polyline :points="upperLine" fill="none"
              stroke="rgba(233,69,96,0.3)" stroke-width="1" stroke-dasharray="4 3"/>

            <!-- Main forecast line -->
            <polyline :points="forecastLine" fill="none"
              stroke="#e94560" stroke-width="2" stroke-linejoin="round"/>

            <!-- High-load dots -->
            <circle v-for="(pt, i) in highLoadDots" :key="'d'+i"
              :cx="pt.cx" :cy="pt.cy" r="3.5"
              fill="#e94560" stroke="#ff6b81" stroke-width="1.5"/>

            <!-- Hover tracking -->
            <rect
              :x="padL" :y="padT" :width="chartW" :height="chartH"
              fill="transparent"
              @mousemove="onMouseMove($event)"
              @mouseleave="hoveredIdx = null"/>

            <!-- Tooltip vertical line -->
            <line v-if="hoveredIdx !== null"
              :x1="hoverX" :y1="padT" :x2="hoverX" :y2="padT + chartH"
              stroke="rgba(255,255,255,0.3)" stroke-width="1" stroke-dasharray="3 2"/>
            <circle v-if="hoveredIdx !== null"
              :cx="hoverX" :cy="hoverY" r="5"
              fill="#e94560" stroke="white" stroke-width="2"/>
          </svg>

          <!-- Tooltip -->
          <div v-if="hoveredIdx !== null" class="chart-tooltip"
            :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }">
            <div class="tt-time">{{ formatTs(result.forecast_points[hoveredIdx].timestamp) }}</div>
            <div class="tt-row">
              <span>Predicted</span>
              <strong>{{ result.forecast_points[hoveredIdx].predicted_value.toFixed(1) }} kWh/h</strong>
            </div>
            <div class="tt-row">
              <span>CI low</span>
              <strong>{{ result.forecast_points[hoveredIdx].lower_bound.toFixed(1) }}</strong>
            </div>
            <div class="tt-row">
              <span>CI high</span>
              <strong>{{ result.forecast_points[hoveredIdx].upper_bound.toFixed(1) }}</strong>
            </div>
            <div v-if="result.forecast_points[hoveredIdx].is_high_load" class="tt-high">
              ⚡ High load
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="chart-legend">
          <div class="legend-item"><span class="leg-line solid"></span> Predicted</div>
          <div class="legend-item"><span class="leg-line dashed"></span> 90% CI</div>
          <div class="legend-item"><span class="leg-dot"></span> High load point</div>
          <div class="legend-item"><span class="leg-zone"></span> High load zone</div>
        </div>
      </div>

      <!-- Table -->
      <div class="table-section">
        <div class="table-header-row">
          <h3 class="section-title">Forecast table</h3>
          <span class="table-hint">Showing {{ result.forecast_points.length }} intervals</span>
        </div>
        <div class="table-wrap">
          <table class="forecast-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Timestamp</th>
                <th>Predicted (kWh/h)</th>
                <th>CI low</th>
                <th>CI high</th>
                <th>Load</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pt, i) in result.forecast_points" :key="i"
                :class="pt.is_high_load ? 'row-high' : ''">
                <td class="row-num">{{ i + 1 }}</td>
                <td>{{ formatTs(pt.timestamp) }}</td>
                <td class="val-cell">{{ pt.predicted_value.toFixed(1) }}</td>
                <td class="muted">{{ pt.lower_bound.toFixed(1) }}</td>
                <td class="muted">{{ pt.upper_bound.toFixed(1) }}</td>
                <td>
                  <span v-if="pt.is_high_load" class="high-badge">⚡ High</span>
                  <span v-else class="normal-badge">Normal</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://localhost:8001'

const feeders       = ref([])
const selectedFeederId = ref('')
const hours         = ref(168)
const horizonHours  = ref(24)
const loading       = ref(false)
const error         = ref(null)
const result        = ref(null)

// ── Chart geometry ────────────────────────────────────────────────────────────
const svgW  = 900
const svgH  = 280
const padL  = 56
const padR  = 20
const padT  = 20
const padB  = 30
const chartW = svgW - padL - padR
const chartH = svgH - padT - padB

const hoveredIdx = ref(null)
const hoverX     = ref(0)
const hoverY     = ref(0)
const tooltipX   = ref(0)
const tooltipY   = ref(0)

// ── Computed chart data ───────────────────────────────────────────────────────
const pts = computed(() => result.value?.forecast_points ?? [])

const yMin = computed(() => Math.max(0, Math.min(...pts.value.map(p => p.lower_bound)) * 0.95))
const yMax = computed(() => Math.max(...pts.value.map(p => p.upper_bound)) * 1.05 || 1)

function scaleX(i) {
  return padL + (i / (pts.value.length - 1 || 1)) * chartW
}
function scaleY(v) {
  return padT + chartH - ((v - yMin.value) / (yMax.value - yMin.value)) * chartH
}

const forecastLine = computed(() =>
  pts.value.map((p, i) => `${scaleX(i)},${scaleY(p.predicted_value)}`).join(' ')
)
const upperLine = computed(() =>
  pts.value.map((p, i) => `${scaleX(i)},${scaleY(p.upper_bound)}`).join(' ')
)
const lowerLine = computed(() =>
  pts.value.map((p, i) => `${scaleX(i)},${scaleY(p.lower_bound)}`).join(' ')
)
const ciPolygon = computed(() => {
  const top = pts.value.map((p, i) => `${scaleX(i)},${scaleY(p.upper_bound)}`).join(' ')
  const bot = [...pts.value].reverse().map((p, i) =>
    `${scaleX(pts.value.length - 1 - i)},${scaleY(p.lower_bound)}`).join(' ')
  return top + ' ' + bot
})

const highLoadDots = computed(() =>
  pts.value.flatMap((p, i) =>
    p.is_high_load ? [{ cx: scaleX(i), cy: scaleY(p.predicted_value) }] : []
  )
)

const highLoadZones = computed(() => {
  const zones = []
  let inZone = false, x1 = 0
  pts.value.forEach((p, i) => {
    const x = scaleX(i)
    if (p.is_high_load && !inZone) { inZone = true; x1 = x }
    if (!p.is_high_load && inZone) { inZone = false; zones.push({ x1, x2: x }) }
  })
  if (inZone) zones.push({ x1, x2: scaleX(pts.value.length - 1) })
  return zones
})

// Grid
const NUM_YTICKS = 5
const yTicks = computed(() => {
  const step = (yMax.value - yMin.value) / (NUM_YTICKS - 1)
  return Array.from({ length: NUM_YTICKS }, (_, i) => Math.round(yMin.value + step * i))
})
const gridYs = computed(() => yTicks.value.map(v => scaleY(v)))

// X labels every 4 intervals (2h)
const xLabelPoints = computed(() =>
  pts.value.reduce((acc, p, i) => {
    if (i % 8 === 0)
      acc.push({ x: scaleX(i), label: formatTs(p.timestamp, true) })
    return acc
  }, [])
)

// KPI class
const peakClass = computed(() => {
  if (!result.value) return ''
  const ratio = result.value.predicted_peak / (pts.value[0]?.upper_bound * 0.9 || 1)
  return ratio > 1 ? 'kpi-danger' : ratio > 0.75 ? 'kpi-warn' : 'kpi-ok'
})

// ── Mouse tracking ────────────────────────────────────────────────────────────
function onMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const svgRect = e.currentTarget.closest('svg').getBoundingClientRect()
  const relX = (e.clientX - svgRect.left) / svgRect.width * svgW
  const idx = Math.round((relX - padL) / chartW * (pts.value.length - 1))
  hoveredIdx.value = Math.max(0, Math.min(pts.value.length - 1, idx))
  hoverX.value = scaleX(hoveredIdx.value)
  hoverY.value = scaleY(pts.value[hoveredIdx.value].predicted_value)

  // Tooltip position relative to chart-wrap
  const wrapRect = e.currentTarget.closest('.chart-wrap').getBoundingClientRect()
  tooltipX.value = e.clientX - wrapRect.left + 14
  tooltipY.value = e.clientY - wrapRect.top - 40
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatTs(iso, short = false) {
  const d = new Date(iso)
  if (short) return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleString('en-GB', {
    day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

// ── API calls ─────────────────────────────────────────────────────────────────
async function loadFeeders() {
  try {
    const r = await axios.get(`${API}/feeders`)
    feeders.value = r.data
  } catch (e) {
    console.error('Could not load feeders', e)
  }
}

async function runForecast() {
  if (!selectedFeederId.value) return
  loading.value = true
  error.value = null
  result.value = null

  try {
    const r = await axios.post(`${API}/forecast`, {
      feeder11_id:  selectedFeederId.value,
      hours:        hours.value,
      horizon_hours: horizonHours.value
    })
    result.value = r.data
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Server error — check that the Python API is running.'
  } finally {
    loading.value = false
  }
}

onMounted(loadFeeders)
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.forecast-container {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  overflow-y: auto;
  padding: 30px;
  font-family: 'Segoe UI', 'Poppins', sans-serif;
  color: white;
}

/* ── Selector ── */
.selector-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.selector-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 20px 28px;
  width: 100%;
  max-width: 860px;
}

.selector-header { margin-bottom: 12px; }
.selector-header label { color: white; font-weight: 500; font-size: 0.85rem; }

.selector-wrapper { position: relative; margin-bottom: 18px; }

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
.feeder-select:focus { outline: none; border-color: #e94560; }
.feeder-select option { background: #1a1a2e; color: white; }
.select-arrow {
  position: absolute; right: 15px; top: 50%;
  transform: translateY(-50%);
  color: #e94560; pointer-events: none;
}

.controls-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.control-group { display: flex; flex-direction: column; gap: 6px; }
.control-label { font-size: 0.72rem; color: rgba(255,255,255,0.5); }

.number-input-wrap { position: relative; }
.number-input {
  width: 150px;
  padding: 10px 14px;
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  color: white;
  font-size: 14px;
}
.number-input:focus { outline: none; border-color: #e94560; }
.number-input::-webkit-inner-spin-button { opacity: 0.4; }

.run-btn {
  padding: 10px 28px;
  background: #e94560;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
  height: 42px;
}
.run-btn:hover:not(:disabled) { background: #c92a4a; }
.run-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

/* ── States ── */
.welcome-state, .loading-state {
  text-align: center;
  padding: 80px 20px;
}
.welcome-icon { font-size: 4rem; margin-bottom: 20px; }
.welcome-state h2 { color: white; font-size: 1.3rem; margin-bottom: 10px; }
.welcome-state p  { color: rgba(255,255,255,0.4); font-size: 0.85rem; }

.spinner {
  width: 44px; height: 44px;
  border: 3px solid rgba(233,69,96,0.2);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
.loading-state p { color: rgba(255,255,255,0.5); font-size: 0.9rem; }

.error-banner {
  max-width: 860px;
  margin: 0 auto 20px;
  padding: 14px 20px;
  background: rgba(233,69,96,0.15);
  border: 1px solid rgba(233,69,96,0.4);
  border-radius: 12px;
  color: #ff8a9a;
  font-size: 0.85rem;
}

/* ── Results ── */
.results { max-width: 960px; margin: 0 auto; }

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
  margin-bottom: 14px;
}

/* KPI strip */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.kpi-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-label { font-size: 0.65rem; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 1.25rem; font-weight: 700; color: white; }
.kpi-value small { font-size: 0.65rem; font-weight: 400; color: rgba(255,255,255,0.5); }

.kpi-danger { border-color: rgba(233,69,96,0.5); }
.kpi-danger .kpi-value { color: #e94560; }
.kpi-warn   { border-color: rgba(255,165,0,0.4); }
.kpi-warn   .kpi-value { color: #ffa500; }
.kpi-ok     { border-color: rgba(34,197,94,0.4); }
.kpi-ok     .kpi-value { color: #22c55e; }

.method-badge {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #e94560;
}

/* High-load windows */
.windows-section { margin-bottom: 24px; }
.windows-grid { display: flex; flex-wrap: wrap; gap: 8px; }

.window-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(233,69,96,0.12);
  border: 1px solid rgba(233,69,96,0.35);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 0.78rem;
  color: #ff8a9a;
}
.window-dot {
  width: 6px; height: 6px;
  background: #e94560;
  border-radius: 50%;
}
.window-arrow { opacity: 0.5; }

/* Chart */
.chart-section {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 20px;
  margin-bottom: 24px;
}

.chart-wrap {
  position: relative;
  width: 100%;
}

.chart-svg {
  width: 100%;
  height: 260px;
  display: block;
}

.chart-tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(15,12,41,0.95);
  border: 1px solid rgba(233,69,96,0.4);
  border-radius: 10px;
  padding: 10px 14px;
  min-width: 160px;
  z-index: 10;
}
.tt-time { font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-bottom: 6px; }
.tt-row  { display: flex; justify-content: space-between; gap: 16px; font-size: 0.78rem; color: rgba(255,255,255,0.7); margin: 2px 0; }
.tt-row strong { color: white; }
.tt-high { margin-top: 6px; font-size: 0.72rem; color: #e94560; font-weight: 600; }

.chart-legend {
  display: flex;
  gap: 20px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.legend-item { display: flex; align-items: center; gap: 7px; font-size: 0.72rem; color: rgba(255,255,255,0.45); }
.leg-line { display: inline-block; width: 22px; height: 2px; background: #e94560; }
.leg-line.dashed { background: none; border-top: 2px dashed rgba(233,69,96,0.5); }
.leg-dot { width: 8px; height: 8px; border-radius: 50%; background: #e94560; flex-shrink: 0; }
.leg-zone { width: 16px; height: 12px; background: rgba(233,69,96,0.2); border: 1px solid rgba(233,69,96,0.3); border-radius: 3px; flex-shrink: 0; }

/* Table */
.table-section {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 20px;
  margin-bottom: 40px;
}

.table-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.table-hint { font-size: 0.72rem; color: rgba(255,255,255,0.35); }

.table-wrap { overflow-x: auto; }

.forecast-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}
.forecast-table th {
  padding: 8px 12px;
  text-align: left;
  color: rgba(255,255,255,0.4);
  font-weight: 500;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.forecast-table td {
  padding: 7px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.8);
}
.forecast-table tr:hover td { background: rgba(255,255,255,0.03); }

.row-high td { background: rgba(233,69,96,0.07); }
.row-high:hover td { background: rgba(233,69,96,0.12) !important; }

.row-num { color: rgba(255,255,255,0.25); font-size: 0.7rem; }
.val-cell { font-weight: 600; color: white; }
.muted { color: rgba(255,255,255,0.4); }

.high-badge {
  display: inline-block;
  padding: 2px 9px;
  background: rgba(233,69,96,0.2);
  border: 1px solid rgba(233,69,96,0.4);
  border-radius: 20px;
  color: #e94560;
  font-size: 0.7rem;
  font-weight: 600;
}
.normal-badge {
  display: inline-block;
  padding: 2px 9px;
  background: rgba(34,197,94,0.1);
  border: 1px solid rgba(34,197,94,0.25);
  border-radius: 20px;
  color: #22c55e;
  font-size: 0.7rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .kpi-strip { grid-template-columns: repeat(3, 1fr); }
  .controls-row { flex-direction: column; align-items: stretch; }
  .number-input { width: 100%; }
  .run-btn { width: 100%; justify-content: center; }
}

@media (max-width: 600px) {
  .forecast-container { padding: 16px; }
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
}
</style>