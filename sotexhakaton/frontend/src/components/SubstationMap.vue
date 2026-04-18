<template>
  <div class="map-container">
    <!-- Search bar -->
    <div class="search-container">
      <input
        type="text"
        v-model="searchQuery"
        @input="searchStation"
        placeholder="🔍 Pretraži stanicu (npr. B5, G22, R2)..."
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
          <span class="result-id">ID: {{ result.id }}</span>
        </div>
      </div>
    </div>

    <div id="map"></div>
    
    <div class="stats-panel">
      <h3>⚡ Sotex Solutions</h3>
      <div class="stat">
        <span>📍 Stanice:</span>
        <strong>{{ stationCount }}</strong>
      </div>
      <div class="legend">
        <h4>📌 Legenda</h4>
        <div><span class="dot red"></span> Trafo stanice</div>
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

const stationCount = ref(0)
const searchQuery = ref('')
const searchResults = ref([])
let leafletMap = null
let allStations = []
let markers = []

async function loadSubstations() {
  try {
    console.log('📍 Učitavam stanice...')
    const response = await axios.get('http://localhost:8080/substations/all')
    allStations = response.data
    
    stationCount.value = allStations.length
    console.log(`✅ Učitano ${allStations.length} stanica`)
    
    if (allStations.length === 0) {
      console.warn('Nema stanica za prikaz')
      return
    }
    
    allStations.forEach(station => {
      const popupContent = `
        <div style="min-width: 180px; padding: 5px;">
          <b style="color: #e94560; font-size: 14px;">🏭 ${station.name}</b><br>
          <hr style="margin: 5px 0;">
          <table style="width: 100%; font-size: 12px;">
            <tr>
              <td style="padding: 2px 0;"><strong>ID:</strong></td>
              <td style="padding: 2px 0;">${station.id}</td>
            </tr>
            <tr>
              <td style="padding: 2px 0;"><strong>🔌 F11 izvoda:</strong></td>
              <td style="padding: 2px 0;">${station.f11Count || 0}</td>
            </tr>
            <tr>
              <td style="padding: 2px 0;"><strong>📍 Koordinate:</strong></td>
              <td style="padding: 2px 0;">${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}</td>
            </tr>
          </table>
        </div>
      `
      
      const marker = L.marker([station.latitude, station.longitude])
        .bindPopup(popupContent)
        .bindTooltip(station.name, { 
          sticky: true, 
          direction: 'top',
          offset: [0, -15]
        })
      
      marker.addTo(leafletMap)
      markers.push({ marker, station })
    })
    
    leafletMap.setView([9.08, 7.49], 9)
    
  } catch (error) {
    console.error('❌ Greška:', error)
  }
}

function searchStation() {
  const query = searchQuery.value.toLowerCase().trim()
  
  if (!query) {
    searchResults.value = []
    return
  }
  
  searchResults.value = allStations.filter(station => 
    station.name.toLowerCase().includes(query)
  ).slice(0, 10) 
}

function centerToStation(station) {

  leafletMap.setView([station.latitude, station.longitude], 15)
  
  const found = markers.find(m => m.station.id === station.id)
  if (found) {
    found.marker.openPopup()
  }
  

  searchQuery.value = ''
  searchResults.value = []
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
}

onMounted(() => {

  leafletMap = L.map('map').setView([9.08, 7.49], 9)
  

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CartoDB',
    subdomains: 'abcd',
    maxZoom: 18,
    minZoom: 6
  }).addTo(leafletMap)
  
  L.control.zoom({ position: 'topright' }).addTo(leafletMap)

  loadSubstations()
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100vh;
}

#map {
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
}


.search-container {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  font-size: 14px;
  border: 2px solid #e94560;
  border-radius: 25px;
  outline: none;
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  transition: all 0.3s;
}

.search-input:focus {
  border-color: #ff6b81;
  box-shadow: 0 2px 15px rgba(233,69,96,0.3);
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
  padding: 0 5px;
}

.clear-btn:hover {
  color: #e94560;
}

.search-results {
  position: absolute;
  top: 45px;
  left: 0;
  right: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1001;
}

.search-result-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
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

.stats-panel {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(26, 26, 46, 0.9);
  color: white;
  padding: 12px 18px;
  border-radius: 8px;
  min-width: 150px;
  backdrop-filter: blur(5px);
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  font-size: 14px;
}

.stats-panel h3 {
  color: #e94560;
  margin-bottom: 8px;
  font-size: 14px;
}

.stats-panel h4 {
  color: #aaa;
  margin-bottom: 6px;
  font-size: 11px;
}

.stat {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
}

.legend {
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px solid #333;
}

.legend div {
  display: flex;
  align-items: center;
  margin: 4px 0;
  font-size: 11px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.dot.red {
  background-color: #e94560;
  border: 1px solid white;
}


:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

:deep(.leaflet-popup-content) {
  margin: 8px 12px;
}
</style>