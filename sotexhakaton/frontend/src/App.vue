<template>
  <div>
    <nav>
      <router-link to="/">Početna</router-link> |
      <router-link to="/dashboard">Dashboard</router-link> |
      <router-link to="/analysis">Analiza</router-link>
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
nav {
  padding: 20px;
  background-color: #f0f0f0;
  margin-bottom: 20px;
}
nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #333;
}
nav a.router-link-active {
  color: #42b983;
  font-weight: bold;
}
</style>