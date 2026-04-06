<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';
  import OutputStream from '../lib/OutputStream.svelte';
  import { 
    config, 
    deployments, 
    outputLines, 
    operationStatus,
    streamResponse 
  } from '../lib/stores.js';

  let selectedDeployment = '';
  let selectedEnvironment = '';
  let selectedModule = '';
  let publisherPrefix = 'appbase_';
  let mode = 'interactive';
  
  let modules = [];
  let tables = [];
  let isLoading = false;
  let isPreviewing = false;
  let isExecuting = false;
  
  // Selected table for detailed view
  let selectedTable = null;
  let activeTab = 'planned';  // 'completed', 'completedLastRound', 'planned'
  
  // Current prompt state (for interactive mode)
  let currentPrompt = null;
  
  $: availableEnvironments = getAvailableEnvironments($config, selectedDeployment);
  
  let hasRestoredState = false;
  
  // Restore deployment and environment once deployments are loaded
  $: if ($deployments && $deployments.length > 0 && !hasRestoredState) {
    const savedDeployment = localStorage.getItem('batchFieldCreator_deployment');
    if (savedDeployment && $deployments.includes(savedDeployment)) {
      selectedDeployment = savedDeployment;
    }
    hasRestoredState = true;
  }
  
  // Restore environment once availableEnvironments are populated
  $: if (availableEnvironments.length > 0 && selectedDeployment) {
    const savedEnvironment = localStorage.getItem('batchFieldCreator_environment');
    if (savedEnvironment && availableEnvironments.some(env => env.key === savedEnvironment)) {
      if (!selectedEnvironment || selectedEnvironment !== savedEnvironment) {
        selectedEnvironment = savedEnvironment;
      }
    }
  }
  
  onMount(async () => {
    // Load saved settings
    const savedPrefix = localStorage.getItem('publisherPrefix');
    if (savedPrefix) {
      publisherPrefix = savedPrefix;
    }
    
    // Load available modules
    await loadModules();
    
    // Restore saved module if it's still valid
    const savedModule = localStorage.getItem('batchFieldCreator_module');
    if (savedModule && modules.some(m => m.path === savedModule)) {
      selectedModule = savedModule;
      // previewTables will be called automatically via reactive statement
    }
  });
  
  $: if (selectedDeployment) {
    localStorage.setItem('batchFieldCreator_deployment', selectedDeployment);
  }
  
  $: if (selectedEnvironment) {
    localStorage.setItem('batchFieldCreator_environment', selectedEnvironment);
  }
  
  $: if (selectedModule) {
    localStorage.setItem('batchFieldCreator_module', selectedModule);
  }
  
  $: if (publisherPrefix) {
    localStorage.setItem('publisherPrefix', publisherPrefix);
  }
  
  // Auto-preview when module changes
  $: if (selectedModule && !isExecuting) {
    previewTables();
  }
  
  function getAvailableEnvironments(cfg, deployment) {
    if (!cfg || !deployment || !cfg.deployments || !cfg.deployments[deployment]) {
      return [];
    }
    const dep = cfg.deployments[deployment];
    if (dep.Environments) {
      return Object.entries(dep.Environments).map(([key, env]) => ({
        key,
        name: env.Name || key
      }));
    }
    return [];
  }
  
  async function loadModules() {
    isLoading = true;
    try {
      const response = await fetch('/api/helpers/scan-modules');
      const data = await response.json();
      modules = data.modules || [];
    } catch (error) {
      console.error('Error loading modules:', error);
      modules = [];
    } finally {
      isLoading = false;
    }
  }
  
  async function previewTables() {
    if (!selectedModule) {
      alert('Please select a module');
      return;
    }
    
    isPreviewing = true;
    tables = [];
    selectedTable = null;  // Clear selection on new preview
    
    try {
      const params = new URLSearchParams({
        module_path: selectedModule,
        publisher_prefix: publisherPrefix
      });
      
      const response = await fetch(`/api/helpers/preview-tables?${params}`);
      
      const data = await response.json();
      
      if (data.error) {
        alert('Error: ' + data.error);
        tables = [];
      } else {
        tables = data.tables || [];
        
        if (tables.length === 0) {
          alert('No tables with Planned fields found in BUILD.md');
        } else {
          // Restore previously selected table if it's still valid
          const savedTableName = localStorage.getItem('batchFieldCreator_selectedTable');
          if (savedTableName) {
            const savedTable = tables.find(t => t.tableName === savedTableName);
            if (savedTable) {
              selectedTable = savedTable;
            }
          }
        }
      }
    } catch (error) {
      console.error('Error previewing tables:', error);
      alert('Error previewing tables: ' + error.message);
    } finally {
      isPreviewing = false;
    }
  }
  
  function selectTable(table) {
    selectedTable = table;
    
    // Restore saved active tab if available, otherwise default to 'planned'
    const savedTab = localStorage.getItem('batchFieldCreator_activeTab');
    if (savedTab && ['planned', 'completed', 'completedLastRound'].includes(savedTab)) {
      activeTab = savedTab;
    } else {
      activeTab = 'planned';
    }
    
    // Save selected table name
    if (table) {
      localStorage.setItem('batchFieldCreator_selectedTable', table.tableName);
    }
  }
  
  // Save active tab when it changes
  $: if (activeTab) {
    localStorage.setItem('batchFieldCreator_activeTab', activeTab);
  }
  
  async function createSingleTable() {
    if (!selectedDeployment || !selectedEnvironment || !selectedTable || !selectedModule) {
      alert('Please select deployment, environment, and table');
      return;
    }
    
    if (selectedTable.sections.planned.length === 0) {
      alert('No planned fields to create for this table');
      return;
    }
    
    if (!confirm(`Create ${selectedTable.sections.planned.length} fields for table "${selectedTable.tableName}"?`)) {
      return;
    }
    
    isExecuting = true;
    const prevSelectedTable = selectedTable;
    selectedTable = null;  // Clear selection to show output stream
    $outputLines = [];
    $operationStatus = 'running';
    
    const operationId = `single-${Date.now()}`;
    
    // Use a dedicated single-table endpoint that wraps the batch logic
    const url = '/api/helpers/create-single-table-fields';
    
    const requestBody = {
      deployment: selectedDeployment,
      environment: selectedEnvironment,
      modulePath: selectedModule,
      tableName: prevSelectedTable.tableName,
      publisherPrefix: publisherPrefix,
      operationId: operationId
    };
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      await streamResponse(response);
      
      // Refresh preview to show updated state (BUILD.md updated by backend)
      await previewTables();
      
      // Re-select the table to show updated field lists
      const updatedTable = tables.find(t => t.tableName === prevSelectedTable.tableName);
      if (updatedTable) {
        selectedTable = updatedTable;
      }
      
    } catch (error) {
      console.error('Single table creation error:', error);
      $operationStatus = 'error';
      $outputLines = [...$outputLines, `\n✗ Connection error: ${error.message}`];
      alert('Error creating fields. Check output for details.');
    } finally {
      isExecuting = false;
    }
  }
  
  async function startBatchCreation() {
    if (!selectedDeployment || !selectedEnvironment || !selectedModule) {
      alert('Please select deployment, environment, and module');
      return;
    }
    
    const totalTables = tables.length;
    const totalFields = tables.reduce((sum, t) => sum + t.sections.planned.length, 0);
    
    const confirmMsg = mode === 'interactive' 
      ? `Create fields for ${totalTables} tables (${totalFields} total fields)?\n\nNote: Interactive mode is not fully implemented yet - this will process all tables automatically without prompting.`
      : `Create fields for ${totalTables} tables (${totalFields} total fields)?\n\nThis will process all tables automatically.`;
    
    if (!confirm(confirmMsg)) {
      return;
    }
    
    isExecuting = true;
    selectedTable = null;  // Clear selection to show output stream
    $outputLines = [];
    $operationStatus = 'running';
    currentPrompt = null;
    
    const operationId = `batch-${Date.now()}`;
    const url = '/api/helpers/batch-create-fields-from-buildmd';
    
    const requestBody = {
      deployment: selectedDeployment,
      environment: selectedEnvironment,
      modulePath: selectedModule,
      publisherPrefix: publisherPrefix,
      mode: mode,
      operationId: operationId
    };
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      await streamResponse(response);
      
      // Refresh preview after batch creation to show updated state
      await previewTables();
    } catch (error) {
      console.error('Batch creation error:', error);
      $operationStatus = 'error';
      $outputLines = [...$outputLines, `\n✗ Connection error: ${error.message}`];
      alert('Error creating fields. Check output for details.');
    } finally {
      isExecuting = false;
      currentPrompt = null;
    }
  }
  
  function respondToPrompt(action) {
    // For now, just auto-continue (full interactive implementation would need WebSocket)
    if (action === 'resume_all') {
      mode = 'auto';
    }
    currentPrompt = null;
  }
