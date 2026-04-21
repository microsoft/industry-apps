<script>
  import { onMount } from 'svelte';
  import ModuleSelector from '../lib/ModuleSelector.svelte';
  import EventStreamViewer from '../lib/EventStreamViewer.svelte';

  // Module selection
  let selectedModule = '';

  // Active tab
  let activeTab = 'data-models'; // data-models, processes, scenarios, simulations

  // Data models state
  let generatingDataModels = false;
  let dataModelsList = [];
  let selectedDataModel = null;
  let dataModelsContent = '';

  // File lists for each type
  let processesList = [];
  let scenariosList = [];
  let simulationsList = [];

  // Selected files
  let selectedProcess = null;
  let selectedScenario = null;
  let selectedSimulation = null;

  // File content editors
  let processContent = '';
  let scenarioContent = '';
  let simulationContent = '';

  // Editing state
  let editingProcess = false;
  let editingScenario = false;
  let editingSimulation = false;

  // New file modals
  let showNewProcessModal = false;
  let showNewScenarioModal = false;
  let showImportSimulationModal = false;
  let newFileName = '';
  let importSimulationContent = '';

  // Validation state
  let validating = false;
  let validationResult = null;

  // Dry run state
  let runningDryRun = false;
  let dryRunResult = null;

  // Execution state
  let executing = false;
  let executionResult = null;

  // Load files when module changes
  $: if (selectedModule) {
    loadAllFiles();
  }

  // Handle module selection change
  function handleModuleChange(event) {
    selectedModule = event.detail.path;
  }

  async function loadAllFiles() {
    await checkDataModels();
    await loadFiles('processes');
    await loadFiles('scenarios');
    await loadFiles('simulations');
  }

  async function checkDataModels() {
    if (!selectedModule) return;

    try {
      const response = await fetch('/api/process-sim/files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          file_type: 'data-models'
        })
      });

      const data = await response.json();
      
      if (data.files && data.files.length > 0) {
        dataModelsList = data.files.sort((a, b) => a.name.localeCompare(b.name));
        // Auto-select first table if none selected
        if (!selectedDataModel && dataModelsList.length > 0) {
          await selectDataModel(dataModelsList[0]);
        }
      } else {
        dataModelsList = [];
        selectedDataModel = null;
        dataModelsContent = '';
      }
    } catch (error) {
      console.error('Error checking data models:', error);
    }
  }

  async function selectDataModel(file) {
    selectedDataModel = file;
    
    try {
      const response = await fetch('/api/process-sim/file/read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: file.path })
      });
      const data = await response.json();
      dataModelsContent = data.content;
    } catch (error) {
      console.error('Error loading data model:', error);
      dataModelsContent = '';
    }
  }

  async function loadFiles(fileType) {
    if (!selectedModule) return;

    try {
      const response = await fetch('/api/process-sim/files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          file_type: fileType
        })
      });

      const data = await response.json();
      
      if (fileType === 'processes') {
        processesList = data.files || [];
      } else if (fileType === 'scenarios') {
        scenariosList = data.files || [];
      } else if (fileType === 'simulations') {
        simulationsList = data.files || [];
      }
    } catch (error) {
      console.error(`Error loading ${fileType}:`, error);
    }
  }

  async function generateDataModels() {
    if (!selectedModule) return;

    generatingDataModels = true;

    try {
      const response = await fetch('/api/process-sim/generate-data-models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_path: selectedModule })
      });

      const data = await response.json();
      
      if (data.success) {
        await checkDataModels();
        activeTab = 'data-models';
      } else {
        alert('Error generating data models: ' + data.error);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      generatingDataModels = false;
    }
  }

  async function selectFile(fileType, file) {
    try {
      const response = await fetch('/api/process-sim/file/read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: file.path })
      });

      const data = await response.json();
      
      if (fileType === 'processes') {
        selectedProcess = file;
        processContent = data.content;
        editingProcess = false;
      } else if (fileType === 'scenarios') {
        selectedScenario = file;
        scenarioContent = data.content;
        editingScenario = false;
      } else if (fileType === 'simulations') {
        selectedSimulation = file;
        simulationContent = data.content;
        editingSimulation = false;
      }
    } catch (error) {
      console.error('Error loading file:', error);
    }
  }

  async function saveFile(fileType) {
    let filePath, content;

    if (fileType === 'processes') {
      filePath = selectedProcess.path;
      content = processContent;
    } else if (fileType === 'scenarios') {
      filePath = selectedScenario.path;
      content = scenarioContent;
    } else if (fileType === 'simulations') {
      filePath = selectedSimulation.path;
      content = simulationContent;
    }

    try {
      const response = await fetch('/api/process-sim/file/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          content: content,
          create_dirs: true
        })
      });

      const data = await response.json();
      
      if (data.success) {
        if (fileType === 'processes') editingProcess = false;
        else if (fileType === 'scenarios') editingScenario = false;
        else if (fileType === 'simulations') editingSimulation = false;
        
        await loadFiles(fileType);
      }
    } catch (error) {
      alert('Error saving file: ' + error.message);
    }
  }

  async function createNewFile(fileType) {
    if (!newFileName) return;

    const filePath = `${selectedModule}/design/${fileType}/${newFileName}.yaml`;
    let templateContent = '';

    if (fileType === 'processes') {
      templateContent = `process_name: ${newFileName}
display_name: ${newFileName}
module: ${selectedModule}
description: 
version: "1.0"

personas:
  - role: 
    name: 
    responsibilities:
      - 

steps:
  - step: 1
    action: 
    description: 
    performed_by: 
    entities:
      - 
    required_fields:
      - 
    business_rules:
      - 
`;
    } else if (fileType === 'scenarios') {
      templateContent = `scenario_name: ${newFileName}
display_name: ${newFileName}
module: ${selectedModule}
process: 
version: "1.0"

context:
  description: 

personas:
  role_name:
    name: 
    personality: 
    experience_level: 
`;
    }

    try {
      const response = await fetch('/api/process-sim/file/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          content: templateContent,
          create_dirs: true
        })
      });

      const data = await response.json();
      
      if (data.success) {
        newFileName = '';
        showNewProcessModal = false;
        showNewScenarioModal = false;
        await loadFiles(fileType);
      }
    } catch (error) {
      alert('Error creating file: ' + error.message);
    }
  }

  async function importSimulation() {
    if (!importSimulationContent || !selectedModule) return;

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const fileName = `imported-${timestamp}`;
    const filePath = `${selectedModule}/design/simulations/${fileName}.yaml`;

    try {
      const response = await fetch('/api/process-sim/file/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          content: importSimulationContent,
          create_dirs: true
        })
      });

      const data = await response.json();
      
      if (data.success) {
        importSimulationContent = '';
        showImportSimulationModal = false;
        await loadFiles('simulations');
        activeTab = 'simulations';
      }
    } catch (error) {
      alert('Error importing simulation: ' + error.message);
    }
  }

  async function validateSimulation() {
    if (!selectedSimulation || !selectedModule) return;

    validating = true;
    validationResult = null;

    try {
      const response = await fetch('/api/process-sim/validate-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          event_stream_yaml: simulationContent
        })
      });

      validationResult = await response.json();
    } catch (error) {
      validationResult = { valid: false, errors: [error.message] };
    } finally {
      validating = false;
    }
  }

  async function dryRun() {
    if (!selectedSimulation || !selectedModule) return;

    runningDryRun = true;
    dryRunResult = null;

    try {
      const response = await fetch('/api/process-sim/dry-run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          event_stream_yaml: simulationContent
        })
      });

      dryRunResult = await response.json();
    } catch (error) {
      dryRunResult = { success: false, errors: [error.message] };
    } finally {
      runningDryRun = false;
    }
  }

