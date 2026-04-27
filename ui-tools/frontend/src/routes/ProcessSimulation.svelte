<script>
  import { onMount } from 'svelte';
  import { config } from '../lib/stores.js';
  import ModuleSelector from '../lib/ModuleSelector.svelte';
  import EnvironmentSelector from '../lib/EnvironmentSelector.svelte';
  import EventStreamViewer from '../lib/EventStreamViewer.svelte';
  import SimulationMetadata from '../lib/simulation/SimulationMetadata.svelte';
  import EventTimeline from '../lib/simulation/EventTimeline.svelte';
  import PrerequisitesList from '../lib/simulation/PrerequisitesList.svelte';
  import * as yaml from 'js-yaml';

  // Module selection
  let selectedModule = '';

  // Deployment and environment selection
  let selectedDeployment = '';
  let selectedEnvironmentKey = '';
  let deploymentsList = [];
  let deploymentsMap = {};

  // Get deployment object for EnvironmentSelector
  $: deploymentObject = selectedDeployment ? deploymentsMap[selectedDeployment] : null;

  // Active tab
  let activeTab = 'data-models'; // data-models, processes, scenarios, simulations, templates

  // Data models state
  let generatingDataModels = false;
  let dataModelsList = [];
  let selectedDataModel = null;
  let dataModelsContent = '';

  // File lists for each type
  let processesList = [];
  let scenariosList = [];
  let simulationsList = [];
  let templatesList = [];

  // Selected files
  let selectedProcess = null;
  let selectedScenario = null;
  let selectedSimulation = null;
  let selectedTemplate = null;

  // File content editors
  let processContent = '';
  let scenarioContent = '';
  let simulationContent = '';
  let templateContent = '';

  // Editing state
  let editingProcess = false;
  let editingScenario = false;
  let editingSimulation = false;
  let editingTemplate = false;

  // Hydration state
  let recordPoolsLoaded = false;
  let recordPoolCounts = {};
  let loadingRecordPools = false;
  let generatingBatch = false;
  let batchCount = 10;
  let stageDistribution = {
    intake_complete: 10,
    investigation_start_complete: 15,
    investigation_complete: 30,
    determination_complete: 45
  };
  let hydrationResult = null;
  let parsedTemplate = null;

  // View mode for simulations (visual timeline or YAML)
  let viewMode = 'visual'; // 'visual' or 'yaml'
  let parsedSimulation = null;

  // Parse simulation content when it changes
  $: if (simulationContent && viewMode === 'visual') {
    try {
      parsedSimulation = yaml.load(simulationContent);
      // Load execution state and prerequisites when simulation changes
      if (parsedSimulation && selectedModule) {
        loadExecutionState();
        loadPrerequisites();
      }
    } catch (error) {
      console.error('Failed to parse simulation YAML:', error);
      parsedSimulation = null;
    }
  }

  // Also load prerequisites when switching to visual view
  $: if (viewMode === 'visual' && simulationContent && !parsedSimulation) {
    loadPrerequisites();
  }

  // Step-by-step execution state
  let eventExecutionStates = {}; // Keyed by event_id: {status, record_id, errors, duration}
  let executingEventId = null;

  // Prerequisites state
  let prerequisites = { lookup_prerequisites: [], template_prerequisites: [], total_prerequisites: 0 };
  let loadingPrerequisites = false;

  // Load prerequisites analysis
  async function loadPrerequisites() {
    if (!simulationContent) return;

    loadingPrerequisites = true;
    try {
      const response = await fetch('/api/process-sim/analyze-prerequisites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule || '',
          event_stream_yaml: simulationContent
        })
      });

      if (response.ok) {
        prerequisites = await response.json();
      } else {
        console.error('Failed to load prerequisites');
        prerequisites = { lookup_prerequisites: [], template_prerequisites: [], total_prerequisites: 0 };
      }
    } catch (error) {
      console.error('Error loading prerequisites:', error);
      prerequisites = { lookup_prerequisites: [], template_prerequisites: [], total_prerequisites: 0 };
    } finally {
      loadingPrerequisites = false;
    }
  }

  // Load execution state from backend
  async function loadExecutionState() {
    if (!parsedSimulation || !selectedModule) return;

    const simulationName = parsedSimulation.event_stream_name;
    if (!simulationName) return;

    try {
      const response = await fetch('/api/process-sim/execution-state/get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          simulation_name: simulationName
        })
      });

      if (response.ok) {
        const state = await response.json();
        
        // Build execution states map from results
        const states = {};
        for (const result of state.execution_results) {
          states[result.event_id] = {
            status: result.success ? 'success' : 'error',
            record_id: result.record_id,
            errors: result.errors || [],
            duration: result.duration_seconds
          };
        }
        eventExecutionStates = states;
      } else if (response.status === 404) {
        // No state yet, that's okay
        eventExecutionStates = {};
      }
    } catch (error) {
      console.error('Error loading execution state:', error);
    }
  }

  // Execute a single event
  async function executeSingleEvent(eventId) {
    if (!parsedSimulation || !selectedModule || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select deployment and environment first');
      return;
    }

    executingEventId = eventId;
    eventExecutionStates[eventId] = { status: 'running', record_id: null, errors: [], duration: null };
    eventExecutionStates = {...eventExecutionStates}; // Trigger reactivity

    try {
      const response = await fetch('/api/process-sim/execute-event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          event_stream_yaml: simulationContent,
          event_id: eventId,
          deployment: selectedDeployment,
          environment: selectedEnvironmentKey
        })
      });

      const result = await response.json();

      if (result.success) {
        eventExecutionStates[eventId] = {
          status: 'success',
          record_id: result.record_id,
          errors: [],
          duration: result.duration_seconds
        };
      } else {
        eventExecutionStates[eventId] = {
          status: 'error',
          record_id: null,
          errors: result.errors || ['Unknown error'],
          duration: result.duration_seconds
        };
      }
      
      eventExecutionStates = {...eventExecutionStates}; // Trigger reactivity
    } catch (error) {
      eventExecutionStates[eventId] = {
        status: 'error',
        record_id: null,
        errors: [error.message],
        duration: null
      };
      eventExecutionStates = {...eventExecutionStates};
    } finally {
      executingEventId = null;
    }
  }

  // Reset all execution state
  async function resetExecutionState() {
    if (!parsedSimulation || !selectedModule) return;

    const simulationName = parsedSimulation.event_stream_name;
    if (!simulationName) return;

    if (!confirm('Reset all execution state? This will clear all progress.')) {
      return;
    }

    try {
      const response = await fetch('/api/process-sim/execution-state/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          simulation_name: simulationName
        })
      });

      if (response.ok) {
        eventExecutionStates = {};
        alert('Execution state reset successfully');
      }
    } catch (error) {
      console.error('Error resetting execution state:', error);
      alert('Failed to reset execution state: ' + error.message);
    }
  }

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

  // Watch for config changes to populate deployments
  $: if ($config && $config.deployments) {
    deploymentsList = Object.keys($config.deployments);
    deploymentsMap = $config.deployments;
    
    // Select first deployment by default if none selected
    if (deploymentsList.length > 0 && !selectedDeployment) {
      selectedDeployment = deploymentsList[0];
    }
  }

  // Handle module selection change
  function handleModuleChange(event) {
    selectedModule = event.detail.path;
  }

  async function loadAllFiles() {
    // Clear previous selections and content when changing modules
    selectedProcess = null;
    selectedScenario = null;
    selectedSimulation = null;
    selectedTemplate = null;
    processContent = '';
    scenarioContent = '';
    simulationContent = '';
    templateContent = '';
    validationResult = null;
    dryRunResult = null;
    executionResult = null;
    hydrationResult = null;
    
    await checkDataModels();
    await loadFiles('processes');
    await loadFiles('scenarios');
    await loadFiles('simulations');
    await loadFiles('templates');
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
      } else if (fileType === 'templates') {
        templatesList = data.files || [];
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
      } else if (fileType === 'templates') {
        selectedTemplate = file;
        templateContent = data.content;
        editingTemplate = false;
        // Parse template
        try {
          parsedTemplate = yaml.load(data.content);
        } catch (error) {
          console.error('Failed to parse template:', error);
          parsedTemplate = null;
        }
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
    } else if (fileType === 'templates') {
      filePath = selectedTemplate.path;
      content = templateContent;
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
        else if (fileType === 'templates') editingTemplate = false;
        
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

  // Initialize on mount
  onMount(async () => {
    // Load deployments from config
    if ($config && $config.deployments) {
      deploymentsList = Object.keys($config.deployments);
      deploymentsMap = $config.deployments;
      
      // Select first deployment by default
      if (deploymentsList.length > 0) {
        selectedDeployment = deploymentsList[0];
      }
    }
  });

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

  async function executeSimulation() {
    if (!selectedSimulation || !selectedModule || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select module, simulation, deployment, and environment');
      return;
    }

    // Confirm execution
    if (!confirm(`Execute simulation against ${selectedDeployment} / ${selectedEnvironmentKey}?\n\nThis will create real records in Dataverse.`)) {
      return;
    }

    executing = true;
    executionResult = null;

    try {
      const response = await fetch('/api/process-sim/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          event_stream_yaml: simulationContent,
          deployment: selectedDeployment,
          environment: selectedEnvironmentKey,
          clear_before_run: false
        })
      });

      executionResult = await response.json();
    } catch (error) {
      executionResult = { success: false, errors: [error.message], event_results: [] };
    } finally {
      executing = false;
    }
  }

  // ========================================================================
  // Hydration Functions
  // ========================================================================

  async function loadRecordPools() {
    if (!selectedModule || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select module, deployment, and environment');
      return;
    }

    loadingRecordPools = true;
    recordPoolCounts = {};

    try {
      const response = await fetch('/api/process-sim/hydrate/load-pools', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          deployment: selectedDeployment,
          environment: selectedEnvironmentKey
        })
      });

      const data = await response.json();
      
      if (data.success) {
        recordPoolCounts = data.record_pools || {};
        recordPoolsLoaded = true;
      } else {
        alert('Error loading record pools');
      }
    } catch (error) {
      alert('Error loading record pools: ' + error.message);
    } finally {
      loadingRecordPools = false;
    }
  }

  async function previewHydration() {
    if (!selectedTemplate || !selectedModule || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select template, module, deployment, and environment');
      return;
    }

    hydrationResult = null;

    try {
      const response = await fetch('/api/process-sim/hydrate/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          template_name: selectedTemplate.name,
          deployment: selectedDeployment,
          environment: selectedEnvironmentKey,
          stage: null // Full stream
        })
      });

      const data = await response.json();
      
      if (data.success) {
        hydrationResult = data;
      } else {
        alert('Error previewing hydration');
      }
    } catch (error) {
      alert('Error previewing hydration: ' + error.message);
    }
  }

  async function generateBatch() {
    if (!selectedTemplate || !selectedModule || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select template, module, deployment, and environment');
      return;
    }

    if (!recordPoolsLoaded) {
      if (!confirm('Record pools not loaded. Load them now?')) {
        return;
      }
      await loadRecordPools();
      if (!recordPoolsLoaded) {
        return;
      }
    }

    generatingBatch = true;

    try {
      const response = await fetch('/api/process-sim/hydrate/generate-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          template_name: selectedTemplate.name,
          deployment: selectedDeployment,
          environment: selectedEnvironmentKey,
          count: batchCount,
          stage_distribution: stageDistribution,
          save_to_disk: true
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`Successfully generated ${data.count} simulations!`);
        await loadFiles('simulations');
        activeTab = 'simulations';
      } else {
        alert('Error generating batch');
      }
    } catch (error) {
      alert('Error generating batch: ' + error.message);
    } finally {
      generatingBatch = false;
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
        <button 
          class:active={activeTab === 'templates'}
          on:click={() => activeTab = 'templates'}
        >
          Templates ({templatesList.length})
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

            <!-- Deployment and Environment Selection -->
            <div class="execution-config">
              <div class="form-row">
                <div class="form-group">
                  <label for="deployment-select">Deployment</label>
                  <select id="deployment-select" bind:value={selectedDeployment}>
                    <option value="">Select deployment...</option>
                    {#each deploymentsList as deployment}
                      <option value={deployment}>{deployment}</option>
                    {/each}
                  </select>
                </div>

                <EnvironmentSelector 
                  deployment={deploymentObject}
                  bind:value={selectedEnvironmentKey}
                  disabled={!selectedDeployment}
                  showLabel={true}
                />
              </div>
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
                      <button 
                        on:click={executeSimulation} 
                        disabled={executing || !selectedDeployment || !selectedEnvironmentKey}
                        class="execute-btn"
                        title={!selectedDeployment || !selectedEnvironmentKey ? 'Select deployment and environment first' : 'Execute simulation in Dataverse'}
                      >
                        {executing ? 'Executing...' : '▶ Execute'}
                      </button>
                      {#if !editingSimulation}
                        <button 
                          on:click={() => viewMode = viewMode === 'visual' ? 'yaml' : 'visual'}
                          class="view-toggle-btn"
                          title="Toggle between visual timeline and YAML view"
                        >
                          {viewMode === 'visual' ? '📋 View YAML' : '📊 View Timeline'}
                        </button>
                      {/if}
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

                  <!-- Execution Results -->
                  {#if executionResult}
                    <div class="execution-results">
                      <div class="result {executionResult.success ? 'success' : 'error'}">
                        <h4>{executionResult.success ? '✓ Execution Complete' : '✗ Execution Failed'}</h4>
                        <div class="execution-summary">
                          <p><strong>Total Events:</strong> {executionResult.total_events}</p>
                          <p><strong>Executed:</strong> {executionResult.executed_events}</p>
                          <p><strong>Failed:</strong> {executionResult.failed_events}</p>
                          <p><strong>Duration:</strong> {executionResult.total_duration_seconds?.toFixed(2)}s</p>
                        </div>
                        
                        {#if executionResult.errors && executionResult.errors.length > 0}
                          <h5>Errors:</h5>
                          <ul>
                            {#each executionResult.errors as error}
                              <li>{error}</li>
                            {/each}
                          </ul>
                        {/if}
                        
                        {#if executionResult.event_results && executionResult.event_results.length > 0}
                          <h5>Event Results:</h5>
                          <div class="event-results-table">
                            <table>
                              <thead>
                                <tr>
                                  <th>Event ID</th>
                                  <th>Operation</th>
                                  <th>Entity</th>
                                  <th>Status</th>
                                  <th>Record ID</th>
                                  <th>Duration</th>
                                </tr>
                              </thead>
                              <tbody>
                                {#each executionResult.event_results as event}
                                  <tr class:success={event.success} class:error={!event.success}>
                                    <td>{event.event_id}</td>
                                    <td>{event.operation}</td>
                                    <td>{event.entity}</td>
                                    <td>{event.success ? '✓' : '✗'}</td>
                                    <td>
                                      {#if event.record_id}
                                        <code class="record-id" title="Click to copy" on:click={() => navigator.clipboard.writeText(event.record_id)}>
                                          {event.record_id}
                                        </code>
                                      {:else}
                                        -
                                      {/if}
                                    </td>
                                    <td>{event.duration_seconds?.toFixed(3)}s</td>
                                  </tr>
                                  {#if event.errors && event.errors.length > 0}
                                    <tr class="error-details">
                                      <td colspan="6">
                                        <strong>Errors:</strong>
                                        <ul>
                                          {#each event.errors as err}
                                            <li>{err}</li>
                                          {/each}
                                        </ul>
                                      </td>
                                    </tr>
                                  {/if}
                                {/each}
                              </tbody>
                            </table>
                          </div>
                        {/if}
                      </div>
                    </div>
                  {/if}

                  <!-- Simulation Content -->
                  {#if editingSimulation}
                    <!-- Edit Mode: Always show YAML -->
                    <textarea bind:value={simulationContent} rows="30"></textarea>
                    <div class="editor-actions">
                      <button on:click={() => saveFile('simulations')} class="primary">Save</button>
                      <button on:click={() => editingSimulation = false}>Cancel</button>
                    </div>
                  {:else if viewMode === 'visual' && parsedSimulation}
                    <!-- Visual Timeline View -->
                    <div class="visual-view">
                      <SimulationMetadata simulation={parsedSimulation} />
                      
                      <!-- Prerequisites Section -->
                      <PrerequisitesList 
                        {prerequisites}
                        loading={loadingPrerequisites}
                      />
                      
                      <EventTimeline 
                        events={parsedSimulation.events || []} 
                        executionResults={executionResult?.event_results || null}
                        eventExecutionStates={eventExecutionStates}
                        onExecuteEvent={executeSingleEvent}
                        onResetState={resetExecutionState}
                        executingEventId={executingEventId}
                        canExecute={!!(selectedDeployment && selectedEnvironmentKey)}
                      />
                    </div>
                    <button on:click={() => editingSimulation = true}>Edit YAML</button>
                  {:else if viewMode === 'visual' && !parsedSimulation}
                    <!-- Parse Error -->
                    <div class="parse-error">
                      <p>⚠ Failed to parse simulation YAML. Switch to YAML view to see the content.</p>
                      <button on:click={() => viewMode = 'yaml'} class="primary">View YAML</button>
                    </div>
                  {:else}
                    <!-- YAML View -->
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

        <!-- Templates Tab -->
        {#if activeTab === 'templates'}
          <div class="section">
            <div class="section-header">
              <h2>Event Stream Templates</h2>
            </div>

            <!-- Deployment and Environment Selection -->
            <div class="execution-config">
              <div class="form-row">
                <div class="form-group">
                  <label for="deployment-select-templates">Deployment</label>
                  <select id="deployment-select-templates" bind:value={selectedDeployment}>
                    <option value="">Select deployment...</option>
                    {#each deploymentsList as deployment}
                      <option value={deployment}>{deployment}</option>
                    {/each}
                  </select>
                </div>

                <EnvironmentSelector 
                  deployment={deploymentObject}
                  bind:value={selectedEnvironmentKey}
                  disabled={!selectedDeployment}
                  showLabel={true}
                />
              </div>
            </div>

            <div class="two-column">
              <!-- Template List -->
              <div class="file-list">
                <h3>Templates</h3>
                {#if templatesList.length === 0}
                  <p class="empty">No templates yet. Create one using GitHub Copilot!</p>
                {:else}
                  <ul>
                    {#each templatesList as file}
                      <li 
                        class:selected={selectedTemplate?.name === file.name}
                        on:click={() => selectFile('templates', file)}
                      >
                        {file.name}
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>

              <!-- Template Viewer/Hydration Config -->
              <div class="file-editor">
                {#if selectedTemplate}
                  <div class="editor-header">
                    <h3>{selectedTemplate.name}</h3>
                  </div>

                  <!-- Hydration Configuration -->
                  <div class="hydration-config">
                    <h4>🎲 Hydration Configuration</h4>
                    
                    <!-- Record Pools -->
                    <div class="config-section">
                      <h5>Record Pools</h5>
                      <button 
                        on:click={loadRecordPools} 
                        disabled={loadingRecordPools || !selectedDeployment || !selectedEnvironmentKey}
                        class="primary"
                      >
                        {loadingRecordPools ? 'Loading...' : recordPoolsLoaded ? '🔄 Reload Record Pools' : '📥 Load Record Pools'}
                      </button>
                      
                      {#if recordPoolsLoaded}
                        <div class="record-pools-status">
                          <p><strong>Available Records:</strong></p>
                          <ul>
                            {#each Object.entries(recordPoolCounts) as [entity, count]}
                              <li>{entity}: <strong>{count}</strong> records</li>
                            {/each}
                          </ul>
                        </div>
                      {/if}
                    </div>

                    <!-- Batch Generation Config -->
                    <div class="config-section">
                      <h5>Batch Generation</h5>
                      
                      <div class="form-group">
                        <label for="batch-count">Number of Variations:</label>
                        <input 
                          id="batch-count" 
                          type="number" 
                          bind:value={batchCount} 
                          min="1" 
                          max="1000"
                        />
                      </div>

                      <div class="form-group">
                        <label>Stage Distribution:</label>
                        <div class="stage-distribution">
                          {#each Object.entries(stageDistribution) as [stage, percentage]}
                            <div class="stage-row">
                              <label for="stage-{stage}">{stage.replace(/_/g, ' ')}:</label>
                              <input 
                                id="stage-{stage}"
                                type="number" 
                                bind:value={stageDistribution[stage]} 
                                min="0" 
                                max="100"
                              />
                              <span>%</span>
                            </div>
                          {/each}
                          <div class="stage-total">
                            Total: {Object.values(stageDistribution).reduce((a, b) => a + b, 0)}%
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Actions -->
                    <div class="hydration-actions">
                      <button 
                        on:click={previewHydration}
                        disabled={!recordPoolsLoaded || !selectedDeployment || !selectedEnvironmentKey}
                      >
                        👁 Preview One Variation
                      </button>
                      <button 
                        on:click={generateBatch}
                        disabled={generatingBatch || !recordPoolsLoaded || !selectedDeployment || !selectedEnvironmentKey}
                        class="primary"
                      >
                        {generatingBatch ? 'Generating...' : `🚀 Generate ${batchCount} Variations`}
                      </button>
                    </div>
                  </div>

                  <!-- Hydration Preview Result -->
                  {#if hydrationResult}
                    <div class="hydration-result">
                      <h4>✅ Preview Result</h4>
                      <div class="result-summary">
                        <p><strong>Generated Stream:</strong> {hydrationResult.event_stream?.event_stream_name}</p>
                        <p><strong>Event Count:</strong> {hydrationResult.event_count}</p>
                        {#if hydrationResult.truncated_at_stage}
                          <p><strong>Truncated At:</strong> {hydrationResult.truncated_at_stage}</p>
                        {/if}
                      </div>
                      <details>
                        <summary>View Generated YAML</summary>
                        <pre>{yaml.dump(hydrationResult.event_stream)}</pre>
                      </details>
                    </div>
                  {/if}

                  <!-- Template Content -->
                  {#if editingTemplate}
                    <div class="template-editor">
                      <h4>Edit Template</h4>
                      <textarea bind:value={templateContent} rows="30"></textarea>
                      <div class="editor-actions">
                        <button on:click={() => saveFile('templates')} class="primary">Save</button>
                        <button on:click={() => editingTemplate = false}>Cancel</button>
                      </div>
                    </div>
                  {:else}
                    <div class="template-viewer">
                      <h4>Template Content</h4>
                      <pre>{templateContent}</pre>
                      <button on:click={() => editingTemplate = true}>Edit</button>
                    </div>
                  {/if}
                {:else}
                  <p class="empty">Select a template to configure hydration</p>
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

  /* Execution configuration styles */
  .execution-config {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
    border: 1px solid #3c3c3c;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  .form-group label {
    margin-bottom: 5px;
    font-size: 14px;
  }

  .form-group select {
    background: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 14px;
  }

  .execute-btn {
    background: #10b981 !important;
    color: white !important;
  }

  .execute-btn:hover:not(:disabled) {
    background: #059669 !important;
  }

  .execute-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Execution results styles */
  .execution-results {
    margin-top: 20px;
  }

  .execution-summary {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin: 15px 0;
    padding: 15px;
    background: #1a1a1a;
    border-radius: 4px;
  }

  .execution-summary p {
    margin: 0;
    color: #e0e0e0;
  }

  .execution-summary strong {
    color: #94a3b8;
    font-size: 12px;
    display: block;
    margin-bottom: 5px;
  }

  .event-results-table {
    margin-top: 15px;
    overflow-x: auto;
  }

  .event-results-table table {
    width: 100%;
    border-collapse: collapse;
    background: #1a1a1a;
    border-radius: 4px;
    overflow: hidden;
  }

  .event-results-table th {
    background: #2a2a2a;
    color: #94a3b8;
    text-align: left;
    padding: 10px;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    border-bottom: 1px solid #3c3c3c;
  }

  .event-results-table td {
    padding: 10px;
    color: #e0e0e0;
    border-bottom: 1px solid #3c3c3c;
    font-size: 14px;
  }

  .event-results-table tr.success td {
    background: rgba(16, 185, 129, 0.05);
  }

  .event-results-table tr.error td {
    background: rgba(239, 68, 68, 0.05);
  }

  .event-results-table tr.error-details td {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
    font-size: 13px;
  }

  .event-results-table tr.error-details ul {
    margin: 5px 0 0 20px;
  }

  .record-id {
    background: #2a2a2a;
    padding: 4px 8px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #60a5fa;
    cursor: pointer;
    display: inline-block;
  }

  .record-id:hover {
    background: #3c3c3c;
    color: #93c5fd;
  }

  /* View toggle button */
  .view-toggle-btn {
    background: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
  }

  .view-toggle-btn:hover {
    background: #3c3c3c;
    border-color: #4b5563;
  }

  /* Visual view container */
  .visual-view {
    margin: 20px 0;
  }

  /* Parse error display */
  .parse-error {
    padding: 40px;
    text-align: center;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    margin: 20px 0;
  }

  .parse-error p {
    color: #f87171;
    font-size: 16px;
    margin-bottom: 20px;
  }

  /* Hydration Config Styles */
  .hydration-config {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
  }

  .hydration-config h4 {
    color: #60a5fa;
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 18px;
  }

  .hydration-config h5 {
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    margin: 15px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .config-section {
    margin: 20px 0;
    padding: 15px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 6px;
  }

  .record-pools-status {
    margin-top: 15px;
    padding: 10px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 4px;
  }

  .record-pools-status p {
    color: #4ade80;
    margin: 0 0 10px 0;
    font-weight: 600;
  }

  .record-pools-status ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .record-pools-status li {
    color: #e0e0e0;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .record-pools-status li:last-child {
    border-bottom: none;
  }

  .record-pools-status strong {
    color: #4ade80;
    float: right;
  }

  .stage-distribution {
    background: rgba(0, 0, 0, 0.3);
    padding: 15px;
    border-radius: 4px;
  }

  .stage-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 8px 0;
  }

  .stage-row label {
    flex: 1;
    color: #94a3b8;
    margin: 0;
    font-size: 14px;
    text-transform: capitalize;
  }

  .stage-row input[type="number"] {
    width: 80px;
    padding: 6px 10px;
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
  }

  .stage-row span {
    color: #94a3b8;
    font-size: 14px;
  }

  .stage-total {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #3c3c3c;
    color: #60a5fa;
    font-weight: 600;
    text-align: right;
  }

  .hydration-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid #3c3c3c;
  }

  .hydration-actions button {
    flex: 1;
  }

  .hydration-result {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
  }

  .hydration-result h4 {
    color: #4ade80;
    margin-top: 0;
    margin-bottom: 15px;
  }

  .result-summary {
    margin-bottom: 15px;
  }

  .result-summary p {
    color: #e0e0e0;
    margin: 8px 0;
  }

  .result-summary strong {
    color: #4ade80;
  }

  .hydration-result details {
    margin-top: 15px;
  }

  .hydration-result summary {
    color: #60a5fa;
    cursor: pointer;
    padding: 10px;
    background: rgba(96, 165, 250, 0.1);
    border-radius: 4px;
    user-select: none;
  }

  .hydration-result summary:hover {
    background: rgba(96, 165, 250, 0.2);
  }

  .hydration-result pre {
    margin-top: 10px;
    max-height: 400px;
    overflow-y: auto;
  }

  .template-viewer,
  .template-editor {
    margin-top: 20px;
  }

  .template-viewer h4,
  .template-editor h4 {
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    margin: 15px 0 10px 0;
  }

  .form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
  }

  .form-row .form-group {
    flex: 1;
  }

  .execution-config {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
  }
</style>
