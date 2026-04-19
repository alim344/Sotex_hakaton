<template>
  <div class="map-container">
    <div id="map"></div>
    
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>
    
    <div class="search-container">
      <input
        type="text"
        v-model="searchQuery"
        @input="searchStation"
        placeholder="🔍 Find stations (e.g., B5, G22, R2)..."
        class="search-input"
      />
      <button v-if="searchQuery" @click="clearSearch" class="clear-btn">✖</button>
      <div v-if="searchResults.length > 0 && searchQuery" class="search-results">
        <div
          v-for="result in searchResults"
          :key="result.id"
          @click="centerToStation(result)"
          class="search-result-item"
        >
          <span class="result-name">🏭 {{ result.name }}</span>
          <span class="result-id">{{ result.f11Count || 0 }} F11</span>
        </div>
        <div v-if="searchResults.length === 0 && searchQuery" class="no-results">
          No results for "{{ searchQuery }}"
        </div>
      </div>
    </div>
    
    <div class="stats-panel">
      <div class="stat">
        <span>📍 Total Stations:</span>
        <strong>{{ totalCount }}</strong>
      </div>
      <div class="legend">
        <div 
          class="legend-item" 
          :class="{ active: filterType === 'all' }"
          @click="setFilter('all')"
        >
          <span class="dot all"></span>
          <span>All Stations</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: filterType === 'substation' }"
          @click="setFilter('substation')"
        >
          <span class="dot red"></span>
          <span>Substations ({{ substationCount }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: filterType === 'transmission' }"
          @click="setFilter('transmission')"
        >
          <span class="dot blue"></span>
          <span>Transmission Stations ({{ transmissionCount }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import axios from 'axios'


delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function getColoredIcon(color) {
  return L.divIcon({
    html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    className: 'custom-marker',
    iconSize: [14, 14],
    popupAnchor: [0, -7]
  })
}

const loading = ref(true)
const filterType = ref('all')
const substationCount = ref(0)
const transmissionCount = ref(0)
const totalCount = ref(0)
const searchQuery = ref('')
const searchResults = ref([])

let leafletMap = null
let allSubstations = []
let allTransmissions = []
let allMarkers = []

function formatFeederList(feeders) {
  if (!feeders || feeders.length === 0) {
    return '<i>No Feeders11</i>'
  }
  
  let html = '<ul style="margin: 8px 0 0 18px; font-size: 11px; max-height: 150px; overflow-y: auto;">'
  feeders.forEach(f => {
    const feederId = f.id || f.Id || '?'
    const feederName = f.name || f.Name || f.feederName || 'Undefined'
    html += `<li style="margin: 3px 0;"><strong>${feederName}</strong> (ID: ${feederId})</li>`
  })
  html += '</ul>'
  
  return html
}

async function loadFeedersForStation(stationId) {
  try {
    const response = await axios.get(`http://localhost:8080/feeders/by-substation/${stationId}`)
    return response.data
  } catch (error) {
    console.warn(`No feeders found for station ${stationId}`)
    return []
  }
}

async function createPopupContent(station) {
  const feeders = await loadFeedersForStation(station.id)
  const feederListHtml = formatFeederList(feeders)
  
  return `
    <div style="min-width: 260px; max-width: 320px; padding: 5px;">
      <b style="color: #e94560; font-size: 14px;">${station.name}</b>
      <hr style="margin: 8px 0;">
      <div style="font-size: 12px; margin: 5px 0;">
        <strong>ID:</strong> ${station.id}
      </div>
        <div style="font-size: 12px; margin: 5px 0;">
              <strong>Type:</strong> Substations
            </div>
      <div style="font-size: 12px; margin: 5px 0;">
        <strong>Feeders11:</strong> ${feeders.length}
      </div>
      ${feeders.length > 0 ? `<hr style="margin: 8px 0;"><div style="font-size: 12px;"><strong>Feeders11 list:</strong>${feederListHtml}</div>` : ''}
    </div>
  `
}

function updateMapFilter() {
  allMarkers.forEach(item => {
    if (filterType.value === 'all') {
      item.marker.addTo(leafletMap)
    } else if (filterType.value === 'substation' && item.type === 'substation') {
      item.marker.addTo(leafletMap)
    } else if (filterType.value === 'transmission' && item.type === 'transmission') {
      item.marker.addTo(leafletMap)
    } else {
      leafletMap.removeLayer(item.marker)
    }
  })
}

function setFilter(type) {
  filterType.value = type
  updateMapFilter()
}

async function loadSubstations() {
  try {
    const response = await axios.get('http://localhost:8080/substations/all')
    allSubstations = response.data
    substationCount.value = allSubstations.length
    
    for (const station of allSubstations) {
      const marker = L.marker([station.latitude, station.longitude], { icon: getColoredIcon('#e94560') })
        .bindTooltip(station.name, { sticky: true, direction: 'top', offset: [0, -15] })
      
      marker.on('click', async () => {
        const popupContent = await createPopupContent(station)
        marker.bindPopup(popupContent).openPopup()
      })
      
      allMarkers.push({ marker, station, type: 'substation' })
    }
    
    console.log(`✅ Loaded ${allSubstations.length} srednjenaponskih stanica`)
    
  } catch (error) {
    console.error('❌ Error:', error)
  }
}


async function loadTransmissionStations() {
  try {
    const response = await axios.get('http://localhost:8080/transmission-stations/all')
    allTransmissions = response.data
    transmissionCount.value = allTransmissions.length
    
    allTransmissions.forEach(station => {
      const marker = L.marker([station.latitude, station.longitude], { icon: getColoredIcon('#3b82f6') })
        .bindTooltip(station.name, { sticky: true, direction: 'top', offset: [0, -15] })
        .bindPopup(`
          <div style="min-width: 200px; padding: 5px;">
            <b style="color: #3b82f6; font-size: 14px;">${station.name}</b>
            <hr style="margin: 8px 0;">
            <div style="font-size: 12px; margin: 5px 0;">
              <strong>ID:</strong> ${station.id}
            </div>
            <div style="font-size: 12px; margin: 5px 0;">
              <strong>Type:</strong> Transmission Stations
            </div>
          </div>
        `)
      
      allMarkers.push({ marker, station, type: 'transmission' })
    })
    
    console.log(`✅ Loaded ${allTransmissions.length} visokonaponskih stanica`)
    
  } catch (error) {
    console.error('❌ Error:', error)
  }
}

function searchStation() {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) {
    searchResults.value = []
    return
  }
  
  const allStations = [
    ...allSubstations.map(s => ({ ...s, type: 'substation' })),
    ...allTransmissions.map(s => ({ ...s, type: 'transmission' }))
  ]
  
  searchResults.value = allStations.filter(station => 
    station.name.toLowerCase().includes(query)
  ).slice(0, 10)
}

function centerToStation(station) {
  leafletMap.setView([station.latitude, station.longitude], 14)
  
  const found = allMarkers.find(m => m.station.id === station.id && m.station.name === station.name)
  if (found) {
    if (station.type === 'substation') {
      createPopupContent(station).then(popupContent => {
        found.marker.bindPopup(popupContent).openPopup()
      })
    } else {
      found.marker.openPopup()
    }
  }
  
  searchQuery.value = ''
  searchResults.value = []
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
}

onMounted(async () => {
  leafletMap = L.map('map').setView([9.08, 7.49], 12)
  
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CartoDB',
    subdomains: 'abcd',
    maxZoom: 18,
    minZoom: 6
  }).addTo(leafletMap)
  
  L.control.zoom({ position: 'topright' }).addTo(leafletMap)
  
  await loadSubstations()
  await loadTransmissionStations()
  
  totalCount.value = substationCount.value + transmissionCount.value
  
  allMarkers.forEach(item => {
    item.marker.addTo(leafletMap)
  })
  
  loading.value = false
})
</script>

