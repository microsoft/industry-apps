<script>
  import { onMount } from 'svelte';
  import Router from 'svelte-spa-router';
  import Sidebar from './lib/Sidebar.svelte';
  import OutputStream from './lib/OutputStream.svelte';
  import { loadConfig, loadModules, loadEnvironments, sidebarCollapsed } from './lib/stores.js';
  
  // Import route components
  import Deploy from './routes/Deploy.svelte';
  import FieldCreator from './routes/FieldCreator.svelte';
  
  // Define routes
  const routes = {
    '/': Deploy,
    '/field-creator': FieldCreator,
  };
  
  // Load initial data
  onMount(async () => {
    console.log('[App] Starting to load data...');
    try {
      await loadConfig();
      await loadModules();
      await loadEnvironments();
      console.log('[App] Data loaded successfully');
    } catch (error) {
      console.error('[App] Error loading data:', error);
    }
  });
</script>

<div class="app-container">
  <Sidebar />
  
  <main class="main-content" class:collapsed={$sidebarCollapsed}>
    <Router {routes} />
  </main>
  
  <!-- Global output stream modal -->
  <OutputStream />
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #1a1a1a;
    color: #e0e0e0;
    overflow: hidden;
  }

  :global(*) {
    box-sizing: border-box;
  }

  .app-container {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .main-content {
    flex: 1;
    margin-left: 240px;
    height: 100vh;
    overflow-y: auto;
    background: #1a1a1a;
    transition: margin-left 0.3s ease;
  }

  .main-content.collapsed {
    margin-left: 70px;
  }

  .main-content::-webkit-scrollbar {
    width: 10px;
  }

  .main-content::-webkit-scrollbar-track {
    background: #0d0d0d;
  }

  .main-content::-webkit-scrollbar-thumb {
    background: #3c3c3c;
    border-radius: 5px;
  }

  .main-content::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }

  :global(.btn) {
    padding: 0.625rem 1.25rem;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
  }

  :global(.btn:disabled) {
    opacity: 0.6;
    cursor: not-allowed;
  }

  :global(.btn-primary) {
    background-color: #0078d4;
    color: white;
  }

  :global(.btn-primary:hover:not(:disabled)) {
    background-color: #1a86e0;
  }

  :global(.btn-secondary) {
    background-color: #3c3c3c;
    color: #ffffff;
  }

  :global(.btn-secondary:hover:not(:disabled)) {
    background-color: #505050;
  }

  :global(.btn-success) {
    background-color: #4caf50;
    color: white;
  }

  :global(.btn-success:hover:not(:disabled)) {
    background-color: #5cb860;
  }

  :global(.btn-danger) {
    background-color: #f44336;
    color: white;
  }

  :global(.btn-danger:hover:not(:disabled)) {
    background-color: #f55545;
  }

  :global(.btn-text) {
    background: transparent;
    color: #0078d4;
    padding: 0.5rem 1rem;
  }

  :global(.btn-text:hover) {
    background-color: #3c3c3c;
  }
</style>
