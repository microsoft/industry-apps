<script>
  import { onMount } from 'svelte';
  
  let modules = [];
  let tenants = [];
  let categories = new Set();
  let selectedCategory = 'all';
  let searchQuery = '';
  let selectedTenantIndex = 0;
  
  let draggedModule = null;
  let dragOverZone = null;
  
  let activeOperation = null;
  let operationStatus = '';
  let outputLines = [];
  
  // Queue state
  let operationQueue = [];
  let queueExecuting = false;
  let currentQueueIndex = -1;
  let showErrorDialog = false;
  let errorDialogData = null;
  let nextQueueId = 1;
  
  let showCreateModuleDialog = false;
  let newModuleName = '';
  let newModuleCategory = '';
  let newModuleDeploy = false;
  let newModuleDeployment = '';
  let newModuleSourceEnv = '';
  let newModuleTargetEnvs = [];
  
  let config = null;
  let deployments = [];
  let availableEnvironments = [];
  
  onMount(async () => {
    await loadConfig();
    await loadModules();
    await loadEnvironments();
  });
  
  async function loadConfig() {
    try {
      const response = await fetch('/api/config');
      if (!response.ok) {
        console.error('Failed to load config:', response.status, response.statusText);
        return;
      }
      config = await response.json();
      console.log('Loaded config:', config);
      deployments = Object.keys(config.deployments || {});
    } catch (error) {
      console.error('Error loading config:', error);
    }
  }
  
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
    // Delay clearing to allow drop event to fire first
    // Drop zones are conditionally rendered, so clearing immediately unmounts them
    setTimeout(() => {
      if (draggedModule) {
        draggedModule = null;
        dragOverZone = null;
      }
    }, 100);
  }
  
  function handleDragOver(event, zone) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    dragOverZone = zone;
  }
  
  function handleDragLeave() {
    dragOverZone = null;
  }
  
  async function handleDrop(event, action, tenant, deploymentName, environment, environmentKey, isSourceEnv) {
    event.preventDefault();
    
    if (!draggedModule) return;
    
    const module = draggedModule;
    
    // Clear drag state immediately
    draggedModule = null;
    dragOverZone = null;
    
    // Add to queue
    addToQueue(action, module, tenant, deploymentName, environment, environmentKey, isSourceEnv);
  }
  
  // Queue management functions
  function addToQueue(action, module, tenant, deploymentName, environment, environmentKey, isSourceEnv) {
    const queueItem = {
      id: nextQueueId++,
      type: action,
      module: module,
      tenant: tenant,
      deployment: deploymentName,
      environment: environment,
      environmentKey: environmentKey,
      isSourceEnv: isSourceEnv,
      status: 'queued', // queued, running, success, failed
      output: [],
      error: null
    };
    
    operationQueue = [...operationQueue, queueItem];
  }
  
  function removeFromQueue(id) {
    operationQueue = operationQueue.filter(item => item.id !== id);
  }
  
  function moveQueueItemUp(index) {
    if (index === 0 || queueExecuting) return;
    const newQueue = [...operationQueue];
    [newQueue[index - 1], newQueue[index]] = [newQueue[index], newQueue[index - 1]];
    operationQueue = newQueue;
  }
  
  function moveQueueItemDown(index) {
    if (index === operationQueue.length - 1 || queueExecuting) return;
    const newQueue = [...operationQueue];
    [newQueue[index], newQueue[index + 1]] = [newQueue[index + 1], newQueue[index]];
    operationQueue = newQueue;
  }
  
  function clearQueue() {
    if (queueExecuting) return;
    operationQueue = [];
  }
  
  function resetQueue() {
    if (queueExecuting) return;
    operationQueue = operationQueue.map(item => ({
      ...item,
      status: 'queued',
      error: null,
      output: []
    }));
  }
  
  async function executeQueue() {
    if (queueExecuting || operationQueue.length === 0) return;
    
    queueExecuting = true;
    
    for (let i = 0; i < operationQueue.length; i++) {
      currentQueueIndex = i;
      const item = operationQueue[i];
      
      // Skip already completed operations
      if (item.status === 'success') {
        continue;
      }
      
      // Update status to running
      operationQueue[i] = { ...item, status: 'running' };
      operationQueue = operationQueue;
      
      // Execute the operation
      try {
        if (item.type === 'sync') {
          await syncModule(item.module);
        } else if (item.type === 'deploy') {
          await deployModule(item.module, item.deployment, item.environmentKey, item.isSourceEnv);
        } else if (item.type === 'ship') {
          await shipModule(item.module, item.tenant, item.environment);
        }
        
        // Mark as success
        operationQueue[i] = { ...item, status: 'success', output: [...outputLines] };
        operationQueue = operationQueue;
      } catch (error) {
        // Mark as failed
        operationQueue[i] = { ...item, status: 'failed', error: error.message, output: [...outputLines] };
        operationQueue = operationQueue;
        
        // Show error dialog and wait for user decision
        errorDialogData = { item, index: i };
        showErrorDialog = true;
        
        // Wait for user to close the error dialog
        await new Promise((resolve) => {
          const checkDialog = setInterval(() => {
            if (!showErrorDialog) {
              clearInterval(checkDialog);
              resolve();
            }
          }, 100);
        });
        
        // If user chose to stop, break out of the loop
        if (errorDialogData?.action === 'stop') {
          break;
        } else if (errorDialogData?.action === 'retry') {
          // Retry the current operation
          i--;
        }
        // If 'continue', just move to next iteration
      }
    }
    
    queueExecuting = false;
    currentQueueIndex = -1;
  }
  
  function handleErrorDialogAction(action) {
    errorDialogData = { ...errorDialogData, action };
    showErrorDialog = false;
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
  
  async function deployModule(module, deploymentName, targetEnvKey, isSourceEnv) {
    const deployType = isSourceEnv ? 'push (unmanaged)' : 'deploy (managed)';
    activeOperation = `${deployType}-${module.name}`;
    operationStatus = 'running';
    outputLines = [];
    
    try {
      const response = await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: deploymentName,
          category: module.category,
          module: module.name,
          targetEnvironment: targetEnvKey,
          managed: !isSourceEnv
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }
      
      await streamResponse(response);
    } catch (error) {
      outputLines = [...outputLines, `\n✗ Connection error: ${error.message || error}`];
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
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              console.log('[DEBUG] SSE data:', data);  // Debug logging
              
              if (data.type === 'output') {
                outputLines = [...outputLines, data.line];
              } else if (data.type === 'complete') {
                operationStatus = data.exitCode === 0 ? 'success' : 'error';
                outputLines = [...outputLines, `\n${data.exitCode === 0 ? '✓' : '✗'} Completed with exit code: ${data.exitCode}`];
              } else if (data.type === 'error') {
                operationStatus = 'error';
                console.error('[ERROR] Backend error:', data);  // Error logging
                outputLines = [...outputLines, `\n✗ Error: ${data.message || 'Unknown error'}`];
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', line, parseError);
              outputLines = [...outputLines, `\n✗ Parse error: ${line}`];
            }
          }
        }
      }
    } catch (error) {
      operationStatus = 'error';
      outputLines = [...outputLines, `\n✗ Stream error: ${error.message || error}`];
    }
  }
  
  function clearOutput() {
    outputLines = [];
    activeOperation = null;
    operationStatus = '';
  }
  
  // Update available environments when deployment changes
  $: if (newModuleDeployment && config) {
    const deployment = config.deployments[newModuleDeployment];
    if (deployment && deployment.Environments) {
      availableEnvironments = Object.keys(deployment.Environments);
    } else {
      availableEnvironments = [];
    }
  }
  
  function openCreateModuleDialog() {
    showCreateModuleDialog = true;
    newModuleName = '';
    newModuleCategory = selectedCategory !== 'all' ? selectedCategory : '';
    newModuleDeploy = false;
    
    // Set defaults from DefaultModule
    if (config && config.defaultModule) {
      newModuleDeployment = config.defaultModule.Tenant || '';
      newModuleSourceEnv = config.defaultModule.Environment || '';
      newModuleTargetEnvs = config.defaultModule.DeploymentTargets || [];
    } else {
      newModuleDeployment = deployments[0] || '';
      newModuleSourceEnv = '';
      newModuleTargetEnvs = [];
    }
  }
  
  function closeCreateModuleDialog() {
    showCreateModuleDialog = false;
  }
  
  async function createModule() {
    if (!newModuleName || !newModuleCategory || !newModuleDeployment || !newModuleSourceEnv) return;
    
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
          deployment: newModuleDeployment,
          sourceEnvironment: newModuleSourceEnv,
          targetEnvironments: newModuleTargetEnvs,
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
      return `⬇️ Sync: ${module.name} from ${module.sourceEnvironment}`;
    } else if (zone.action === 'deploy') {
      const isSource = zone.environment === module.sourceEnvironment;
      const deployType = isSource ? 'Push (Unmanaged)' : 'Deploy (Managed)';
      return `⬆️ ${deployType}: ${module.name} → ${zone.environment}`;
    } else if (zone.action === 'ship') {
      return `🚀 Ship (Managed): ${module.name} → ${zone.tenant}/${zone.environment}`;
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
                    <span class="label">Category:</span>
                    <span class="value">{module.category}</span>
                  </div>
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
                  Drag to deploy →
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
    
    <!-- Right Column: Local Sync & Target Environments -->
    <div class="column targets-column">
      <div class="info-box">
        Drag a module to Local (Sync From) to sync, or to an environment to deploy.
      </div>
      
      <!-- Local Sync Section -->
      <div class="section-container">
        <h2>⬇️ Local (Sync From)</h2>
        
        {#if draggedModule}
          <div 
            class="drop-zone local-sync-zone {dragOverZone?.action === 'sync' ? 'drag-over' : ''}"
            on:dragover={(e) => handleDragOver(e, { action: 'sync' })}
            on:dragleave={handleDragLeave}
            on:drop={(e) => handleDrop(e, 'sync')}>
            
            <div class="zone-content">
              <div class="zone-icon">⬇️</div>
            </div>
          </div>
        {:else}
          <div class="placeholder-zone local-placeholder">
            <div class="placeholder-icon">⬇️</div>
            <div class="placeholder-text">Drag a module here to sync from source</div>
          </div>
        {/if}
      </div>
      
      <!-- Targets Section -->
      <div class="section-container targets-section">
        <h2>📤 Targets (Deploy To)</h2>
        
        <!-- Tenant Tabs -->
        <div class="tenant-tabs">
          {#each tenants as tenant, index}
            <button
              class="tenant-tab {selectedTenantIndex === index ? 'active' : ''}"
              on:click={() => selectedTenantIndex = index}>
              <span class="tenant-icon">🏢</span>
              {tenant.name}
            </button>
          {/each}
        </div>
        
      <div class="tenant-list">
        {#if tenants[selectedTenantIndex]}
          {@const tenant = tenants[selectedTenantIndex]}
          <div class="tenant-group">
            
            {#each tenant.deployments as deployment}
              {#each deployment.environments as env}
                {#if draggedModule}
                  {@const isSourceEnv = env.name === draggedModule.sourceEnvironment}
                  {@const isTargetEnv = draggedModule.targetEnvironmentKeys.includes(env.key)}
                  {@const isSameTenant = tenant.name === draggedModule.tenant}
                  {@const action = isSameTenant ? 'deploy' : 'ship'}
                  
                  <div 
                    class="drop-zone environment-zone {dragOverZone?.environment === env.name ? 'drag-over' : ''} {isSourceEnv ? 'source-env' : ''} {isTargetEnv ? 'target-env' : ''}"
                    on:dragover={(e) => handleDragOver(e, { action, tenant: tenant.name, environment: env.name, environmentKey: env.key, isSourceEnv })}
                    on:dragleave={handleDragLeave}
                    on:drop={(e) => handleDrop(e, action, tenant.name, deployment.name, env.name, env.key, isSourceEnv)}>
                    
                    <div class="zone-content">
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
        {/if}
      </div>
      </div>
    </div>
    
    <!-- Queue Column -->
    <div class="column queue-column">
      <h2>📋 Operation Queue</h2>
      
      <div class="queue-header">
        <button 
          class="btn btn-primary" 
          disabled={operationQueue.length === 0 || queueExecuting}
          on:click={executeQueue}>
          {queueExecuting ? '⏳ Executing...' : '▶️ Execute All'}
        </button>
        <button 
          class="btn btn-secondary" 
          disabled={operationQueue.length === 0 || queueExecuting}
          on:click={resetQueue}>
          🔄 Reset
        </button>
        <button 
          class="btn btn-text" 
          disabled={operationQueue.length === 0 || queueExecuting}
          on:click={clearQueue}>
          🗑️ Clear
        </button>
      </div>
      
      <div class="queue-list">
        {#if operationQueue.length === 0}
          <div class="empty-state">
            <p>No operations queued</p>
            <p class="hint">Drag modules to environments to add operations to the queue</p>
          </div>
        {:else}
          {#each operationQueue as item, index}
            <div class="queue-item {item.status}">
              <div class="queue-item-header">
                <div class="queue-item-status">
                  {#if item.status === 'queued'}⏸️
                  {:else if item.status === 'running'}⏳
                  {:else if item.status === 'success'}✅
                  {:else if item.status === 'failed'}❌
                  {/if}
                </div>
                <div class="queue-item-title">
                  {#if item.type === 'sync'}
                    ⬇️ Sync
                  {:else if item.type === 'deploy'}
                    📤 Deploy
                  {:else if item.type === 'ship'}
                    🚢 Ship
                  {/if}
                  <strong>{item.module.name}</strong>
                </div>
              </div>
              
              <div class="queue-item-details">
                {#if item.type === 'sync'}
                  <div class="detail">From: {item.module.sourceEnvironment}</div>
                {:else if item.type === 'deploy'}
                  <div class="detail">To: {item.environment}</div>
                  <div class="detail">Tenant: {item.tenant || item.module.tenant}</div>
                {:else if item.type === 'ship'}
                  <div class="detail">To: {item.environment}</div>
                  <div class="detail">Tenant: {item.tenant}</div>
                {/if}
              </div>
              
              <div class="queue-item-actions">
                <button 
                  class="btn btn-icon-sm" 
                  title="Move up"
                  disabled={queueExecuting || index === 0}
                  on:click={() => moveQueueItemUp(index)}>
                  ▲
                </button>
                <button 
                  class="btn btn-icon-sm" 
                  title="Move down"
                  disabled={queueExecuting || index === operationQueue.length - 1}
                  on:click={() => moveQueueItemDown(index)}>
                  ▼
                </button>
                {#if item.status === 'queued'}
                  <div class="action-divider"></div>
                  <button 
                    class="btn btn-icon-sm remove" 
                    title="Remove from queue"
                    disabled={queueExecuting}
                    on:click={() => removeFromQueue(item.id)}>
                    ✕
                  </button>
                {/if}
              </div>
              
              {#if item.error}
                <div class="queue-item-error">
                  ❌ {item.error}
                </div>
              {/if}
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
  
  <!-- Drag Preview -->
  {#if draggedModule && dragOverZone}
    <div class="drag-preview">
      {getActionPreview(draggedModule, dragOverZone)}
    </div>
  {/if}
  
  <!-- Error Dialog -->
  {#if showErrorDialog && errorDialogData}
    <div class="dialog-overlay">
      <div class="dialog error-dialog" on:click={(e) => e.stopPropagation()}>
        <h2>❌ Operation Failed</h2>
        
        <div class="error-content">
          <p><strong>Module:</strong> {errorDialogData.item.module.name}</p>
          <p><strong>Operation:</strong> {errorDialogData.item.type}</p>
          {#if errorDialogData.item.environment}
            <p><strong>Target:</strong> {errorDialogData.item.environment}</p>
          {/if}
          {#if errorDialogData.item.error}
            <p class="error-message">{errorDialogData.item.error}</p>
          {/if}
        </div>
        
        <div class="dialog-actions">
          <button class="btn btn-primary" on:click={() => handleErrorDialogAction('continue')}>
            Continue with Next
          </button>
          <button class="btn btn-secondary" on:click={() => handleErrorDialogAction('retry')}>
            Retry This Operation
          </button>
          <button class="btn btn-text" on:click={() => handleErrorDialogAction('stop')}>
            Stop Queue
          </button>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Output Modal Dialog -->
  {#if outputLines.length > 0}
    <div class="dialog-overlay" on:click={operationStatus !== 'running' ? clearOutput : null}>
      <div class="dialog output-dialog {operationStatus}" on:click={(e) => e.stopPropagation()}>
        <div class="output-header">
          <h2>
            {#if operationStatus === 'running'}⏳{:else if operationStatus === 'success'}✅{:else}❌{/if}
            Operation Output
          </h2>
          {#if operationStatus !== 'running'}
            <button class="btn btn-text" on:click={clearOutput}>✕ Close</button>
          {/if}
        </div>
        
        <div class="output">
          {#each outputLines as line}
            <div>{line}</div>
          {/each}
          {#if operationStatus === 'running'}
            <div class="processing">⏳ Processing...</div>
          {/if}
        </div>
        
        {#if operationStatus !== 'running'}
          <div class="dialog-actions">
            <button class="btn btn-primary" on:click={clearOutput}>Close</button>
          </div>
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
        
        <div class="form-divider"></div>
        
        <div class="form-group">
          <label>Development Deployment</label>
          <select bind:value={newModuleDeployment}>
            <option value="">-- Select Deployment --</option>
            {#each deployments as deployment}
              <option value={deployment}>{deployment}</option>
            {/each}
          </select>
          <div class="help-text">Where this module will be developed</div>
        </div>
        
        <div class="form-group">
          <label>Source Environment</label>
          <select bind:value={newModuleSourceEnv} disabled={!newModuleDeployment}>
            <option value="">-- Select Environment --</option>
            {#each availableEnvironments as env}
              <option value={env}>{env}</option>
            {/each}
          </select>
          <div class="help-text">Environment to sync from and push to during development</div>
        </div>
        
        <div class="form-group">
          <label>Target Environments (Optional)</label>
          <div class="checkbox-list">
            {#each availableEnvironments as env}
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  value={env}
                  checked={newModuleTargetEnvs.includes(env)}
                  on:change={(e) => {
                    if (e.target.checked) {
                      newModuleTargetEnvs = [...newModuleTargetEnvs, env];
                    } else {
                      newModuleTargetEnvs = newModuleTargetEnvs.filter(t => t !== env);
                    }
                  }}
                  disabled={!newModuleDeployment} />
                {env}
              </label>
            {/each}
          </div>
          <div class="help-text">Downstream environments for managed deployments</div>
        </div>
        
        <div class="form-divider"></div>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" bind:checked={newModuleDeploy} />
            Build and deploy to source environment immediately
          </label>
        </div>
        
        <div class="dialog-actions">
          <button class="btn btn-secondary" on:click={closeCreateModuleDialog}>Cancel</button>
          <button 
            class="btn btn-primary" 
            on:click={createModule}
            disabled={!newModuleName || !newModuleCategory || !newModuleDeployment || !newModuleSourceEnv}>
            Create Module
          </button>
        </div>
      </div>
    </div>
  {/if}
</main>

<style>
  :global(html) {
    height: 100%;
    margin: 0;
    padding: 0;
  }
  
  :global(body) {
    margin: 0;
    padding: 0;
    height: 100%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #1e1e1e;
    color: #e0e0e0;
    overflow-y: auto;
  }
  
  :global(#app) {
    min-height: 100%;
  }
  
  main {
    padding: 20px 20px 0 20px;
    max-width: 1800px;
    margin: 0 auto;
    display: block;
  }
  
  main > *:last-child {
    margin-bottom: 0;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  h1 {
    color: #ffffff;
    font-weight: 600;
    margin: 0;
  }
  
  h2 {
    color: #ffffff;
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 16px 0;
  }
  
  .toolbar {
    background: #252526;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    border: 1px solid #3c3c3c;
  }
  
  .search-box {
    margin-bottom: 12px;
  }
  
  .search-box input {
    width: 100%;
    padding: 10px 16px;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    background: #1e1e1e;
    color: #e0e0e0;
  }
  
  .search-box input:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }
  
  .category-filter {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .category-chip {
    padding: 6px 16px;
    border: 1px solid #3c3c3c;
    border-radius: 20px;
    background: #2d2d30;
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.2s;
    color: #cccccc;
  }
  
  .category-chip:hover {
    border-color: #0078d4;
    background: #264f78;
    color: #ffffff;
  }
  
  .category-chip.active {
    background: #0078d4;
    color: white;
    border-color: #0078d4;
  }
  
  .workspace {
    display: grid;
    grid-template-columns: 25% 50% 25%;
    gap: 20px;
    min-height: 0;
  }
  
  .column {
    background: #252526;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    border: 1px solid #3c3c3c;
    display: flex;
    flex-direction: column;
  }
  
  .modules-column {
    overflow-y: auto;
    max-height: calc(100vh - 220px);
  }
  
  .targets-column {
    max-height: calc(100vh - 220px);
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
  }
  
  .queue-column {
    max-height: calc(100vh - 220px);
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
  }
  
  .queue-header {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }
  
  .queue-header .btn {
    flex: 1;
  }
  
  .queue-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .queue-item {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 12px;
    transition: all 0.2s;
  }
  
  .queue-item.disabled {
    pointer-events: none;
    opacity: 0.6;
  }
  
  .queue-item[draggable="true"] {
    cursor: grab;
  }
  
  .queue-item[draggable="true"]:active {
    cursor: grabbing;
  }
  
  .queue-item.drag-over {
    border-color: #0078d4;
    border-width: 2px;
    margin-top: 4px;
    transform: translateY(2px);
  }
  
  .queue-item.running {
    border-color: #0078d4;
    background: #1a2332;
  }
  
  .queue-item.success {
    border-color: #4caf50;
    background: #1a2a1b;
  }
  
  .queue-item.failed {
    border-color: #f44336;
    background: #2a1a1b;
  }
  
  .queue-item-header {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 6px;
  }
  
  .queue-item-status {
    font-size: 18px;
    line-height: 1;
    flex-shrink: 0;
  }
  
  .queue-item-title {
    flex: 1;
    font-size: 13px;
    color: #cccccc;
    line-height: 1.4;
  }
  
  .queue-item-title strong {
    color: #ffffff;
  }
  
  .queue-item-actions {
    display: flex;
    gap: 4px;
    align-items: center;
    padding-top: 6px;
    border-top: 1px solid #3c3c3c;
    margin-top: 8px;
  }
  
  .action-divider {
    width: 1px;
    height: 16px;
    background: #3c3c3c;
    margin: 0 4px;
  }
  
  .btn-icon-sm {
    background: transparent;
    border: 1px solid #3c3c3c;
    color: #cccccc;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 11px;
    line-height: 1;
    transition: all 0.2s;
    min-width: 28px;
  }
  
  .btn-icon-sm:hover:not(:disabled) {
    background: #0078d4;
    border-color: #0078d4;
    color: white;
  }
  
  .btn-icon-sm.remove:hover:not(:disabled) {
    background: #d32f2f;
    border-color: #d32f2f;
  }
  
  .btn-icon-sm:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
  
  .queue-item-details {
    margin-left: 26px;
    font-size: 12px;
    color: #858585;
    margin-bottom: 2px;
  }
  
  .queue-item-details .detail {
    margin-bottom: 2px;
  }
  
  .queue-item-error {
    margin-top: 8px;
    margin-left: 26px;
    padding: 6px 8px;
    background: #2a1a1b;
    border: 1px solid #f44336;
    border-radius: 4px;
    font-size: 12px;
    color: #f48771;
  }
  
  .error-dialog {
    max-width: 500px;
  }
  
  .error-content {
    margin: 16px 0;
    padding: 12px;
    background: #2a1a1b;
    border: 1px solid #f44336;
    border-radius: 6px;
  }
  
  .error-content p {
    margin: 8px 0;
    font-size: 13px;
  }
  
  .error-message {
    color: #f48771;
    font-family: 'Consolas', monospace;
    margin-top: 12px !important;
    padding-top: 12px;
    border-top: 1px solid #3c3c3c;
  }
  
  .section-container {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 12px;
    padding: 14px;
  }
  
  .section-container h2 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 15px;
  }
  
  .section-container:first-child {
    padding: 10px;
  }
  
  .targets-section {
    flex: 1;
    overflow-y: auto;
    max-height: calc(100vh - 340px);
  }
  
  .local-sync-zone,
  .local-placeholder {
    min-height: 40px;
    height: 40px;
    box-sizing: border-box;
  }
  
  .drop-zone.local-sync-zone {
    padding: 8px !important;
    margin-bottom: 0 !important;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .drop-zone.local-sync-zone .zone-content {
    gap: 0;
    flex-direction: row;
  }
  
  .drop-zone.local-sync-zone.drag-over {
    transform: none !important;
  }
  
  .local-sync-zone .zone-icon {
    font-size: 18px;
  }
  
  .local-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: #2d2d2d;
    border: 2px dashed #505050;
    border-radius: 8px;
    padding: 8px !important;
  }
  
  .local-placeholder .placeholder-icon {
    font-size: 18px;
  }
  
  .local-placeholder .placeholder-text {
    color: #888;
    font-size: 13px;
  }
  
  .info-box {
    background: #1e3a5f;
    border: 1px solid #2b5a8e;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 0;
    font-size: 13px;
    color: #9cdcfe;
  }
  
  .tenant-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    border-bottom: 1px solid #3c3c3c;
    padding-bottom: 0;
  }
  
  .tenant-tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 16px;
    cursor: pointer;
    color: #888;
    font-size: 14px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: -1px;
  }
  
  .tenant-tab:hover {
    color: #c0c0c0;
    background: #2d2d2d;
  }
  
  .tenant-tab.active {
    color: #ffffff;
    border-bottom-color: #0078d4;
  }
  
  .tenant-tab .tenant-icon {
    font-size: 16px;
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
    color: #999999;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  
  .module-card {
    background: #2d2d30;
    border: 2px solid #3c3c3c;
    border-radius: 6px;
    padding: 14px;
    cursor: grab;
    transition: all 0.2s;
  }
  
  .module-card:hover {
    border-color: #0078d4;
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
    transform: translateY(-2px);
    background: #333333;
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
  
  .module-actions {
    display: flex;
    gap: 4px;
  }
  
  .module-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 15px;
  }
  
  .icon-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 18px;
    padding: 4px;
    opacity: 0.7;
    transition: opacity 0.2s;
    filter: grayscale(0);
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
    color: #999999;
    font-weight: 600;
  }
  
  .meta-item .value {
    color: #cccccc;
  }
  
  .meta-item .source {
    color: #4fc3f7;
    font-weight: 600;
  }
  
  .meta-item .targets {
    color: #81c784;
  }
  
  .module-hint {
    font-size: 11px;
    color: #808080;
    font-style: italic;
  }
  
  .drop-zone {
    border: 2px dashed #3c3c3c;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
    transition: all 0.2s;
    background: #2d2d30;
    margin-bottom: 12px;
  }
  
  .drop-zone.drag-over {
    border-color: #0078d4;
    background: #1e3a5f;
    transform: scale(1.02);
  }
  
  .drop-zone.source-env {
    border-color: #2b5a8e;
    background: #1e3a5f;
  }
  
  .drop-zone.target-env {
    border-color: #2e7d32;
    background: #1b3d1b;
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
  
  .environment-zone .zone-content {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
    justify-content: center;
  }
  
  .environment-zone .zone-title {
    font-weight: 500;
    color: #ffffff;
    font-size: 13px;
  }
  
  .zone-subtitle {
    font-size: 12px;
    color: #999999;
  }
  
  .zone-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .source-badge {
    background: #1e3a5f;
    color: #4fc3f7;
  }
  
  .target-badge {
    background: #1b3d1b;
    color: #81c784;
  }
  
  .placeholder-zone {
    border: 2px dashed #3c3c3c;
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    color: #666666;
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
    color: #999999;
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
    color: #ffffff;
    font-size: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #3c3c3c;
  }
  
  .tenant-icon {
    font-size: 18px;
  }
  
  .environment-zone {
    padding: 12px;
    margin-bottom: 8px;
  }
  
  .environment-zone.drag-over {
    transform: none !important;
  }
  
  .drag-preview {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #0078d4;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 4px 16px rgba(0, 120, 212, 0.5);
    z-index: 1000;
    pointer-events: none;
  }
  
  .output-dialog {
    width: 1200px;
    max-width: 95%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }
  
  .output-dialog.running {
    border-top: 4px solid #0078d4;
  }
  
  .output-dialog.success {
    border-top: 4px solid #4caf50;
  }
  
  .output-dialog.error {
    border-top: 4px solid #f44336;
  }
  
  .output-dialog .output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .output-dialog .output-header h2 {
    margin: 0;
    font-size: 18px;
    color: #ffffff;
  }
  
  .output {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    overflow-y: auto;
    line-height: 1.5;
    flex: 1;
    max-height: 650px;
    min-height: 300px;
    border: 1px solid #3c3c3c;
  }
  
  .processing {
    color: #4ec9b0;
    margin-top: 8px;
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999999;
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
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
  }
  
  .dialog {
    background: #252526;
    border-radius: 8px;
    padding: 24px;
    width: 500px;
    max-width: 90%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    border: 1px solid #3c3c3c;
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
    color: #cccccc;
    font-size: 14px;
  }
  
  .form-group input[type="text"],
  .form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    background: #1e1e1e;
    color: #e0e0e0;
  }
  
  .form-group input[type="text"]:focus,
  .form-group select:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }
  
  .form-divider {
    height: 1px;
    background: #3c3c3c;
    margin: 24px 0;
  }
  
  .help-text {
    font-size: 12px;
    color: #808080;
    margin-top: 4px;
  }
  
  .checkbox-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
    max-height: 150px;
    overflow-y: auto;
  }
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-weight: normal;
    color: #cccccc;
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
    background-color: #1a86e0;
  }
  
  .btn-secondary {
    background-color: #3c3c3c;
    color: #ffffff;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #505050;
  }
  
  .btn-text {
    background: transparent;
    color: #0078d4;
    padding: 8px 16px;
  }
  
  .btn-text:hover {
    background-color: #3c3c3c;
  }
</style>






















