<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo">
          <span class="logo-icon">⚡</span>
          <span class="logo-text">Sotex Solutions</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link" active-class="active">
       
            Substations Map
          </router-link>
          <router-link to="/monitor" class="nav-link" active-class="active">
       
                Feeders
            </router-link>
            <router-link to="/feeders" class="nav-link" active-class="active">
   
            Feeders Analysis
            </router-link>
            <router-link to="/risk" class="nav-link" active-class="active">
     
              Risk Analysis
            </router-link>
            <router-link to="/forecast" class="nav-link" active-class="active">
            Forecast
          </router-link>
        </div>

      </div>
    </nav>

    <router-view />

  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: 'Segoe UI', 'Poppins', 'Inter', sans-serif;
}

#app {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.navbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  background: rgba(26, 26, 46, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(233, 69, 96, 0.3);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.6rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.6rem;
  animation: pulse 2s infinite;
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #e94560, #ff6b81);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.2rem;
  text-decoration: none;
  color: #e0e0e0;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.nav-link:hover {
  background: rgba(233, 69, 96, 0.15);
  color: #e94560;
}

.nav-link.active {
  background: linear-gradient(135deg, #e94560, #c92a4a);
  color: white;
}

.nav-icon {
  font-size: 1rem;
}

.nav-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.3rem 0.8rem;
  border-radius: 30px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-text {
  font-size: 0.7rem;
  color: #4ade80;
}


.footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  background: rgba(26, 26, 46, 0.7);
  backdrop-filter: blur(8px);
  color: #888;
  padding: 0.3rem 1rem;
  text-align: center;
  font-size: 0.65rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.footer-content p {
  margin: 0;
}


@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    padding: 0.5rem;
  }
  
  .logo-text {
    font-size: 1rem;
  }
  
  .nav-link {
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
  }
}
</style>