<script>
  import { location } from 'svelte-spa-router';

  // Navigation items
  const navItems = [
    { path: '/', label: 'Deploy', icon: '🚀', description: 'Solution deployment' },
    { path: '/field-creator', label: 'Field Creator', icon: '📋', description: 'Mass create fields' },
  ];
</script>

<aside class="sidebar">
  <div class="sidebar-header">
    <h1 class="app-title">
      <span class="icon">🛠️</span>
      <span class="title-text">UI Tools</span>
    </h1>
    <p class="subtitle">Dataverse Solution Management</p>
  </div>

  <nav class="nav-menu">
    {#each navItems as item}
      <a 
        href="#{item.path}" 
        class="nav-item" 
        class:active={$location === item.path}
        title={item.description}
      >
        <span class="nav-icon">{item.icon}</span>
        <span class="nav-label">{item.label}</span>
      </a>
    {/each}
  </nav>

  <div class="sidebar-footer">
    <p class="version">v0.1.0</p>
  </div>
</aside>

<style>
  .sidebar {
    width: 240px;
    height: 100vh;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    color: #e2e8f0;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #334155;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
  }

  .sidebar-header {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #334155;
  }

  .app-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #f1f5f9;
  }

  .icon {
    font-size: 1.5rem;
  }

  .title-text {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    margin: 0.25rem 0 0 0;
    font-size: 0.75rem;
    color: #94a3b8;
    padding-left: 2rem;
  }

  .nav-menu {
    flex: 1;
    padding: 1rem 0.5rem;
    overflow-y: auto;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.25rem;
    border-radius: 0.5rem;
    text-decoration: none;
    color: #cbd5e1;
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
  }

  .nav-item:hover {
    background: rgba(59, 130, 246, 0.1);
    color: #f1f5f9;
    transform: translateX(4px);
  }

  .nav-item.active {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    color: #f1f5f9;
    font-weight: 600;
  }

  .nav-item.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 60%;
    background: linear-gradient(180deg, #60a5fa 0%, #a78bfa 100%);
    border-radius: 0 2px 2px 0;
  }

  .nav-icon {
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.5rem;
  }

  .nav-label {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .sidebar-footer {
    padding: 1rem;
    border-top: 1px solid #334155;
    text-align: center;
  }

  .version {
    margin: 0;
    font-size: 0.7rem;
    color: #64748b;
  }

  /* Scrollbar styling */
  .nav-menu::-webkit-scrollbar {
    width: 6px;
  }

  .nav-menu::-webkit-scrollbar-track {
    background: transparent;
  }

  .nav-menu::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
  }

  .nav-menu::-webkit-scrollbar-thumb:hover {
    background: #475569;
  }
</style>