</script>

<div class="batch-field-creator">
  <Header title="⚡ Batch Field Creator" description="Create fields from BUILD.md - click a table to create just that one, or use batch mode">
    <button class="btn btn-primary" on:click={startBatchCreation} disabled={!selectedModule || isExecuting || $operationStatus === 'running'}>
      {isExecuting ? '⏳ Creating...' : '▶ Create All Tables'}
    </button>
  </Header>

  <!-- Toolbar -->
  <div class="toolbar">
    <div class="toolbar-row">
      <select class="toolbar-select" bind:value={selectedDeployment} disabled={isExecuting}>
        <option value="">Deployment</option>
        {#each $deployments || [] as deployment}
          <option value={deployment}>{deployment}</option>
        {/each}
      </select>

      <select class="toolbar-select" bind:value={selectedEnvironment} disabled={!selectedDeployment || isExecuting}>
        <option value="">Environment</option>
        {#each availableEnvironments as env}
          <option value={env.key}>{env.name}</option>
        {/each}
      </select>

      <input 
        type="text" 
        class="toolbar-input"
        bind:value={publisherPrefix}
        disabled={isExecuting}
        placeholder="Publisher Prefix (e.g., appbase_)"
      />

      <select class="toolbar-select module-select" bind:value={selectedModule} disabled={isExecuting || isLoading}>
        <option value="">-- Select Module --</option>
        {#each modules as module}
          <option value={module.path}>{module.displayName}</option>
        {/each}
      </select>

      <select class="toolbar-select" bind:value={mode} disabled={isExecuting}>
        <option value="interactive">Interactive</option>
        <option value="auto">Auto</option>
      </select>
    </div>
  </div>

  <div class="content">
    <div class="main-container">
      <!-- Left Column: Preview -->
      <div class="left-column">
        {#if isPreviewing}
          <div class="preview-section empty">
            <h3>📋 Preview</h3>
            <p class="empty-state">⏳ Loading tables...</p>
          </div>
        {:else if tables.length > 0}
          <div class="preview-section">
            <div class="section-header-row">
              <h3>📋 Tables to Process ({tables.length})</h3>
              <button 
                class="btn-refresh" 
                on:click={async () => {
                  const currentTableName = selectedTable?.tableName;
                  await previewTables();
                  // Re-select the table if it still exists
                  if (currentTableName && tables.length > 0) {
                    const table = tables.find(t => t.tableName === currentTableName);
                    if (table) selectedTable = table;
                  }
                }}
                disabled={isPreviewing}
                title="Refresh table list"
              >
                🔄
              </button>
            </div>
            <div class="tables-list">
              {#each tables as table}
                <div 
                  class="table-item" 
                  class:selected={selectedTable === table}
                  on:click={() => selectTable(table)}
                  role="button"
                  tabindex="0"
                  on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectTable(table); }}
                >
                  <div class="table-info">
                    <div class="table-name">{table.tableName}</div>
                    <div class="field-count">
                      {table.sections.planned.length} planned
                      {#if table.sections.completed.length > 0}
                        • {table.sections.completed.length} completed
                      {/if}
                      {#if table.sections.completedLastRound.length > 0}
                        • {table.sections.completedLastRound.length} last round
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {:else}
          <div class="preview-section empty">
            <h3>📋 Preview</h3>
            <p class="empty-state">Select a module to see tables</p>
          </div>
        {/if}
      </div>

      <!-- Right Column: Field Details or Output -->
      <div class="right-column">
        {#if selectedTable && !isExecuting}
          <div class="field-detail-section">
            <div class="section-header-row">
              <h3>📝 {selectedTable.tableName}</h3>
              <button 
                class="btn-create-single" 
                on:click={createSingleTable}
                disabled={selectedTable.sections.planned.length === 0}
                title="Create fields for just this table"
              >
                ▶ Create Fields
              </button>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
              <button 
                class="tab" 
                class:active={activeTab === 'planned'}
                on:click={() => activeTab = 'planned'}
              >
                Planned ({selectedTable.sections.planned.length})
              </button>
              <button 
                class="tab" 
                class:active={activeTab === 'completed'}
                on:click={() => activeTab = 'completed'}
                disabled={selectedTable.sections.completed.length === 0}
              >
                Completed ({selectedTable.sections.completed.length})
              </button>
              <button 
                class="tab" 
                class:active={activeTab === 'completedLastRound'}
                on:click={() => activeTab = 'completedLastRound'}
                disabled={selectedTable.sections.completedLastRound.length === 0}
              >
                Last Round ({selectedTable.sections.completedLastRound.length})
              </button>
            </div>
            
            <!-- Field List -->
            <div class="field-list">
              {#if activeTab === 'planned' && selectedTable.sections.planned.length > 0}
                {#each selectedTable.sections.planned as field}
                  <div class="field-item planned">{field}</div>
                {/each}
              {:else if activeTab === 'completed' && selectedTable.sections.completed.length > 0}
                {#each selectedTable.sections.completed as field}
                  <div class="field-item completed">{field}</div>
                {/each}
              {:else if activeTab === 'completedLastRound' && selectedTable.sections.completedLastRound.length > 0}
                {#each selectedTable.sections.completedLastRound as field}
                  <div class="field-item completed-last">{field}</div>
                {/each}
              {:else}
                <div class="empty-state">No fields in this section</div>
              {/if}
            </div>
          </div>
        {:else}
          <div class="output-section">
            <h3>📄 Output</h3>
            <OutputStream lines={$outputLines} status={$operationStatus} />
          </div>
        {/if}
      </div>
    </div>
  </div>

  {#if currentPrompt}
    <div class="prompt-overlay">
      <div class="prompt-dialog">
        <h3>Table {currentPrompt.index}/{currentPrompt.total}</h3>
        <p class="table-name-prompt">{currentPrompt.table}</p>
        <p class="prompt-text">Create fields for this table?</p>
        
        <div class="prompt-buttons">
          <button class="btn-create" on:click={() => respondToPrompt('create')}>
            ✓ Create
          </button>
          <button class="btn-skip" on:click={() => respondToPrompt('skip')}>
            ⊘ Skip
          </button>
          <button class="btn-resume-all" on:click={() => respondToPrompt('resume_all')}>
            ▶ Resume All
          </button>
          <button class="btn-exit" on:click={() => respondToPrompt('exit')}>
            ✗ Exit
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .batch-field-creator {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #1e1e1e;
    color: #e0e0e0;
  }

  /* Toolbar */
  .toolbar {
    background: #252526;
    border-radius: 6px;
    padding: 1rem;
    margin: 0 2rem 1.25rem 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    border: 1px solid #3c3c3c;
  }

  .toolbar-row {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }

  .toolbar-select {
    padding: 10px 16px;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    min-width: 180px;
    cursor: pointer;
  }

  .toolbar-select.module-select {
    flex: 1;
    min-width: 250px;
  }

  .toolbar-select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .toolbar-select:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  .toolbar-input {
    padding: 10px 16px;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    min-width: 200px;
  }

  .toolbar-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .toolbar-input:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  /* Content */
  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .main-container {
    flex: 1;
    overflow-y: auto;
    padding: 0 2rem 1.25rem 2rem;
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 1.5rem;
    align-items: start;
  }

  .left-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .right-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 0;
  }

  /* Sections */
  .preview-section {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
  }

  .preview-section.empty {
    text-align: center;
    padding: 2rem 1rem;
  }

  .empty-state {
    color: #858585;
    font-size: 14px;
    margin: 0;
  }

  .output-section {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: calc(100vh - 280px);
  }

  h3 {
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 1rem 0;
  }

  /* Tables List */
  .tables-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: calc(100vh - 340px);
    overflow-y: auto;
  }

  .table-item {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .table-item:hover {
    background: #2d2d30;
    border-color: #4c4c4c;
  }

  .table-item.selected {
    background: #094771;
    border-color: #0078d4;
  }

  .table-item.selected:hover {
    background: #0d5a8a;
  }

  .table-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .table-name {
    font-weight: 500;
    color: #e0e0e0;
    font-size: 14px;
  }

  .field-count {
    color: #858585;
    font-size: 12px;
  }

  /* Prompt Overlay */
  .prompt-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .prompt-dialog {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 2rem;
    min-width: 400px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
  }
  
  .prompt-dialog h3 {
    margin-top: 0;
    margin-bottom: 0.5rem;
    color: #e0e0e0;
    font-size: 18px;
  }
  
  .table-name-prompt {
    font-size: 16px;
    font-weight: 600;
    color: #0078d4;
    margin: 1rem 0;
  }
  
  .prompt-text {
    margin: 1rem 0 1.5rem;
    color: #cccccc;
    font-size: 14px;
  }
  
  .prompt-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  
  .prompt-buttons button {
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid transparent;
  }
  
  .btn-create {
    background: #107c10;
    color: white;
    border-color: #107c10;
  }
  
  .btn-create:hover {
    background: #0e6b0e;
  }
  
  .btn-skip {
    background: #ca5010;
    color: white;
    border-color: #ca5010;
  }
  
  .btn-skip:hover {
    background: #a74109;
  }
  
  .btn-resume-all {
    background: #0078d4;
    color: white;
    border-color: #0078d4;
  }
  
  .btn-resume-all:hover {
    background: #106ebe;
  }
  
  .btn-exit {
    background: #3c3c3c;
    color: #e0e0e0;
    border-color: #3c3c3c;
  }
  
  .btn-exit:hover {
    background: #505050;
  }

  /* Field Detail Section */
  .field-detail-section {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: calc(100vh - 280px);
  }

  .field-detail-section h3 {
    margin-bottom: 0.75rem;
  }

  .section-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .section-header-row h3 {
    margin: 0;
  }

  .btn-create-single {
    padding: 8px 16px;
    background: #0e639c;
    border: 1px solid #0078d4;
    border-radius: 4px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
  }

  .btn-refresh {
    padding: 6px 10px;
    background: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn-refresh:hover:not(:disabled) {
    background: #505050;
    border-color: #0078d4;
  }

  .btn-refresh:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-create-single:hover:not(:disabled) {
    background: #1177bb;
  }

  .btn-create-single:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Tabs */
  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #3c3c3c;
    padding-bottom: 0.5rem;
  }

  .tab {
    padding: 8px 16px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #858585;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .tab:hover:not(:disabled) {
    color: #e0e0e0;
    background: #2d2d30;
    border-radius: 4px 4px 0 0;
  }

  .tab.active {
    color: #0078d4;
    border-bottom-color: #0078d4;
  }

  .tab:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Field List */
  .field-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 0;
  }

  .field-item {
    padding: 10px 14px;
    margin-bottom: 0.5rem;
    border-radius: 4px;
    border-left: 3px solid;
    font-size: 13px;
    font-family: 'Consolas', 'Monaco', monospace;
    background: #1e1e1e;
  }

  .field-item.planned {
    border-left-color: #0078d4;
    color: #d4d4d4;
  }

  .field-item.completed {
    border-left-color: #107c10;
    color: #b4b4b4;
    opacity: 0.8;
  }

  .field-item.completed-last {
    border-left-color: #ca5010;
    color: #b4b4b4;
    opacity: 0.7;
  }
</style>