<style scoped>
.map-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}

#map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #e8e8e8;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 18px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.search-container {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 320px;
}

.search-input {
  width: 100%;
  padding: 10px 35px 10px 15px;
  font-size: 14px;
  border: 2px solid #e94560;
  border-radius: 30px;
  outline: none;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #999;
}

.search-results {
  position: absolute;
  top: 45px;
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 250px;
  overflow-y: auto;
  z-index: 1001;
}

.search-result-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
}

.search-result-item:hover {
  background: #f5f5f5;
}

.result-name {
  font-weight: 500;
  color: #333;
}

.result-id {
  font-size: 12px;
  color: #999;
}

.no-results {
  padding: 10px 15px;
  text-align: center;
  color: #999;
}

.stats-panel {
  position: absolute;
  bottom: 70px;
  left: 30px;
  background: rgba(26, 26, 46, 0.9);
  backdrop-filter: blur(8px);
  color: white;
  padding: 12px 18px;
  border-radius: 10px;
  min-width: 200px;
  z-index: 1000;
  border-left: 3px solid #e94560;
}

.stats-panel h3 {
  color: #e94560;
  margin-bottom: 8px;
  font-size: 13px;
}

.stat {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
  font-size: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.legend {
  margin-top: 5px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 6px 0;
  font-size: 11px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.legend-item:hover {
  background: rgba(255,255,255,0.1);
}

.legend-item.active {
  background: rgba(233, 69, 96, 0.2);
  border-left: 2px solid #e94560;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.dot.red {
  background-color: #e94560;
}

.dot.blue {
  background-color: #3b82f6;
}

.dot.all {
  background: linear-gradient(135deg, #e94560 50%, #3b82f6 50%);
}
</style>