</script>

<div class="container">
  <div class="main-content">
    <!-- Page Header with Module Selector -->
    <div class="page-header">
      <div class="header-text">
        <h1>Process Simulation</h1>
        <p class="subtitle">Generate realistic test data through simulated business workflows</p>
      </div>
      <div class="header-selector">
        <ModuleSelector 
          bind:value={selectedModule}
          on:change={handleModuleChange}
          placeholder="-- Select a module --"
        />
      </div>
    </div>

    {#if selectedModule}
      <!-- Tabs -->
      <div class="tabs">
        <button 
          class:active={activeTab === 'data-models'}
          on:click={() => activeTab = 'data-models'}
        >
          Data Models
        </button>
        <button 
          class:active={activeTab === 'processes'}
          on:click={() => activeTab = 'processes'}
        >
          Processes ({processesList.length})
        </button>
        <button 
          class:active={activeTab === 'scenarios'}
          on:click={() => activeTab = 'scenarios'}
        >
          Scenarios ({scenariosList.length})
        </button>
        <button 
          class:active={activeTab === 'simulations'}
          on:click={() => activeTab = 'simulations'}
        >
          Simulations ({simulationsList.length})
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        
        <!-- Data Models Tab -->
        {#if activeTab === 'data-models'}
          <div class="section">
            <div class="section-header">
              <h2>Data Models</h2>
              <button on:click={generateDataModels} disabled={generatingDataModels} class="primary">
                {generatingDataModels ? 'Regenerating...' : 'Refresh Data Models'}
              </button>
            </div>
            <p>Auto-generated table schemas from Entity.xml files.</p>
            
            {#if dataModelsList.length > 0}
              <div class="two-column">
                <!-- Table List -->
                <div class="file-list">
                  <h3>Tables ({dataModelsList.length})</h3>
                  <ul>
                    {#each dataModelsList as file}
                      <li 
                        class:selected={selectedDataModel?.name === file.name}
                        on:click={() => selectDataModel(file)}
                      >
                        {file.name.replace('.yaml', '').split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </li>
                    {/each}
                  </ul>
                </div>

                <!-- Table Schema Viewer -->
                <div class="file-editor">
                  {#if selectedDataModel}
                    <div class="editor-header">
                      <h3>{selectedDataModel.name.replace('.yaml', '').split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h3>
                      <div class="file-info">
                        <small>Last updated: {new Date(selectedDataModel.modified).toLocaleString()}</small>
                      </div>
                    </div>

                    <div class="file-viewer">
                      <pre>{dataModelsContent}</pre>
                    </div>
                  {:else}
                    <p class="empty">Select a table to view its schema</p>
                  {/if}
                </div>
              </div>
            {:else}
              <p class="warning">⚠ No data models found</p>
              <button on:click={generateDataModels} disabled={generatingDataModels} class="primary">
                {generatingDataModels ? 'Generating...' : 'Generate Data Models'}
              </button>
            {/if}
          </div>
        {/if}

        <!-- Processes Tab -->
        {#if activeTab === 'processes'}
          <div class="section">
            <div class="section-header">
              <h2>Process Definitions</h2>
              <button on:click={() => showNewProcessModal = true} class="primary">
                + New Process
              </button>
            </div>

            <div class="two-column">
              <!-- File List -->
              <div class="file-list">
                <h3>Processes</h3>
                {#if processesList.length === 0}
                  <p class="empty">No processes defined yet</p>
                {:else}
                  <ul>
                    {#each processesList as file}
                      <li 
                        class:selected={selectedProcess?.name === file.name}
                        on:click={() => selectFile('processes', file)}
                      >
                        {file.name}
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>

              <!-- File Editor -->
              <div class="file-editor">
                {#if selectedProcess}
                  <div class="editor-header">
                    <h3>{selectedProcess.name}</h3>
                    <div class="editor-actions">
                      {#if editingProcess}
                        <button on:click={() => saveFile('processes')} class="primary">Save</button>
                        <button on:click={() => editingProcess = false}>Cancel</button>
                      {:else}
                        <button on:click={() => editingProcess = true}>Edit</button>
                      {/if}
                    </div>
                  </div>

                  {#if editingProcess}
                    <textarea bind:value={processContent} rows="30"></textarea>
                  {:else}
                    <pre>{processContent}</pre>
                  {/if}
                {:else}
                  <p class="empty">Select a process to view</p>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <!-- Scenarios Tab -->
        {#if activeTab === 'scenarios'}
          <div class="section">
            <div class="section-header">
              <h2>Scenario Definitions</h2>
              <button on:click={() => showNewScenarioModal = true} class="primary">
                + New Scenario
              </button>
            </div>

            <div class="two-column">
              <!-- File List -->
              <div class="file-list">
                <h3>Scenarios</h3>
                {#if scenariosList.length === 0}
                  <p class="empty">No scenarios defined yet</p>
                {:else}
                  <ul>
                    {#each scenariosList as file}
                      <li 
                        class:selected={selectedScenario?.name === file.name}
                        on:click={() => selectFile('scenarios', file)}
                      >
                        {file.name}
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>

              <!-- File Editor -->
              <div class="file-editor">
                {#if selectedScenario}
                  <div class="editor-header">
                    <h3>{selectedScenario.name}</h3>
                    <div class="editor-actions">
                      {#if editingScenario}
                        <button on:click={() => saveFile('scenarios')} class="primary">Save</button>
                        <button on:click={() => editingScenario = false}>Cancel</button>
                      {:else}
                        <button on:click={() => editingScenario = true}>Edit</button>
                      {/if}
                    </div>
                  </div>

                  {#if editingScenario}
                    <textarea bind:value={scenarioContent} rows="30"></textarea>
                  {:else}
                    <pre>{scenarioContent}</pre>
                  {/if}
                {:else}
                  <p class="empty">Select a scenario to view</p>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <!-- Simulations Tab -->
        {#if activeTab === 'simulations'}
          <div class="section">
            <div class="section-header">
              <h2>Simulations</h2>
              <button on:click={() => showImportSimulationModal = true} class="primary">
                Import Simulation
              </button>
            </div>

            <div class="two-column">
              <!-- File List -->
              <div class="file-list">
                <h3>Simulations</h3>
                {#if simulationsList.length === 0}
                  <p class="empty">No simulations yet. Import one from Copilot!</p>
                {:else}
                  <ul>
                    {#each simulationsList as file}
                      <li 
                        class:selected={selectedSimulation?.name === file.name}
                        on:click={() => selectFile('simulations', file)}
                      >
                        {file.name}
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>

              <!-- Simulation Viewer/Editor -->
              <div class="file-editor">
                {#if selectedSimulation}
                  <div class="editor-header">
                    <h3>{selectedSimulation.name}</h3>
                    <div class="editor-actions">
                      <button on:click={validateSimulation} disabled={validating}>
                        {validating ? 'Validating...' : 'Validate'}
                      </button>
                      <button on:click={dryRun} disabled={runningDryRun} class="primary">
                        {runningDryRun ? 'Running...' : 'Dry Run'}
                      </button>
                    </div>
                  </div>

                  <!-- Validation Results -->
                  {#if validationResult}
                    <div class="result {validationResult.valid ? 'success' : 'error'}">
                      <h4>{validationResult.valid ? '✓ Valid' : '✗ Invalid'}</h4>
                      {#if validationResult.errors && validationResult.errors.length > 0}
                        <ul>
                          {#each validationResult.errors as error}
                            <li>{error}</li>
                          {/each}
                        </ul>
                      {/if}
                      {#if validationResult.warnings && validationResult.warnings.length > 0}
                        <h5>Warnings:</h5>
                        <ul>
                          {#each validationResult.warnings as warning}
                            <li>{warning}</li>
                          {/each}
                        </ul>
                      {/if}
                    </div>
                  {/if}

                  <!-- Dry Run Results -->
                  {#if dryRunResult}
                    <EventStreamViewer result={dryRunResult} />
                  {/if}

                  <!-- YAML Content -->
                  {#if editingSimulation}
                    <textarea bind:value={simulationContent} rows="30"></textarea>
                    <div class="editor-actions">
                      <button on:click={() => saveFile('simulations')} class="primary">Save</button>
                      <button on:click={() => editingSimulation = false}>Cancel</button>
                    </div>
                  {:else}
                    <pre>{simulationContent}</pre>
                    <button on:click={() => editingSimulation = true}>Edit</button>
                  {/if}
                {:else}
                  <p class="empty">Select a simulation to inspect</p>
                {/if}
              </div>
            </div>
          </div>
        {/if}

      </div>
    {/if}
  </div>
</div>

<!-- New Process Modal -->
{#if showNewProcessModal}
  <div class="modal">
    <div class="modal-content">
      <h3>Create New Process</h3>
      <label>
        File Name:
        <input type="text" bind:value={newFileName} placeholder="process-name" />
      </label>
      <div class="modal-actions">
        <button on:click={() => createNewFile('processes')} class="primary">Create</button>
        <button on:click={() => { showNewProcessModal = false; newFileName = ''; }}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- New Scenario Modal -->
{#if showNewScenarioModal}
  <div class="modal">
    <div class="modal-content">
      <h3>Create New Scenario</h3>
      <label>
        File Name:
        <input type="text" bind:value={newFileName} placeholder="scenario-name" />
      </label>
      <div class="modal-actions">
        <button on:click={() => createNewFile('scenarios')} class="primary">Create</button>
        <button on:click={() => { showNewScenarioModal = false; newFileName = ''; }}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Import Simulation Modal -->
{#if showImportSimulationModal}
  <div class="modal">
    <div class="modal-content">
      <h3>Import Simulation</h3>
      <p>Paste the YAML generated by GitHub Copilot:</p>
      <textarea bind:value={importSimulationContent} rows="20" placeholder="Paste YAML here..."></textarea>
      <div class="modal-actions">
        <button on:click={importSimulation} class="primary">Import</button>
        <button on:click={() => { showImportSimulationModal = false; importSimulationContent = ''; }}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .container {
    padding: 20px;
    background: #1a1a1a;
    min-height: 100vh;
  }

  .main-content {
    max-width: 1400px;
    margin: 0 auto;
  }

  h1 {
    color: #ffffff;
    margin: 0 0 5px 0;
  }

  h2, h3, h4 {
    color: #ffffff;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 25px;
    gap: 20px;
  }

  .header-text {
    flex: 1;
  }

  .header-selector {
    min-width: 350px;
    padding-top: 5px;
  }

  .subtitle {
    color: #94a3b8;
    margin-top: 5px;
    margin-bottom: 0;
  }

  .section {
    margin: 20px 0;
    padding: 20px;
    background: #252525;
    border-radius: 8px;
    border: 1px solid #3c3c3c;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  label {
    color: #e0e0e0;
    font-weight: 500;
    margin-bottom: 8px;
  }

  .tabs {
    display: flex;
    gap: 5px;
    margin: 20px 0;
    border-bottom: 2px solid #3c3c3c;
  }

  .tabs button {
    padding: 10px 20px;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    color: #94a3b8;
  }

  .tabs button:hover {
    background: #2a2a2a;
    color: #e0e0e0;
  }

  .tabs button.active {
    border-bottom-color: #60a5fa;
    font-weight: bold;
    color: #ffffff;
  }

  .two-column {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 20px;
    margin-top: 15px;
  }

  .file-list {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 4px;
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #3c3c3c;
  }

  .file-list ul {
    list-style: none;
    padding: 0;
  }

  .file-list li {
    padding: 10px;
    cursor: pointer;
    border-radius: 4px;
    margin: 2px 0;
    color: #e0e0e0;
  }

  .file-list li:hover {
    background: #333;
  }

  .file-list li.selected {
    background: #60a5fa;
    color: white;
  }

  .file-editor {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 4px;
    border: 1px solid #3c3c3c;
  }

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #3c3c3c;
  }

  .editor-header h3 {
    color: #ffffff;
    margin: 0;
  }

  .editor-actions {
    display: flex;
    gap: 10px;
  }

  .file-info small {
    color: #999;
    font-size: 12px;
  }

  .file-viewer pre,
  .file-editor pre {
    background: #1a1a1a;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
    font-size: 12px;
    line-height: 1.5;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
  }

  textarea {
    width: 100%;
    padding: 10px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    background: #1a1a1a;
    color: #e0e0e0;
  }

  textarea:focus {
    outline: none;
    border-color: #60a5fa;
  }

  button {
    padding: 8px 16px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }

  button:hover:not(:disabled) {
    background: #e0e0e0;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }button.primary {
    background: #0078d4;
    color: white;
    border-color: #0078d4;
  }

  button.primary:hover:not(:disabled) {
    background: #006abc;
  }

  .info {
    color: #60a5fa;
    padding: 10px;
    background: rgba(96, 165, 250, 0.1);
    border-radius: 4px;
    margin: 10px 0;
    border: 1px solid rgba(96, 165, 250, 0.3);
  }

  .warning {
    color: #fbbf24;
    padding: 10px;
    background: rgba(251, 191, 36, 0.1);
    border-radius: 4px;
    margin: 10px 0;
    border: 1px solid rgba(251, 191, 36, 0.3);
  }

  .empty {
    color: #94a3b8;
    font-style: italic;
    padding: 20px;
    text-align: center;
  }

  .result {
    margin: 15px 0;
    padding: 15px;
    border-radius: 4px;
  }

  .result.success {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #4ade80;
  }

  .result.error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #f87171;
  }

  .result ul {
    margin: 10px 0 0 20px;
  }

  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-content {
    background: #2a2a2a;
    padding: 30px;
    border-radius: 8px;
    min-width: 400px;
    max-width: 80%;
    border: 1px solid #3c3c3c;
  }

  .modal-content h3 {
    margin-top: 0;
    color: #ffffff;
  }

  .modal-content p {
    color: #94a3b8;
  }

  .modal-content label {
    display: block;
    margin: 15px 0;
    color: #e0e0e0;
  }

  .modal-content input,
  .modal-content textarea {
    width: 100%;
    margin-top: 5px;
  }

  .modal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
  }
</style>
