<script>
  import { onMount } from 'svelte';
  import { modules, config, outputLines, operationStatus, streamResponse } from '../lib/stores.js';
  import ModuleSelector from '../lib/ModuleSelector.svelte';
  import EnvironmentSelector from '../lib/EnvironmentSelector.svelte';
  import OutputStream from '../lib/OutputStream.svelte';
  import Header from '../lib/Header.svelte';

  let selectedModule = '';
  let selectedModulePath = '';
  let selectedDeployment = '';
  let selectedEnvironmentKey = '';
  let hasDataZip = false;
  let dataFileName = '';
  let importing = false;
  let showOutput = false;
  let checkingModules = true;

  // Deployment objects
  let deploymentsList = [];
  let deploymentsMap = {};

  // Track which modules have sample data
  let modulesWithData = new Set();

  // Generate unique operation ID
  function generateOperationId() {
    return `op_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

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

  // Check all modules for sample data availability
  async function checkAllModulesForData() {
    if (!$modules || $modules.length === 0) {
      checkingModules = false;
      return;
    }

    checkingModules = true;
    const dataSet = new Set();

    // Check each module in parallel
    await Promise.all(
      $modules.map(async (module) => {
        try {
          const response = await fetch(`/api/deployment/check-sample-data?module_path=${encodeURIComponent(module.path)}`);
          const data = await response.json();
          if (data.exists) {
            dataSet.add(module.path);
          }
        } catch (error) {
          console.error(`Error checking sample data for ${module.path}:`, error);
        }
      })
    );

    modulesWithData = dataSet;
    checkingModules = false;
  }

  // Watch for modules to be loaded, then check for sample data
  $: if ($modules && $modules.length > 0 && modulesWithData.size === 0) {
    checkAllModulesForData();
  }

  // Watch for config changes
  $: if ($config && $config.deployments) {
    deploymentsList = Object.keys($config.deployments);
    deploymentsMap = $config.deployments;
    
    // If no deployment selected and we have deployments, select first
    if (!selectedDeployment && deploymentsList.length > 0) {
      selectedDeployment = deploymentsList[0];
    }
  }

  // Get deployment object
  $: deploymentObject = selectedDeployment ? deploymentsMap[selectedDeployment] : null;

  // Handle module selection
  async function handleModuleChange(event) {
    const { path, module } = event.detail;
    selectedModulePath = path;
    selectedModule = module;
    
    // Check for sample data
    if (path) {
      await checkSampleData(path);
    } else {
      hasDataZip = false;
      dataFileName = '';
    }
  }

  // Handle environment selection
  function handleEnvironmentChange(event) {
    // Environment key is already bound via the component
  }

  // Check if sample data exists
  async function checkSampleData(modulePath) {
    try {
      const response = await fetch(`/api/deployment/check-sample-data?module_path=${encodeURIComponent(modulePath)}`);
      const data = await response.json();
      hasDataZip = data.exists;
      dataFileName = data.data_file || '';
    } catch (error) {
      console.error('Error checking sample data:', error);
      hasDataZip = false;
      dataFileName = '';
    }
  }

  // Import data
  async function importData() {
    if (!selectedModulePath || !selectedDeployment || !selectedEnvironmentKey) {
      alert('Please select a module, deployment, and environment');
      return;
    }

    if (!hasDataZip) {
      alert('No sample data available for this module');
      return;
    }

    importing = true;
    showOutput = true;
    outputLines.set([]);
    operationStatus.set('running');

    const operationId = generateOperationId();

    try {
      const response = await fetch('/api/deployment/import-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          deployment: selectedDeployment,
          environment_key: selectedEnvironmentKey,
          module_path: selectedModulePath,
          operationId: operationId
        }),
      });

      await streamResponse(response);
    } catch (error) {
      console.error('Import error:', error);
      operationStatus.set('error');
      outputLines.update(lines => [...lines, `Error: ${error.message}`]);
    } finally {
      importing = false;
    }
  }

  // Close output modal
  function closeOutput() {
    showOutput = false;
    outputLines.set([]);
    operationStatus.set('idle');
  }

  // Can import?
  $: canImport = selectedModulePath && selectedDeployment && selectedEnvironmentKey && hasDataZip && !importing;
</script>

<div class="data-importer">
  <Header 
    title="Data Importer" 
    subtitle="Import sample data into Dataverse environments"
  />

  <div class="container">
    <div class="form-section">
      <h2>Import Configuration</h2>
      
      <div class="form-row">
        <ModuleSelector 
          bind:value={selectedModulePath}
          on:change={handleModuleChange}
          allowedPaths={modulesWithData}
          placeholder={checkingModules ? "Loading modules..." : "-- Select Module (with sample data) --"}
          disabled={checkingModules}
        />
        {#if checkingModules}
          <p class="loading-text">Checking modules for sample data...</p>
        {:else if modulesWithData.size === 0}
          <p class="info-text">No modules with sample data found</p>
        {:else}
          <p class="info-text">{modulesWithData.size} module{modulesWithData.size !== 1 ? 's' : ''} with sample data</p>
        {/if}
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="deployment-select">Deployment:</label>
          <select 
            id="deployment-select"
            bind:value={selectedDeployment}
          >
            <option value="">-- Select Deployment --</option>
            {#each deploymentsList as deployment}
              <option value={deployment}>{deployment}</option>
            {/each}
          </select>
        </div>
      </div>

      <div class="form-row">
        <EnvironmentSelector 
          deployment={deploymentObject}
          bind:value={selectedEnvironmentKey}
          on:change={handleEnvironmentChange}
        />
      </div>

      {#if selectedModulePath}
        <div class="info-section">
          {#if hasDataZip}
            <div class="info success">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="currentColor"/>
              </svg>
              <span>Sample data available: <strong>{dataFileName}</strong></span>
            </div>
          {:else}
            <div class="info warning">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/>
              </svg>
              <span>No sample data found for this module</span>
            </div>
          {/if}
        </div>
      {/if}

      <div class="actions">
        <button 
          class="btn-primary"
          on:click={importData}
          disabled={!canImport}
        >
          {#if importing}
            Importing...
          {:else}
            Import Data
          {/if}
        </button>
      </div>
    </div>

    <div class="help-section">
      <h3>About Data Import</h3>
      <p>
        This tool imports sample data from module <code>sample-data</code> folders into
        Dataverse environments using the Power Platform CLI.
      </p>
      <ul>
        <li>Select a module that contains sample data</li>
        <li>Choose the target deployment and environment</li>
        <li>Click "Import Data" to run the import</li>
      </ul>
      <p class="note">
        <strong>Note:</strong> The data import uses <code>pac data import</code> command,
        which requires the module's solution to already be deployed to the target environment.
      </p>
    </div>
  </div>
</div>

<!-- Output Modal -->
{#if showOutput}
  <OutputStream 
    title="Data Import Output"
    on:close={closeOutput}
  />
{/if}

<style>
  .data-importer {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .container {
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 30px;
    margin-top: 20px;
  }

  .form-section {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
  }

  .form-section h2 {
    margin: 0 0 24px 0;
    color: #e0e0e0;
    font-size: 18px;
    font-weight: 600;
  }

  .form-row {
    margin-bottom: 20px;
  }

  .loading-text {
    margin: 8px 0 0 0;
    font-size: 13px;
    color: #1e90ff;
    font-style: italic;
  }

  .info-text {
    margin: 8px 0 0 0;
    font-size: 13px;
    color: #94a3b8;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  label {
    color: #e0e0e0;
    font-weight: 500;
    font-size: 14px;
  }

  select {
    padding: 10px 12px;
    font-size: 14px;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    background: #2a2a2a;
    color: #e0e0e0;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  select:hover {
    border-color: #1e90ff;
    background: #333333;
  }

  select:focus {
    outline: none;
    border-color: #1e90ff;
    box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.1);
  }

  .info-section {
    margin: 20px 0;
  }

  .info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 14px;
  }

  .info.success {
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.3);
    color: #28a745;
  }

  .info.warning {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    color: #ffc107;
  }

  .info svg {
    flex-shrink: 0;
  }

  .actions {
    margin-top: 24px;
    display: flex;
    gap: 12px;
  }

  .btn-primary {
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    border: none;
    border-radius: 6px;
    background: #1e90ff;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1873cc;
    box-shadow: 0 2px 8px rgba(30, 144, 255, 0.3);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .help-section {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
  }

  .help-section h3 {
    margin: 0 0 16px 0;
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 600;
  }

  .help-section p {
    margin: 0 0 16px 0;
    color: #b0b0b0;
    font-size: 14px;
    line-height: 1.6;
  }

  .help-section ul {
    margin: 0 0 16px 0;
    padding-left: 20px;
    color: #b0b0b0;
    font-size: 14px;
    line-height: 1.8;
  }

  .help-section li {
    margin-bottom: 8px;
  }

  .help-section code {
    background: #2a2a2a;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #1e90ff;
  }

  .note {
    background: rgba(255, 193, 7, 0.1);
    border-left: 3px solid #ffc107;
    padding: 12px;
    border-radius: 4px;
  }

  @media (max-width: 1200px) {
    .container {
      grid-template-columns: 1fr;
    }
  }
</style>
