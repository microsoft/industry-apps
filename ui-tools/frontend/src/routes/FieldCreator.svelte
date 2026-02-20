<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';
  import { 
    config, 
    deployments, 
    tenants, 
    outputLines, 
    operationStatus, 
    streamResponse 
  } from '../lib/stores.js';

  let selectedDeployment = '';
  let selectedEnvironment = '';
  let tableName = '';
  let fieldsText = '';
  
  $: availableEnvironments = getAvailableEnvironments($config, selectedDeployment);
  
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

  async function createFields() {
    if (!selectedDeployment || !selectedEnvironment || !tableName || !fieldsText.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    // Parse field definitions
    const lines = fieldsText.trim().split('\n');
    const fields = [];
    
    for (const line of lines) {
      if (!line.trim() || line.trim().startsWith('#')) continue;
      
      // Expected format: schemaName|displayName|type|required|maxLength
      // Example: cr09x_customfield|Custom Field|Text|false|100
      const parts = line.split('|').map(p => p.trim());
      
      if (parts.length < 3) {
        alert(`Invalid field definition: ${line}\nExpected format: schemaName|displayName|type|required|maxLength`);
        return;
      }
      
      fields.push({
        schemaName: parts[0],
        displayName: parts[1],
        type: parts[2],
        required: parts[3] === 'true' || parts[3] === 'yes',
        maxLength: parts[4] ? parseInt(parts[4]) : null
      });
    }

    if (fields.length === 0) {
      alert('No valid field definitions found');
      return;
    }

    // Start operation
    outputLines.set([]);
    operationStatus.set('running');

    try {
      const response = await fetch('/api/helpers/create-fields', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: selectedDeployment,
          environment: selectedEnvironment,
          tableName,
          fields
        })
      });

      await streamResponse(response);
      
      // Clear form on success
      if ($operationStatus === 'success') {
        fieldsText = '';
      }
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }

  onMount(() => {
    // Set default deployment
    if ($deployments && $deployments.length > 0) {
      selectedDeployment = $deployments[0];
    }
  });

  const exampleFields = `# Example field definitions
# Format: schemaName|displayName|type|required|maxLength
# Types: Text, Number, Date, DateTime, Choice, Lookup, MultiChoice, Boolean, Currency, etc.

cr09x_customtext|Custom Text Field|Text|false|100
cr09x_customnumber|Custom Number|Number|false|
cr09x_customdate|Custom Date|Date|false|
cr09x_isactive|Is Active|Boolean|true|`;
</script>

<div class="field-creator">
  <Header title="Field Creator" description="Mass create fields on Dataverse tables">
    <button class="btn btn-primary" on:click={createFields} disabled={$operationStatus === 'running'}>
      {$operationStatus === 'running' ? '⏳ Creating...' : '▶ Create Fields'}
    </button>
  </Header>

  <div class="content">
    <div class="form-container">
      <div class="form-section">
        <h3>Target Environment</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="deployment">Deployment</label>
            <select id="deployment" bind:value={selectedDeployment}>
              <option value="">-- Select Deployment --</option>
              {#each $deployments as deployment}
                <option value={deployment}>{deployment}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="environment">Environment</label>
            <select id="environment" bind:value={selectedEnvironment} disabled={!selectedDeployment}>
              <option value="">-- Select Environment --</option>
              {#each availableEnvironments as env}
                <option value={env.key}>{env.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="tableName">Table Logical Name</label>
          <input 
            type="text" 
            id="tableName" 
            bind:value={tableName}
            placeholder="e.g., cr09x_customtable"
            pattern="[a-z0-9_]+"
          />
          <p class="help-text">Enter the logical name of the target table (lowercase, underscores allowed)</p>
        </div>
      </div>

      <div class="form-section">
        <h3>Field Definitions</h3>
        
        <div class="form-group">
          <label for="fieldsText">Fields (one per line)</label>
          <textarea 
            id="fieldsText"
            bind:value={fieldsText}
            placeholder={exampleFields}
            rows="15"
          ></textarea>
          <p class="help-text">
            Format: <code>schemaName|displayName|type|required|maxLength</code><br>
            Lines starting with # are comments and will be ignored.
          </p>
        </div>

        <div class="example-box">
          <h4>📋 Supported Field Types</h4>
          <ul class="type-list">
            <li><strong>Text</strong> - Single line of text</li>
            <li><strong>Number</strong> - Whole number or decimal</li>
            <li><strong>Date</strong> - Date only</li>
            <li><strong>DateTime</strong> - Date and time</li>
            <li><strong>Boolean</strong> - Yes/No</li>
            <li><strong>Currency</strong> - Money field</li>
            <li><strong>Choice</strong> - Option set</li>
            <li><strong>Lookup</strong> - Reference to another table</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="info-panel">
      <div class="info-card">
        <h3>ℹ️ How to Use</h3>
        <ol>
          <li>Select the target deployment and environment</li>
          <li>Enter the logical name of the target table</li>
          <li>Define fields using the pipe-separated format</li>
          <li>Click "Create Fields" to execute</li>
          <li>Monitor progress in the output window</li>
        </ol>
      </div>

      <div class="info-card warning">
        <h3>⚠️ Important Notes</h3>
        <ul>
          <li>Field schema names must start with your publisher prefix</li>
          <li>Schema names cannot be changed after creation</li>
          <li>This operation cannot be easily undone</li>
          <li>Test in a development environment first</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<style>
  .field-creator {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 2rem;
  }

  .form-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .form-section {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .form-section h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.25rem;
    color: #ffffff;
    font-weight: 600;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group:last-child {
    margin-bottom: 0;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #cccccc;
    font-size: 14px;
  }

  .form-group input[type="text"],
  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 0.625rem 0.75rem;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    background: #1e1e1e;
    color: #e0e0e0;
    transition: border-color 0.2s;
  }

  .form-group input[type="text"]:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  .form-group textarea {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: vertical;
  }

  .form-group select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .help-text {
    font-size: 12px;
    color: #808080;
    margin: 0.5rem 0 0 0;
  }

  .help-text code {
    background: #1e1e1e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #4fc3f7;
    font-size: 11px;
  }

  .example-box {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    margin-top: 1rem;
  }

  .example-box h4 {
    margin: 0 0 0.75rem 0;
    font-size: 14px;
    color: #4fc3f7;
    font-weight: 600;
  }

  .type-list {
    margin: 0;
    padding-left: 1.25rem;
    color: #cccccc;
    font-size: 13px;
  }

  .type-list li {
    margin-bottom: 0.5rem;
  }

  .type-list strong {
    color: #a5d6a7;
  }

  .info-panel {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .info-card {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .info-card.warning {
    border-color: #f44336;
    border-left-width: 4px;
  }

  .info-card h3 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #ffffff;
    font-weight: 600;
  }

  .info-card ol,
  .info-card ul {
    margin: 0;
    padding-left: 1.25rem;
    color: #cccccc;
    font-size: 14px;
    line-height: 1.6;
  }

  .info-card li {
    margin-bottom: 0.5rem;
  }

  .info-card li:last-child {
    margin-bottom: 0;
  }

  @media (max-width: 1200px) {
    .content {
      grid-template-columns: 1fr;
    }
    
    .info-panel {
      order: -1;
    }
  }
</style>
