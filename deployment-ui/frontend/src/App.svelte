<script>
  import { onMount } from 'svelte';
  
  let modules = [];
  let tenants = [];
  let categories = new Set();
  let selectedCategory = 'all';
  let searchQuery = '';
  
  let draggedModule = null;
  let dragOverZone = null;
  
  let activeOperation = null;
  let operationStatus = '';
  let outputLines = [];
  
  let showCreateModuleDialog = false;
  let newModuleName = '';
  let newModuleCategory = '';
  let newModuleDeploy = false;
  
  onMount(async () => {
    await loadModules();
    await loadEnvironments();
  });
  
  async function loadModules() {
    try {
      const response = await fetch('/api/modules');
      if (!response.ok) {
        console.error('Failed to load modules:', response.status, response.statusText);
        return;
      }
      const data = await response.json();
      console.log('Loaded modules:', data);
      modules = data.modules || [];
      
      // Extract unique categories
      categories = new Set(modules.map(m => m.category));
    } catch (error) {
      console.error('Error loading modules:', error);
    }
  }
  
  async function loadEnvironments() {
    try {
      const response = await fetch('/api/environments');
      if (!response.ok) {
        console.error('Failed to load environments:', response.status, response.statusText);
        return;
      }
      const data = await response.json();
      console.log('Loaded environments:', data);
      tenants = data.tenants || [];
    } catch (error) {
      console.error('Error loading environments:', error);
    }
  }
  
  // Filtered modules based on search and category
  $: filteredModules = modules.filter(m => {
    const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory;
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });
  
  // Group modules by category
  $: modulesByCategory = filteredModules.reduce((acc, module) => {
    if (!acc[module.category]) acc[module.category] = [];
    acc[module.category].push(module);
    return acc;
  }, {});
  
  // Drag and drop handlers
  function handleDragStart(event, module) {
    draggedModule = module;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', event.target.innerHTML);
  }
  
  function handleDragEnd() {
    draggedModule = null;
    dragOverZone = null;
  }
  
  function handleDragOver(event, zone) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    dragOverZone = zone;
  }
  
  function handleDragLeave() {
    dragOverZone = null;
  }
  
  async function handleDrop(event, action, tenant, environment) {
    event.preventDefault();
    dragOverZone = null;
    
    if (!draggedModule) return;
    
    const module = draggedModule;
    draggedModule = null;
    
    // Determine the action and execute
    if (action === 'sync') {
      await syncModule(module);
    } else if (action === 'deploy') {
      await deployModule(module, environment);
    } else if (action === 'ship') {
      await shipModule(module, tenant, environment);
    }
  }
  
  async function syncModule(module) {
    activeOperation = `sync-${module.name}`;
    operationStatus = 'running';
    outputLines = [];
    
    try {
      const response = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: module.deployment,
          category: module.category,
          module: module.name
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message}`];
      operationStatus = 'error';
    }
  }
  
  async function deployModule(module, targetEnvKey) {
    activeOperation = `deploy-${module.name}`;
    operationStatus = 'running';
    outputLines = [];
    
    try {
      const response = await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: module.deployment,
          category: module.category,
          module: module.name
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message}`];
      operationStatus = 'error';
    }
  }
  
  async function shipModule(module, tenantName, environmentName) {
    activeOperation = `ship-${module.name}`;
    operationStatus = 'running';
    outputLines = [];
    
    // Find the deployment name for this tenant
    const tenant = tenants.find(t => t.name === tenantName);
    if (!tenant || tenant.deployments.length === 0) {
      outputLines = [`\n✗ Could not find deployment for tenant: ${tenantName}`];
      operationStatus = 'error';
      return;
    }
    
    const deployment = tenant.deployments[0];
    const env = deployment.environments.find(e => e.name === environmentName);
    
    if (!env) {
      outputLines = [`\n✗ Could not find environment: ${environmentName}`];
      operationStatus = 'error';
      return;
    }
    
    try {
      const response = await fetch('/api/ship', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant: deployment.name,
          environment: env.key,
          category: module.category,
          module: module.name
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message}`];
      operationStatus = 'error';
    }
  }
  
  async function streamResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const text = decoder.decode(value);
      const lines = text.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.substring(6));
          
          if (data.type === 'output') {
            outputLines = [...outputLines, data.line];
          } else if (data.type === 'complete') {
            operationStatus = data.exitCode === 0 ? 'success' : 'error';
            outputLines = [...outputLines, `\n${data.exitCode === 0 ? '✓' : '✗'} Completed with exit code: ${data.exitCode}`];
          } else if (data.type === 'error') {
            operationStatus = 'error';
            outputLines = [...outputLines, `\n✗ Error: ${data.message}`];
          }
        }
      }
    }
  }
  
  function clearOutput() {
    outputLines = [];
    activeOperation = null;
    operationStatus = '';
  }
  
  function openCreateModuleDialog() {
    showCreateModuleDialog = true;
    newModuleName = '';
    newModuleCategory = selectedCategory !== 'all' ? selectedCategory : '';
    newModuleDeploy = false;
  }
  
  function closeCreateModuleDialog() {
    showCreateModuleDialog = false;
  }
  
  async function createModule() {
    if (!newModuleName || !newModuleCategory) return;
    
    activeOperation = 'create-module';
    operationStatus = 'running';
    outputLines = [];
    showCreateModuleDialog = false;
    
    try {
      const response = await fetch('/api/modules/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: newModuleCategory,
          moduleName: newModuleName,
          deploy: newModuleDeploy
        })
      });
      
      await streamResponse(response);
      await loadModules(); // Reload modules after creation
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message}`];
      operationStatus = 'error';
    }
  }
  
  async function createRelease(module) {
    activeOperation = `release-${module.name}`;
    operationStatus = 'running';
    outputLines = [];
    
    try {
      const response = await fetch('/api/modules/release', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: module.category,
          module: module.name
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message}`];
      operationStatus = 'error';
    }
  }
  
  function getActionPreview(module, zone) {
    if (!module || !zone) return '';
    
    if (zone.action === 'sync') {
      return `⬇️ Pull ${module.name} from ${module.sourceEnvironment}`;
    } else if (zone.action === 'deploy') {
      return `⬆️ Deploy ${module.name} to ${zone.environment}`;
    } else if (zone.action === 'ship') {
      return `🚀 Ship ${module.name} to ${zone.tenant}/${zone.environment}`;
    }
    
    return '';
  }
</script>

<main>
  <div class="header">
    <h1>🎯 Module Deployment Dashboard</h1>
    <button class="btn btn-primary" on:click={openCreateModuleDialog}>+ New Module</button>
  </div>
  
  <div class="toolbar">
    <div class="search-box">
      <input type="text" placeholder="🔍 Search modules..." bind:value={searchQuery} />
    </div>
    
    <div class="category-filter">
      <button 
        class="category-chip {selectedCategory === 'all' ? 'active' : ''}"
        on:click={() => selectedCategory = 'all'}>
        All
      </button>
      {#each Array.from(categories) as category}
        <button 
          class="category-chip {selectedCategory === category ? 'active' : ''}"
          on:click={() => selectedCategory = category}>
          {category}
        </button>
      {/each}
    </div>
  </div>
  
  <div class="workspace">
    <!-- Left Column: Modules -->
    <div class="column modules-column">
      <h2>📦 Modules</h2>
      
      <div class="module-list">
        {#each Object.entries(modulesByCategory) as [category, categoryModules]}
          <div class="category-group">
            <div class="category-header">{category}</div>
            
            {#each categoryModules as module}
              <div 
                class="module-card"
                draggable="true"
                on:dragstart={(e) => handleDragStart(e, module)}
                on:dragend={handleDragEnd}>
                
                <div class="module-header">
                  <div class="module-name">{module.name}</div>
                  <button 
                    class="icon-btn" 
                    title="Create Release"
                    on:click={() => createRelease(module)}>
                    📦
                  </button>
                </div>
                
                <div class="module-meta">
                  <div class="meta-item">
                    <span class="label">Tenant:</span>
                    <span class="value">{module.tenant}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">Source:</span>
                    <span class="value source">{module.sourceEnvironment}</span>
                  </div>
                  {#if module.targetEnvironments.length > 0}
                    <div class="meta-item">
                      <span class="label">Targets:</span>
                      <span class="value targets">{module.targetEnvironments.join(', ')}</span>
                    </div>
                  {/if}
                </div>
                
                <div class="module-hint">
                  Drag to sync or deploy →
                </div>
              </div>
            {/each}
          </div>
        {/each}
        
        {#if filteredModules.length === 0}
          <div class="empty-state">
            <p>No modules found</p>
            <button class="btn btn-secondary" on:click={openCreateModuleDialog}>Create Module</button>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Middle Column: Source Environments -->
    <div class="column source-column">
      <h2>📥 Source (Sync From)</h2>
      
      <div class="info-box">
        Drag a module here to sync (pull) from its source environment
      </div>
      
      {#if draggedModule}
        <div 
          class="drop-zone {dragOverZone?.action === 'sync' ? 'drag-over' : ''}"
          on:dragover={(e) => handleDragOver(e, { action: 'sync' })}
          on:dragleave={handleDragLeave}
          on:drop={(e) => handleDrop(e, 'sync')}>
          
          <div class="zone-content">
            <div class="zone-icon">⬇️</div>
            <div class="zone-title">Sync: {draggedModule.name}</div>
            <div class="zone-subtitle">From: {draggedModule.sourceEnvironment}</div>
          </div>
        </div>
      {:else}
        <div class="placeholder-zone">
          <div class="placeholder-icon">⬇️</div>
          <div class="placeholder-text">Drag a module to sync</div>
        </div>
      {/if}
    </div>
    
    <!-- Right Column: Target Environments -->
    <div class="column targets-column">
      <h2>📤 Targets (Deploy To)</h2>
      
      <div class="info-box">
        Drag a module here to deploy (push) to target environments
      </div>
      
      <div class="tenant-list">
        {#each tenants as tenant}
          <div class="tenant-group">
            <div class="tenant-header">
              <span class="tenant-icon">🏢</span>
              {tenant.name}
            </div>
            
            {#each tenant.deployments as deployment}
              {#each deployment.environments as env}
                {#if draggedModule}
                  {@const isSourceEnv = env.name === draggedModule.sourceEnvironment}
                  {@const isTargetEnv = draggedModule.targetEnvironmentKeys.includes(env.key)}
                  {@const isSameTenant = tenant.name === draggedModule.tenant}
                  {@const action = isSameTenant ? 'deploy' : 'ship'}
                  
                  <div 
                    class="drop-zone environment-zone {dragOverZone?.environment === env.name ? 'drag-over' : ''} {isSourceEnv ? 'source-env' : ''} {isTargetEnv ? 'target-env' : ''}"
                    on:dragover={(e) => handleDragOver(e, { action, tenant: tenant.name, environment: env.name })}
                    on:dragleave={handleDragLeave}
                    on:drop={(e) => handleDrop(e, action, tenant.name, env.name)}>
                    
                    <div class="zone-content">
                      <div class="zone-icon">{isSameTenant ? '⬆️' : '🚀'}</div>
                      <div class="zone-title">{env.name}</div>
                      {#if isSourceEnv}
                        <div class="zone-badge source-badge">Source</div>
                      {/if}
                      {#if isTargetEnv}
                        <div class="zone-badge target-badge">Target</div>
                      {/if}
                    </div>
                  </div>
                {:else}
                  <div class="placeholder-zone environment-placeholder">
                    <div class="placeholder-text">{env.name}</div>
                  </div>
                {/if}
              {/each}
            {/each}
          </div>
        {/each}
      </div>
    </div>
  </div>
  
  <!-- Drag Preview -->
  {#if draggedModule && dragOverZone}
    <div class="drag-preview">
      {getActionPreview(draggedModule, dragOverZone)}
    </div>
  {/if}
  
  <!-- Output Panel -->
  {#if outputLines.length > 0}
    <div class="output-panel {operationStatus}">
      <div class="output-header">
        <h3>
          {#if operationStatus === 'running'}⏳{:else if operationStatus === 'success'}✅{:else}❌{/if}
          Operation Output
        </h3>
        <button class="btn btn-text" on:click={clearOutput}>✕ Close</button>
      </div>
      
      <div class="output">
        {#each outputLines as line}
          <div>{line}</div>
        {/each}
        {#if operationStatus === 'running'}
          <div class="processing">⏳ Processing...</div>
        {/if}
      </div>
    </div>
  {/if}
  
  <!-- Create Module Dialog -->
  {#if showCreateModuleDialog}
    <div class="dialog-overlay" on:click={closeCreateModuleDialog}>
      <div class="dialog" on:click={(e) => e.stopPropagation()}>
        <h2>Create New Module</h2>
        
        <div class="form-group">
          <label>Module Name</label>
          <input type="text" bind:value={newModuleName} placeholder="e.g., Knowledge Management" />
        </div>
        
        <div class="form-group">
          <label>Category</label>
          <select bind:value={newModuleCategory}>
            <option value="">-- Select or Enter Category --</option>
            {#each Array.from(categories) as category}
              <option value={category}>{category}</option>
            {/each}
          </select>
          <input 
            type="text" 
            bind:value={newModuleCategory} 
            placeholder="Or enter new category (e.g., healthcare)" 
            style="margin-top: 8px;" />
        </div>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" bind:checked={newModuleDeploy} />
            Deploy to development environment after creation
          </label>
        </div>
        
        <div class="dialog-actions">
          <button class="btn btn-secondary" on:click={closeCreateModuleDialog}>Cancel</button>
          <button 
            class="btn btn-primary" 
            on:click={createModule}
            disabled={!newModuleName || !newModuleCategory}>
            Create Module
          </button>
        </div>
      </div>
    </div>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
  }
  
  main {
    padding: 20px;
    max-width: 1800px;
    margin: 0 auto;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  h1 {
    color: #323130;
    font-weight: 600;
    margin: 0;
  }
  
  h2 {
    color: #323130;
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 16px 0;
  }
  
  .toolbar {
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .search-box {
    margin-bottom: 12px;
  }
  
  .search-box input {
    width: 100%;
    padding: 10px 16px;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
  }
  
  .search-box input:focus {
    outline: none;
    border-color: #0078d4;
  }
  
  .category-filter {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .category-chip {
    padding: 6px 16px;
    border: 1px solid #d1d1d1;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.2s;
  }
  
  .category-chip:hover {
    border-color: #0078d4;
    background: #f3f8fc;
  }
  
  .category-chip.active {
    background: #0078d4;
    color: white;
    border-color: #0078d4;
  }
  
  .workspace {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    min-height: 600px;
  }
  
  .column {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
  }
  
  .modules-column {
    overflow-y: auto;
    max-height: calc(100vh - 300px);
  }
  
  .source-column,
  .targets-column {
    overflow-y: auto;
    max-height: calc(100vh - 300px);
  }
  
  .info-box {
    background: #f3f8fc;
    border: 1px solid #c7e0f4;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #0078d4;
  }
  
  .module-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .category-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .category-header {
    font-size: 12px;
    font-weight: 600;
    color: #8a8886;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  
  .module-card {
    background: #fafafa;
    border: 2px solid #e1dfdd;
    border-radius: 6px;
    padding: 14px;
    cursor: grab;
    transition: all 0.2s;
  }
  
  .module-card:hover {
    border-color: #0078d4;
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.15);
    transform: translateY(-2px);
  }
  
  .module-card:active {
    cursor: grabbing;
  }
  
  .module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .module-name {
    font-weight: 600;
    color: #323130;
    font-size: 15px;
  }
  
  .icon-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 4px;
    opacity: 0.7;
    transition: opacity 0.2s;
  }
  
  .icon-btn:hover {
    opacity: 1;
  }
  
  .module-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 10px;
  }
  
  .meta-item {
    display: flex;
    gap: 6px;
    font-size: 12px;
  }
  
  .meta-item .label {
    color: #8a8886;
    font-weight: 600;
  }
  
  .meta-item .value {
    color: #323130;
  }
  
  .meta-item .source {
    color: #0078d4;
    font-weight: 600;
  }
  
  .meta-item .targets {
    color: #107c10;
  }
  
  .module-hint {
    font-size: 11px;
    color: #8a8886;
    font-style: italic;
  }
  
  .drop-zone {
    border: 2px dashed #d1d1d1;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
    transition: all 0.2s;
    background: #fafafa;
    margin-bottom: 12px;
  }
  
  .drop-zone.drag-over {
    border-color: #0078d4;
    background: #f3f8fc;
    transform: scale(1.02);
  }
  
  .drop-zone.source-env {
    border-color: #0078d4;
    background: #f0f8ff;
  }
  
  .drop-zone.target-env {
    border-color: #107c10;
    background: #f0fff0;
  }
  
  .zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .zone-icon {
    font-size: 32px;
  }
  
  .zone-title {
    font-weight: 600;
    color: #323130;
    font-size: 14px;
  }
  
  .zone-subtitle {
    font-size: 12px;
    color: #8a8886;
  }
  
  .zone-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .source-badge {
    background: #e6f4ff;
    color: #0078d4;
  }
  
  .target-badge {
    background: #e6ffe6;
    color: #107c10;
  }
  
  .placeholder-zone {
    border: 2px dashed #e1dfdd;
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    color: #8a8886;
  }
  
  .placeholder-icon {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.5;
  }
  
  .placeholder-text {
    font-size: 13px;
  }
  
  .environment-placeholder {
    padding: 12px;
    margin-bottom: 8px;
  }
  
  .environment-placeholder .placeholder-text {
    font-size: 13px;
    color: #605e5c;
  }
  
  .tenant-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .tenant-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .tenant-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #323130;
    font-size: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e1dfdd;
  }
  
  .tenant-icon {
    font-size: 18px;
  }
  
  .environment-zone {
    padding: 16px;
    margin-bottom: 8px;
  }
  
  .drag-preview {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #323130;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    pointer-events: none;
  }
  
  .output-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 3px solid #0078d4;
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.2);
    z-index: 100;
    max-height: 400px;
    display: flex;
    flex-direction: column;
  }
  
  .output-panel.success {
    border-top-color: #107c10;
  }
  
  .output-panel.error {
    border-top-color: #d13438;
  }
  
  .output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #e1dfdd;
  }
  
  .output-header h3 {
    margin: 0;
    font-size: 16px;
    color: #323130;
  }
  
  .output {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    overflow-y: auto;
    line-height: 1.5;
    flex: 1;
  }
  
  .processing {
    color: #4ec9b0;
    margin-top: 8px;
  }
  
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #8a8886;
  }
  
  .empty-state p {
    margin-bottom: 16px;
  }
  
  .dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
  }
  
  .dialog {
    background: white;
    border-radius: 8px;
    padding: 24px;
    width: 500px;
    max-width: 90%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  
  .dialog h2 {
    margin: 0 0 20px 0;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #323130;
    font-size: 14px;
  }
  
  .form-group input[type="text"],
  .form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
  }
  
  .form-group input[type="text"]:focus,
  .form-group select:focus {
    outline: none;
    border-color: #0078d4;
  }
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  
  .checkbox-label input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .dialog-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
  }
  
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
  }
  
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .btn-primary {
    background-color: #0078d4;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background-color: #106ebe;
  }
  
  .btn-secondary {
    background-color: #f3f2f1;
    color: #323130;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #e1dfdd;
  }
  
  .btn-text {
    background: transparent;
    color: #0078d4;
    padding: 8px 16px;
  }
  
  .btn-text:hover {
    background-color: #f3f2f1;
  }
</style>
