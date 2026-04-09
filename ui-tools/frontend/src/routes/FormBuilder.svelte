<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';

  let selectedModule = '';
  let selectedEntity = '';
  let formGuid = '';
  
  let availableModules = [];
  let availableEntities = [];
  
  // Extract section
  let extractedYaml = '';
  let fieldCount = 0;
  let extracting = false;
  let extractError = '';
  
  // Build section
  let yamlInput = '';
  let validating = false;
  let building = false;
  let validationResult = null;
  let buildResult = null;
  let dryRunResult = null;
  
  // Load modules on mount
  onMount(() => {
    loadModules();
  });
  
  // Load entities when module changes
  $: if (selectedModule) {
    loadEntities();
  }
  
  async function loadModules() {
    try {
      const response = await fetch('/api/formbuilder/list-modules');
      const data = await response.json();
      
      if (data.success && data.modules) {
        availableModules = data.modules;
      }
    } catch (error) {
      console.error('Error loading modules:', error);
    }
  }
  
  async function loadEntities() {
    if (!selectedModule) return;
    
    try {
      const response = await fetch('/api/formbuilder/list-entities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_path: selectedModule })
      });
      
      const data = await response.json();
      
      if (data.success) {
        availableEntities = data.entities;
      } else {
        console.error('Error loading entities:', data.error);
        availableEntities = [];
      }
    } catch (error) {
      console.error('Error loading entities:', error);
      availableEntities = [];
    }
  }
  
  async function extractFields() {
    if (!selectedModule || !selectedEntity) {
      extractError = 'Please select a module and entity';
      return;
    }
    
    extracting = true;
    extractError = '';
    extractedYaml = '';
    fieldCount = 0;
    
    try {
      const response = await fetch('/api/formbuilder/extract-fields', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          entity_name: selectedEntity,
          form_guid: formGuid || null
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        extractedYaml = data.yaml_template;
        fieldCount = data.field_count;
      } else {
        extractError = data.error || 'Failed to extract fields';
      }
    } catch (error) {
      extractError = `Error: ${error.message}`;
    } finally {
      extracting = false;
    }
  }
  
  function copyToClipboard() {
    navigator.clipboard.writeText(extractedYaml);
    // Could add a toast notification here
  }
  
  function downloadYaml() {
    const blob = new Blob([extractedYaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedEntity}-form-config.yaml`;
    a.click();
    URL.revokeObjectURL(url);
  }
  
  function prepareForCopilot() {
    const prompt = `Organize these fields into logical tabs and sections based on their types and purpose:\n\n${extractedYaml}`;
    navigator.clipboard.writeText(prompt);
    // Show the prepared prompt in yamlInput for visibility
    yamlInput = prompt;
  }
  
  async function validateYaml() {
    if (!yamlInput.trim()) {
      validationResult = { valid: false, errors: ['YAML is empty'] };
      return;
    }
    
    if (!selectedModule) {
      validationResult = { valid: false, errors: ['Please select a module first'] };
      return;
    }
    
    validating = true;
    validationResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/validate-yaml', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          yaml_config: yamlInput,
          module_path: selectedModule
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        validationResult = {
          valid: data.valid,
          errors: data.errors || [],
          warnings: data.warnings || []
        };
      } else {
        validationResult = {
          valid: false,
          errors: [data.error || 'Validation failed']
        };
      }
    } catch (error) {
      validationResult = {
        valid: false,
        errors: [`Error: ${error.message}`]
      };
    } finally {
      validating = false;
    }
  }
  
  async function buildForm(dryRun = false) {
    if (!yamlInput.trim()) {
      buildResult = { success: false, error: 'YAML is empty' };
      return;
    }
    
    if (!selectedModule) {
      buildResult = { success: false, error: 'Please select a module first' };
      return;
    }
    
    building = true;
    buildResult = null;
    dryRunResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/build-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          yaml_config: yamlInput,
          module_path: selectedModule,
          dry_run: dryRun
        })
      });
      
      const data = await response.json();
      
      if (dryRun) {
        dryRunResult = data;
      } else {
        buildResult = data;
      }
    } catch (error) {
      if (dryRun) {
        dryRunResult = { success: false, error: error.message };
      } else {
        buildResult = { success: false, error: error.message };
      }
    } finally {
      building = false;
    }
  }
  
  function clearResults() {
    extractedYaml = '';
    fieldCount = 0;
    extractError = '';
    yamlInput = '';
    validationResult = null;
    buildResult = null;
    dryRunResult = null;
  }
</script>

<div class="page-container">
  <Header title="Form Builder" subtitle="Generate forms from entity schemas using AI-assisted YAML configuration" />
  
  <div class="content">
    <!-- Configuration Section -->
    <div class="card">
      <h3>Configuration</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Module</label>
          <select bind:value={selectedModule} on:change={clearResults}>
            <option value="">Select Module</option>
            {#each availableModules as module}
              <option value={module.path}>{module.display_name}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
    
    <!-- Step 1: Extract Fields -->
    <div class="card">
      <h3>📤 Step 1: Extract Fields</h3>
      <p class="help-text">Select an entity to extract its custom fields into a YAML template.</p>
      
      <div class="form-row">
        <div class="form-group">
          <label>Entity</label>
          <select bind:value={selectedEntity} disabled={!selectedModule}>
            <option value="">Select Entity</option>
            {#each availableEntities as entity}
              <option value={entity.name}>{entity.display_name}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-group">
          <label>Form GUID (Optional)</label>
          <input 
            type="text" 
            bind:value={formGuid} 
            placeholder="00000000-0000-0000-0000-000000000000"
            disabled={!selectedModule}
          />
        </div>
      </div>
      
      <button 
        class="btn btn-primary" 
        on:click={extractFields}
        disabled={!selectedEntity || extracting}
      >
        {extracting ? 'Extracting...' : 'Extract Fields'}
      </button>
      
      {#if extractError}
        <div class="alert alert-error">
          {extractError}
        </div>
      {/if}
      
      {#if extractedYaml}
        <div class="result-section">
          <div class="result-header">
            <span class="success-badge">✓ Extracted {fieldCount} custom fields</span>
            <div class="button-group">
              <button class="btn btn-sm" on:click={copyToClipboard}>📋 Copy</button>
              <button class="btn btn-sm" on:click={downloadYaml}>💾 Download</button>
            </div>
          </div>
          
          <textarea 
            class="yaml-display" 
            readonly 
            value={extractedYaml}
            rows="20"
          ></textarea>
        </div>
      {/if}
    </div>
    
    <!-- Step 2: Organize with Copilot -->
    <div class="card">
      <h3>🤖 Step 2: Organize with Copilot</h3>
      <p class="help-text">
        Click the button below to prepare a prompt with the extracted fields ready for Copilot.
      </p>
      
      <button 
        class="btn btn-primary" 
        on:click={prepareForCopilot}
        disabled={!extractedYaml}
      >
        📋 Prepare for Copilot (Copy Prompt)
      </button>
      
      <p class="help-text" style="margin-top: 16px;">
        The prompt has been copied to your clipboard and shown in Step 3 below. 
        Paste it into GitHub Copilot in VS Code or the sidebar, 
        then copy the organized YAML result back into Step 3.
      </p>
    </div>
    
    <!-- Step 3: Build Form -->
    <div class="card">
      <h3>🔨 Step 3: Build Form</h3>
      <p class="help-text">Paste the organized YAML from Copilot here to build the form.</p>
      
      <textarea 
        class="yaml-input" 
        bind:value={yamlInput}
        placeholder="Paste organized YAML configuration here..."
        rows="15"
      ></textarea>
      
      <div class="button-group">
        <button 
          class="btn btn-secondary" 
          on:click={validateYaml}
          disabled={!yamlInput || validating}
        >
          {validating ? 'Validating...' : '✓ Validate YAML'}
        </button>
        
        <button 
          class="btn btn-secondary" 
          on:click={() => buildForm(true)}
          disabled={!yamlInput || building}
        >
          👁️ Preview (Dry Run)
        </button>
        
        <button 
          class="btn btn-primary" 
          on:click={() => buildForm(false)}
          disabled={!yamlInput || building}
        >
          {building ? 'Building...' : '🔨 Build Form'}
        </button>
      </div>
      
      {#if validationResult}
        <div class="alert {validationResult.valid ? 'alert-success' : 'alert-error'}">
          <strong>{validationResult.valid ? '✓ Valid YAML' : '✗ Invalid YAML'}</strong>
          
          {#if validationResult.errors && validationResult.errors.length > 0}
            <ul class="error-list">
              {#each validationResult.errors as error}
                <li>❌ {error}</li>
              {/each}
            </ul>
          {/if}
          
          {#if validationResult.warnings && validationResult.warnings.length > 0}
            <ul class="warning-list">
              {#each validationResult.warnings as warning}
                <li>⚠️ {warning}</li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}
      
      {#if dryRunResult}
        <div class="alert alert-info">
          <strong>📋 Preview of Operations</strong>
          {#if dryRunResult.success}
            <p>{dryRunResult.operations.length} operations will be performed:</p>
            <ul class="operation-list">
              {#each dryRunResult.operations as op}
                <li>
                  {#if op.type === 'add_tab'}
                    ➕ Add tab: <strong>{op.tab_label}</strong>
                  {:else if op.type === 'add_section'}
                    ➕ Add section: <strong>{op.section_label}</strong> ({op.columns} column{op.columns > 1 ? 's' : ''})
                  {:else if op.type === 'add_fields'}
                    ➕ Add {op.field_count} fields to <strong>{op.section_label}</strong>
                  {/if}
                </li>
              {/each}
            </ul>
          {:else}
            <p class="error-text">❌ {dryRunResult.error}</p>
          {/if}
        </div>
      {/if}
      
      {#if buildResult}
        <div class="alert {buildResult.success ? 'alert-success' : 'alert-error'}">
          {#if buildResult.success}
            <strong>✓ Form Built Successfully!</strong>
            <p>{buildResult.message}</p>
            <p class="file-path">Form updated: {buildResult.form_path}</p>
            <p class="next-steps">
              Next: Run <code>pac solution sync --packagetype Both</code> to sync changes
            </p>
          {:else}
            <strong>✗ Build Failed</strong>
            <p class="error-text">{buildResult.error}</p>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .page-container {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .card {
    background: #0d0d0d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
  }
  
  .card h3 {
    margin: 0 0 16px 0;
    color: #e0e0e0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .help-text {
    color: #a0a0a0;
    font-size: 14px;
    margin: 8px 0;
    line-height: 1.5;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .form-group label {
    color: #b0b0b0;
    font-size: 14px;
    font-weight: 500;
  }
  
  select, input, textarea {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 8px 12px;
    font-size: 14px;
    font-family: inherit;
  }
  
  select:focus, input:focus, textarea:focus {
    outline: none;
    border-color: #0078d4;
  }
  
  select:disabled, input:disabled, textarea:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn {
    padding: 10px 20px;
    border-radius: 4px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: #0078d4;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: #106ebe;
  }
  
  .btn-secondary {
    background: #3c3c3c;
    color: #e0e0e0;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: #4c4c4c;
  }
  
  .btn-sm {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-group {
    display: flex;
    gap: 12px;
    margin-top: 16px;
  }
  
  .alert {
    padding: 16px;
    border-radius: 4px;
    margin-top: 16px;
  }
  
  .alert-success {
    background: rgba(0, 120, 212, 0.1);
    border: 1px solid #0078d4;
    color: #4db8ff;
  }
  
  .alert-error {
    background: rgba(232, 17, 35, 0.1);
    border: 1px solid #e81123;
    color: #ff6b7a;
  }
  
  .alert-info {
    background: rgba(255, 185, 0, 0.1);
    border: 1px solid #ffb900;
    color: #ffd666;
  }
  
  .alert strong {
    display: block;
    margin-bottom: 8px;
    font-size: 15px;
  }
  
  .error-list, .warning-list, .operation-list {
    margin: 12px 0 0 0;
    padding-left: 20px;
  }
  
  .error-list li, .warning-list li, .operation-list li {
    margin: 6px 0;
    font-size: 14px;
  }
  
  .result-section {
    margin-top: 16px;
  }
  
  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .success-badge {
    color: #4db8ff;
    font-weight: 500;
    font-size: 14px;
  }
  
  .yaml-display, .yaml-input {
    width: 100%;
    background: #0d0d0d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: vertical;
  }
  
  .yaml-display {
    background: #1a1a1a;
  }
  
  .copilot-prompt {
    background: #1a1a1a;
    border: 1px solid #0078d4;
    border-left: 4px solid #0078d4;
    padding: 16px;
    margin: 12px 0;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    color: #4db8ff;
    border-radius: 4px;
  }
  
  .file-path {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    margin: 8px 0;
    color: #a0a0a0;
  }
  
  .next-steps {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #3c3c3c;
  }
  
  .next-steps code {
    background: #1a1a1a;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #4db8ff;
  }
  
  .error-text {
    color: #ff6b7a;
  }
</style>
