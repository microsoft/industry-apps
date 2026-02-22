<script>
  import { onMount } from 'svelte';
  import { outputLines, activeOperation, operationStatus, modules, tenants, config, loadModules, loadEnvironments, loadConfig } from '../lib/stores.js';
  import OutputStream from '../lib/OutputStream.svelte';
  import Header from '../lib/Header.svelte';
  
  let categories = new Set();
  let selectedCategory = 'all';
  let searchQuery = '';
  let selectedTenantIndex = 0;
  
  let draggedModule = null;
  let draggedEnvironment = null; // For reverse drag (environment → module)
  let dragOverZone = null;
  
  // Queue state
  let operationQueue = [];
  let queueExecuting = false;
  let currentQueueIndex = -1;
  let showErrorDialog = false;
  let errorDialogData = null;
  let nextQueueId = 1;
  
  // Sync-from confirmation dialog
  let showSyncFromDialog = false;
  let syncFromDialogData = null;
  
  let showCreateModuleDialog = false;
  let newModuleName = '';
  let newModuleCategory = '';
  let newModuleDeploy = false;
  let newModuleDeployment = '';
  let newModuleSourceEnv = '';
  let newModuleTargetEnvs = [];
  
  let deployments = [];
  let availableEnvironments = [];
  
  // Version management state
  let editingVersionModule = null;  // Module currently being edited
  let editVersionValue = '';        // Current input value
  
  // Sync settings
  let autoIncrementOnSync = true;   // Auto-increment revision on sync

  onMount(async () => {
    await loadConfig();
    await loadModules();
    await loadEnvironments();
  });
  
  // Update deployments when config changes
  $: if ($config) {
    deployments = Object.keys($config.deployments || {});
  }
  
  // Update categories when modules change
  $: if ($modules) {
    categories = new Set($modules.map(m => m.category));
  }
  
  // Filtered modules based on search and category
  $: filteredModules = $modules.filter(m => {
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
  
  // Environment drag handlers (for reverse drag: environment → module)
  function handleEnvDragStart(event, envData) {
    draggedEnvironment = envData;
    event.dataTransfer.effectAllowed = 'copy'; // Use 'copy' to differentiate from module drag
    event.dataTransfer.setData('text/html', event.target.innerHTML);
  }
  
  function handleEnvDragEnd() {
    setTimeout(() => {
      if (draggedEnvironment) {
        draggedEnvironment = null;
        dragOverZone = null;
      }
    }, 100);
  }
  
  function handleDragOver(event, zone) {
    event.preventDefault();
    event.dataTransfer.dropEffect = draggedEnvironment ? 'copy' : 'move';
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
  
  // Handle drop of environment onto module (sync-from)
  async function handleEnvDropOnModule(event, module) {
    event.preventDefault();
    
    if (!draggedEnvironment) return;
    
    const envData = draggedEnvironment;
    
    // Clear drag state
    draggedEnvironment = null;
    dragOverZone = null;
    
    // Show confirmation dialog
    syncFromDialogData = {
      module: module,
      environment: envData
    };
    showSyncFromDialog = true;
  }
  
  function confirmSyncFrom() {
    if (!syncFromDialogData) return;
    
    const { module, environment } = syncFromDialogData;
    
    // Add sync-from to queue
    const queueItem = {
      id: nextQueueId++,
      type: 'sync-from',
      module: module,
      tenant: environment.tenant,
      deployment: environment.deployment,
      environment: environment.name,
      environmentKey: environment.key,
      isSourceEnv: false,
      status: 'queued',
      output: [],
      error: null
    };
    
    operationQueue = [...operationQueue, queueItem];
    
    // Close dialog
    showSyncFromDialog = false;
    syncFromDialogData = null;
  }
  
  function cancelSyncFrom() {
    showSyncFromDialog = false;
    syncFromDialogData = null;
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
      error: null,
      upgrade: false, // upgrade flag for managed deployments
      forceUnmanaged: false // force unmanaged deployment (override default)
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
  
  function toggleQueueItemUpgrade(id) {
    operationQueue = operationQueue.map(item => 
      item.id === id ? { ...item, upgrade: !item.upgrade } : item
    );
  }
  
  function toggleQueueItemUnmanaged(id) {
    operationQueue = operationQueue.map(item => 
      item.id === id ? { ...item, forceUnmanaged: !item.forceUnmanaged } : item
    );
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
        } else if (item.type === 'sync-from') {
          await syncModuleFromEnvironment(item.module, item.deployment, item.environment);
        } else if (item.type === 'deploy') {
          await deployModule(item.module, item.deployment, item.environmentKey, item.isSourceEnv, item.upgrade, item.forceUnmanaged);
        } else if (item.type === 'ship') {
          await shipModule(item.module, item.deployment, item.environment, item.environmentKey, item.forceUnmanaged);
        }
        
        // Mark as success
        operationQueue[i] = { ...item, status: 'success', output: [...$outputLines] };
        operationQueue = operationQueue;
      } catch (error) {
        // Mark as failed
        operationQueue[i] = { ...item, status: 'failed', error: error.message, output: [...$outputLines] };
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
    
    // Reload modules if any sync operations were successful
    const hadSuccessfulSync = operationQueue.some(item => 
      (item.type === 'sync' || item.type === 'sync-from') && item.status === 'success'
    );
    if (hadSuccessfulSync) {
      await loadModules();
    }
  }
  
  function handleErrorDialogAction(action) {
    errorDialogData = { ...errorDialogData, action };
    showErrorDialog = false;
  }
  
  async function syncModule(module) {
    activeOperation.set(`sync-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
    try {
      // If auto-increment is enabled, update version (which includes sync)
      if (autoIncrementOnSync) {
        outputLines.update(lines => [...lines, 'Auto-incrementing revision number...']);
        
        // Calculate new version (increment revision)
        const parts = module.version.split('.').map(p => parseInt(p) || 0);
        while (parts.length < 4) parts.push(0);
        parts[3]++; // Increment revision
        const newVersion = parts.join('.');
        
        outputLines.update(lines => [...lines, `Updating version: ${module.version} → ${newVersion}`]);
        outputLines.update(lines => [...lines, '(Version update includes sync operation)']);
        outputLines.update(lines => [...lines, '']);
        
        // Call version update endpoint (which already includes sync)
        const versionResponse = await fetch('/api/version', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            deployment: module.deployment,
            category: module.category,
            module: module.name,
            version: newVersion
          })
        });
        
        await streamResponse(versionResponse);
      } else {
        // Just do a regular sync without version update
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
      }
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }
  
  async function syncModuleFromEnvironment(module, deploymentName, environmentName) {
    activeOperation.set(`sync-from-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
    try {
      const response = await fetch('/api/sync-from', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: deploymentName,
          category: module.category,
          module: module.name,
          sourceEnvironment: environmentName
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }
  
  async function deployModule(module, deploymentName, targetEnvKey, isSourceEnv, upgrade = false, forceUnmanaged = false) {
    // Determine if this should be managed or unmanaged
    const isManaged = forceUnmanaged ? false : !isSourceEnv;
    const deployType = isManaged ? 'deploy (managed)' : 'push (unmanaged)';
    activeOperation.set(`${deployType}-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
    try {
      const response = await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: deploymentName,
          category: module.category,
          module: module.name,
          targetEnvironment: targetEnvKey,
          managed: isManaged,
          upgrade: upgrade && isManaged // Only upgrade for managed deployments
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }
      
      await streamResponse(response);
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message || error}`]);
      operationStatus.set('error');
    }
  }
  
  async function shipModule(module, deploymentName, environmentName, environmentKey, forceUnmanaged = false) {
    const isManaged = !forceUnmanaged;
    const deployType = isManaged ? 'ship (managed)' : 'ship (unmanaged)';
    activeOperation.set(`${deployType}-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
    try {
      const response = await fetch('/api/ship', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant: deploymentName,
          environment: environmentKey,
          category: module.category,
          module: module.name,
          managed: isManaged
        })
      });
      
      await streamResponse(response);
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }
  
  async function pushToSource(module) {
    // Push unmanaged solution to the source environment
    await deployModule(module, module.deployment, module.sourceEnvironmentKey, true, false);
    
    // Reload modules after successful push
    if ($operationStatus === 'success') {
      await loadModules();
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
                outputLines.update(prevLines => [...prevLines, data.line]);
              } else if (data.type === 'complete') {
                operationStatus.set(data.exitCode === 0 ? 'success' : 'error');
                outputLines.update(prevLines => [...prevLines, `\n${data.exitCode === 0 ? '✓' : '✗'} Completed with exit code: ${data.exitCode}`]);
              } else if (data.type === 'error') {
                operationStatus.set('error');
                console.error('[ERROR] Backend error:', data);  // Error logging
                outputLines.update(prevLines => [...prevLines, `\n✗ Error: ${data.message || 'Unknown error'}`]);
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', line, parseError);
              outputLines.update(prevLines => [...prevLines, `\n✗ Parse error: ${line}`]);
            }
          }
        }
      }
    } catch (error) {
      operationStatus.set('error');
      outputLines.update(prevLines => [...prevLines, `\n✗ Stream error: ${error.message || error}`]);
    }
  }
  
  // Update available environments when deployment changes
  $: if (newModuleDeployment && $config) {
    const deployment = $config.deployments[newModuleDeployment];
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
    if ($config && $config.defaultModule) {
      newModuleDeployment = $config.defaultModule.Tenant || '';
      newModuleSourceEnv = $config.defaultModule.Environment || '';
      newModuleTargetEnvs = $config.defaultModule.DeploymentTargets || [];
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
    
    const requestData = {
      category: newModuleCategory,
      moduleName: newModuleName,
      deployment: newModuleDeployment,
      sourceEnvironment: newModuleSourceEnv,
      targetEnvironments: newModuleTargetEnvs,
      deploy: newModuleDeploy
    };
    
    console.log('Creating module with data:', requestData);
    
    activeOperation.set('create-module');
    operationStatus.set('running');
    outputLines.set([]);
    showCreateModuleDialog = false;
    
    try {
      const response = await fetch('/api/modules/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
      
      await streamResponse(response);
      await loadModules(); // Reload modules after creation
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }
  
  async function createRelease(module) {
    activeOperation.set(`release-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
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
      
      // Reload modules after successful release (version unchanged, just rebuild)
      if ($operationStatus === 'success') {
        await loadModules();
      }
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }
  
  // Version Management Functions
  function startEditingVersion(module) {
    editingVersionModule = module;
    editVersionValue = module.version || '1.0.0.0';
  }
  
  function cancelEditingVersion() {
    editingVersionModule = null;
    editVersionValue = '';
  }
  
  function incrementVersion(part) {
    const parts = editVersionValue.split('.').map(p => parseInt(p) || 0);
    while (parts.length < 4) parts.push(0);
    
    if (part === 'major') {
      parts[0]++;
      parts[1] = 0;
      parts[2] = 0;
      parts[3] = 0;
    } else if (part === 'minor') {
      parts[1]++;
      parts[2] = 0;
      parts[3] = 0;
    } else if (part === 'build') {
      parts[2]++;
      parts[3] = 0;
    } else if (part === 'revision') {
      parts[3]++;
    }
    
    editVersionValue = parts.join('.');
  }
  
  function isValidVersion(version) {
    return /^\d+\.\d+\.\d+\.\d+$/.test(version);
  }
  
  async function updateVersion() {
    if (!editingVersionModule || !isValidVersion(editVersionValue)) {
      return;
    }
    
    // Close the editor and open the modal
    const module = editingVersionModule;
    const version = editVersionValue;
    cancelEditingVersion();
    
    // Use the same modal system as deployments
    activeOperation.set(`version-${module.name}`);
    operationStatus.set('running');
    outputLines.set([]);
    
    try {
      const response = await fetch('/api/version', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: module.deployment,
          category: module.category,
          module: module.name,
          version: version
        })
      });
      
      await streamResponse(response);
      
      // Reload modules after successful update
      if ($operationStatus === 'success') {
        await loadModules();
      }
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
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

<Header title="🎯 Deploy" description="Manage and deploy Power Platform solutions">
  <button class="btn btn-primary" on:click={openCreateModuleDialog}>+ New Module</button>
</Header>

<main>
  
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
              {#if draggedEnvironment}
                <!-- Module becomes a drop zone when environment is being dragged -->
                <div 
                  class="drop-zone module-drop-zone {dragOverZone?.module === module.name ? 'drag-over-reverse' : ''}"
                  on:dragover={(e) => handleDragOver(e, { action: 'sync-from', module: module.name })}
                  on:dragleave={handleDragLeave}
                  on:drop={(e) => handleEnvDropOnModule(e, module)}>
                  
                  <div class="zone-content">
                    <div class="zone-icon">⬇️</div>
                    <div class="zone-title">{module.name}</div>
                    <div class="zone-hint">Drop to sync FROM {draggedEnvironment.name}</div>
                  </div>
                </div>
              {:else}
                <!-- Normal module card (draggable to environments) -->
                <div 
                  class="module-card"
                  draggable="true"
                  on:dragstart={(e) => handleDragStart(e, module)}
                  on:dragend={handleDragEnd}>
                
                <div class="module-header">
                  <div class="module-name">{module.name}</div>
                  <div class="header-buttons">
                    <button 
                      class="icon-btn push-btn" 
                      title="Push to {module.sourceEnvironment} (unmanaged)"
                      on:click|stopPropagation={() => pushToSource(module)}>
                      ⬆️
                    </button>
                    <button 
                      class="icon-btn" 
                      title="Create Release"
                      on:click={() => createRelease(module)}>
                      📦
                    </button>
                  </div>
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
                    <span class="label">Version:</span>
                    <span class="value version">{module.version}</span>
                    <button 
                      class="version-edit-btn" 
                      title="Update Version"
                      on:click|stopPropagation={() => startEditingVersion(module)}>
                      ✏️
                    </button>
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
                
                {#if editingVersionModule?.name === module.name}
                  <div class="version-editor">
                    <div class="version-editor-header">
                      <strong>Update Version</strong>
                      <button class="icon-btn-small" on:click={cancelEditingVersion}>✕</button>
                    </div>
                    
                    <div class="version-input-row">
                      <input 
                        type="text" 
                        bind:value={editVersionValue}
                        placeholder="1.0.0.0"
                        class:invalid={!isValidVersion(editVersionValue)} />
                      <button 
                        class="btn btn-primary btn-small"
                        disabled={!isValidVersion(editVersionValue)}
                        on:click={updateVersion}>
                        Update
                      </button>
                    </div>
                    
                    <div class="version-increment-buttons">
                      <button class="btn btn-secondary btn-tiny" on:click={() => incrementVersion('major')}>Maj</button>
                      <button class="btn btn-secondary btn-tiny" on:click={() => incrementVersion('minor')}>Min</button>
                      <button class="btn btn-secondary btn-tiny" on:click={() => incrementVersion('build')}>Bld</button>
                      <button class="btn btn-secondary btn-tiny" on:click={() => incrementVersion('revision')}>Rev</button>
                    </div>
                  </div>
                {/if}
                
                <div class="module-hint">
                  Drag to deploy →
                </div>
              </div>
              {/if}
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
        <div class="section-header-with-options">
          <h2>⬇️ Local (Sync From)</h2>
          <label class="sync-option">
            <input type="checkbox" bind:checked={autoIncrementOnSync} />
            <span>Auto-increment revision</span>
          </label>
        </div>
        
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
          {#each $tenants as tenant, index}
            <button
              class="tenant-tab {selectedTenantIndex === index ? 'active' : ''}"
              on:click={() => selectedTenantIndex = index}>
              <span class="tenant-icon">🏢</span>
              {tenant.name}
            </button>
          {/each}
        </div>
        
      <div class="tenant-list">
        {#if $tenants[selectedTenantIndex]}
          {@const tenant = $tenants[selectedTenantIndex]}
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
                  <!-- Environment zones are draggable when not in module-drag mode -->
                  <div 
                    class="placeholder-zone environment-placeholder {draggedEnvironment?.environment === env.name ? 'dragging' : ''}"
                    draggable="true"
                    on:dragstart={(e) => handleEnvDragStart(e, { name: env.name, key: env.key, tenant: tenant.name, deployment: deployment.name })}
                    on:dragend={handleEnvDragEnd}>
                    <div class="placeholder-text">{env.name}</div>
                    <div class="drag-hint">↖️ Drag to module to sync FROM this environment</div>
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
            <p class="hint">Drag modules → environments to deploy</p>
            <p class="hint">Drag environments → modules to sync FROM</p>
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
                  {:else if item.type === 'sync-from'}
                    ⬆️ Sync FROM
                  {:else if item.type === 'deploy'}
                    {#if item.isSourceEnv}
                      ⬆️ Push
                    {:else}
                      📤 Deploy
                    {/if}
                  {:else if item.type === 'ship'}
                    🚢 Ship
                  {/if}
                  <strong>{item.module.name}</strong>
                </div>
              </div>
              
              <div class="queue-item-details">
                {#if item.type === 'sync'}
                  <div class="detail">From: {item.module.sourceEnvironment}</div>
                {:else if item.type === 'sync-from'}
                  <div class="detail">⚠️ FROM: {item.environment}</div>
                  <div class="detail">Deployment: {item.deployment}</div>
                  <div class="detail" style="color: #ff9800; font-size: 11px;">Will overwrite local files</div>
                {:else if item.type === 'deploy'}
                  <div class="detail">To: {item.environment}</div>
                  <div class="detail">Tenant: {item.tenant || item.module.tenant}</div>
                  {#if item.status === 'queued'}
                    {#if !item.isSourceEnv && !item.forceUnmanaged}
                      <label class="upgrade-checkbox">
                        <input 
                          type="checkbox" 
                          checked={item.upgrade}
                          on:change={() => toggleQueueItemUpgrade(item.id)}
                          disabled={queueExecuting} />
                        <span>Upgrade (delete removed components)</span>
                      </label>
                    {/if}
                    {#if !item.isSourceEnv}
                      <label class="upgrade-checkbox">
                        <input 
                          type="checkbox" 
                          checked={item.forceUnmanaged}
                          on:change={() => toggleQueueItemUnmanaged(item.id)}
                          disabled={queueExecuting} />
                        <span>🔓 Deploy as Unmanaged (override)</span>
                      </label>
                    {/if}
                  {/if}
                {:else if item.type === 'ship'}
                  <div class="detail">To: {item.environment}</div>
                  <div class="detail">Tenant: {item.tenant}</div>
                  {#if item.status === 'queued'}
                    <label class="upgrade-checkbox">
                      <input 
                        type="checkbox" 
                        checked={item.forceUnmanaged}
                        on:change={() => toggleQueueItemUnmanaged(item.id)}
                        disabled={queueExecuting} />
                      <span>🔓 Ship as Unmanaged (override)</span>
                    </label>
                  {/if}
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
  
  <!-- Sync-From Confirmation Dialog -->
  {#if showSyncFromDialog && syncFromDialogData}
    <div class="dialog-overlay" on:click={cancelSyncFrom}>
      <div class="dialog warning-dialog" on:click={(e) => e.stopPropagation()}>
        <h2>⚠️ Sync FROM Environment</h2>
        
        <div class="warning-content">
          <p><strong>Module:</strong> {syncFromDialogData.module.name}</p>
          <p><strong>Source Environment:</strong> {syncFromDialogData.environment.name}</p>
          <p><strong>Deployment:</strong> {syncFromDialogData.environment.deployment}</p>
          
          <div class="warning-box">
            <p><strong>⚠️ Warning:</strong></p>
            <p>This will OVERWRITE your local module files with the solution from the selected environment.</p>
            <p>Use this for rare "hotfix" scenarios where you need to pull changes from a non-default environment.</p>
            <p><strong>Make sure you have committed any local changes before proceeding!</strong></p>
          </div>
        </div>
        
        <div class="dialog-actions">
          <button class="btn btn-primary" on:click={confirmSyncFrom}>
            ✓ Add to Queue
          </button>
          <button class="btn btn-secondary" on:click={cancelSyncFrom}>
            ✕ Cancel
          </button>
        </div>
      </div>
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
  
  <!-- Output Stream Component -->
  <OutputStream />
  
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
    padding: 0 2rem 2rem 2rem;
    max-width: 2400px;
    margin: 0 auto;
    display: block;
  }
  
  main > *:last-child {
    margin-bottom: 0;
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
    margin: 0 0 1.25rem 0;
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
    grid-template-columns: minmax(300px, 1fr) minmax(500px, 2fr) minmax(300px, 1fr);
    gap: 20px;
    min-height: 0;
    overflow: hidden;
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
    max-height: calc(100vh - 280px);
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
  
  .upgrade-checkbox {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 6px;
    font-size: 12px;
    color: #cccccc;
    cursor: pointer;
  }
  
  .upgrade-checkbox input[type="checkbox"] {
    cursor: pointer;
  }
  
  .upgrade-checkbox input[type="checkbox"]:disabled {
    cursor: not-allowed;
  }
  
  .upgrade-checkbox span {
    user-select: none;
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
  
  .section-header-with-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .section-header-with-options h2 {
    margin: 0;
  }
  
  .sync-option {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #cccccc;
    cursor: pointer;
    user-select: none;
  }
  
  .sync-option input[type="checkbox"] {
    cursor: pointer;
    width: 14px;
    height: 14px;
  }
  
  .sync-option span {
    cursor: pointer;
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
  
  .header-buttons {
    display: flex;
    gap: 6px;
    align-items: center;
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
  
  .push-btn {
    font-size: 16px;
    opacity: 0.6;
  }
  
  .push-btn:hover {
    opacity: 0.9;
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
  
  .meta-item .version {
    color: #a5d6a7;
    font-weight: 600;
    font-family: 'Courier New', monospace;
  }
  
  .version-edit-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 12px;
    padding: 0 4px;
    opacity: 0.6;
    transition: opacity 0.2s;
    margin-left: 4px;
  }
  
  .version-edit-btn:hover {
    opacity: 1;
  }
  
  .version-editor {
    background: #1e1e1e;
    border: 1px solid #0078d4;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
  }
  
  .version-editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    color: #ffffff;
  }
  
  .icon-btn-small {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 2px 4px;
    opacity: 0.7;
    color: #ffffff;
  }
  
  .icon-btn-small:hover {
    opacity: 1;
  }
  
  .version-input-row {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }
  
  .version-input-row input {
    flex: 0 1 auto;
    min-width: 0;
    max-width: 140px;
    padding: 6px 10px;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    background: #252526;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    font-size: 14px;
  }
  
  .version-input-row input:focus {
    outline: none;
    border-color: #0078d4;
  }
  
  .version-input-row input.invalid {
    border-color: #f44336;
  }
  
  .version-increment-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
  }
  
  .btn-tiny {
    padding: 4px 8px;
    font-size: 11px;
    white-space: nowrap;
    flex-shrink: 0;
  }
  
  .btn-small {
    padding: 6px 12px;
    font-size: 12px;
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
  
  /* Bidirectional drag styles */
  .module-drop-zone {
    border: 2px dashed #ff9800;
    background: #3d2a1f;
  }
  
  .module-drop-zone.drag-over-reverse {
    border-color: #ff9800;
    background: #5d3a2f;
    transform: scale(1.02);
  }
  
  .zone-hint {
    font-size: 11px;
    color: #ff9800;
    margin-top: 4px;
  }
  
  .drag-hint {
    font-size: 10px;
    color: #999999;
    margin-top: 4px;
    opacity: 0.7;
  }
  
  .environment-placeholder.dragging {
    opacity: 0.5;
    border-color: #ff9800;
  }
  
  .environment-placeholder:hover {
    border-color: #ff9800;
    background: #2d2d30;
    cursor: grab;
  }
  
  .environment-placeholder:hover .drag-hint {
    opacity: 1;
    color: #ff9800;
  }
  
  /* Warning dialog */
  .warning-dialog {
    max-width: 500px;
  }
  
  .warning-content {
    margin: 20px 0;
    color: #cccccc;
  }
  
  .warning-content p {
    margin: 8px 0;
  }
  
  .warning-box {
    background: #3d2a1f;
    border: 2px solid #ff9800;
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
  }
  
  .warning-box p {
    margin: 6px 0;
    color: #ff9800;
  }
  
  .warning-box p:first-child {
    font-weight: 700;
    font-size: 14px;
  }
</style>

