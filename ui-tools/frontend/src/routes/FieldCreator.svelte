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
  
  // Quick entry form variables
  let quickDisplayName = '';
  let quickType = 'Text';
  let quickRequired = false;
  let quickMaxLength = '';
  let publisherPrefix = '';
  let displayNameInput;
  
  // Template variables
  let templates = [];
  let selectedTemplate = '';
  let newTemplateName = '';
  let newTemplateDescription = '';
  let showSaveTemplateForm = false;
  
  // UI state
  let activeTab = 'settings'; // 'settings', 'create', 'templates', 'help'
  let showQuickAdd = false;
  
  // Field counter
  $: fieldCount = countFields(fieldsText);
  
  $: availableEnvironments = getAvailableEnvironments($config, selectedDeployment);
  
  // Load publisher prefix from localStorage
  onMount(() => {
    const savedPrefix = localStorage.getItem('publisherPrefix');
    if (savedPrefix) {
      publisherPrefix = savedPrefix;
    } else {
      publisherPrefix = 'appbase_';
    }
    
    // Set default deployment
    if ($deployments && $deployments.length > 0) {
      selectedDeployment = $deployments[0];
    }
    
    // Load templates
    loadTemplates();
  });
  
  async function loadTemplates() {
    try {
      const response = await fetch('/api/helpers/field-templates');
      const data = await response.json();
      templates = data.templates || [];
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  }
  
  async function loadTemplate() {
    if (!selectedTemplate) return;
    
    try {
      const response = await fetch(`/api/helpers/field-templates/${encodeURIComponent(selectedTemplate)}`);
      const template = await response.json();
      
      if (template.error) {
        alert(`Error loading template: ${template.error}`);
        return;
      }
      
      // Convert template fields to pipe format
      const lines = template.fields.map(field => {
        const parts = [];
        
        // If template has its own schema names, use them; otherwise generate
        if (field.schemaName) {
          parts.push(field.schemaName);
        } else {
          const schema = (template.publisherPrefix || publisherPrefix) + 
            field.displayName.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, '');
          parts.push(schema);
        }
        
        parts.push(field.displayName);
        parts.push(field.type || 'Text');
        parts.push(field.required ? 'true' : 'false');
        if (field.maxLength) {
          parts.push(field.maxLength.toString());
        }
        
        return parts.join('|');
      });
      
      fieldsText = lines.join('\n');
      
      // Update prefix if template has one
      if (template.publisherPrefix) {
        publisherPrefix = template.publisherPrefix;
      }
      
    } catch (error) {
      alert(`Error loading template: ${error.message}`);
    }
  }
  
  async function saveTemplate() {
    if (!newTemplateName.trim()) {
      alert('Please enter a template name');
      return;
    }
    
    if (!fieldsText.trim()) {
      alert('No fields to save');
      return;
    }
    
    // Parse current fields
    const lines = fieldsText.trim().split('\n');
    const fields = [];
    
    for (const line of lines) {
      if (!line.trim() || line.trim().startsWith('#')) continue;
      
      const parts = line.split('|').map(p => p.trim());
      if (parts.length >= 2) {
        // Store fields in a normalized format
        fields.push({
          displayName: parts[1] || parts[0],
          type: parts[2] || 'Text',
          required: parts[3] === 'true',
          maxLength: parts[4] ? parseInt(parts[4]) : null
        });
      }
    }
    
    try {
      const response = await fetch('/api/helpers/field-templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newTemplateName,
          description: newTemplateDescription,
          publisherPrefix: publisherPrefix,
          fields
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Template "${newTemplateName}" saved successfully!`);
        newTemplateName = '';
        newTemplateDescription = '';
        showSaveTemplateForm = false;
        loadTemplates();
      } else {
        alert(`Error saving template: ${result.error}`);
      }
    } catch (error) {
      alert(`Error saving template: ${error.message}`);
    }
  }
  
  async function deleteTemplate() {
    if (!selectedTemplate) return;
    
    if (!confirm(`Are you sure you want to delete the template "${selectedTemplate}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/helpers/field-templates/${encodeURIComponent(selectedTemplate)}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Template deleted successfully`);
        selectedTemplate = '';
        loadTemplates();
      } else {
        alert(`Error deleting template: ${result.error}`);
      }
    } catch (error) {
      alert(`Error deleting template: ${error.message}`);
    }
  }
  
  // Save publisher prefix to localStorage when changed
  $: if (publisherPrefix) {
    localStorage.setItem('publisherPrefix', publisherPrefix);
  }
  
  function countFields(text) {
    if (!text || !text.trim()) return 0;
    const lines = text.trim().split('\n');
    return lines.filter(line => {
      const trimmed = line.trim();
      return trimmed && !trimmed.startsWith('#');
    }).length;
  }
  
  function generateSchemaName(displayName) {
    if (!displayName || !publisherPrefix) return '';
    // Convert display name to lowercase, remove special chars, keep only alphanumeric
    const cleaned = displayName.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '');
    return publisherPrefix + cleaned;
  }
  
  function addQuickField() {
    if (!quickDisplayName.trim()) {
      alert('Please enter a display name');
      return;
    }
    
    const schemaName = generateSchemaName(quickDisplayName);
    const required = quickRequired ? 'true' : 'false';
    const maxLen = quickMaxLength || '';
    
    // Build field line
    let fieldLine = `${schemaName}|${quickDisplayName}|${quickType}|${required}`;
    if (maxLen) {
      fieldLine += `|${maxLen}`;
    }
    
    // Append to textarea
    if (fieldsText.trim()) {
      fieldsText += '\n' + fieldLine;
    } else {
      fieldsText = fieldLine;
    }
    
    // Clear quick form and refocus
    quickDisplayName = '';
    quickType = 'Text';
    quickRequired = false;
    quickMaxLength = '';
    
    // Focus back on display name input
    setTimeout(() => {
      if (displayNameInput) {
        displayNameInput.focus();
      }
    }, 0);
  }
  
  function handleQuickEntryKeydown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addQuickField();
    }
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

  async function createFields() {
    if (!selectedDeployment || !selectedEnvironment || !tableName || !fieldsText.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    // Parse field definitions
    const lines = fieldsText.trim().split('\n');
    const fields = [];
    const warnings = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim() || line.trim().startsWith('#')) continue;
      
      let schemaName, displayName, type, required, maxLength;
      
      // Check for BUILD.md format: "Display Name: Type" or "Display Name: Type (details)"
      if (line.includes(': ') && !line.includes('|') && !line.includes('::')) {
        const colonIndex = line.indexOf(': ');
        displayName = line.substring(0, colonIndex).trim();
        let typeInfo = line.substring(colonIndex + 2).trim();
        
        // Remove any trailing bullet points or dashes
        displayName = displayName.replace(/^[-•]\s*/, '');
        
        // Extract type (handle parentheses for lookups/choices)
        if (typeInfo.includes('(')) {
          const parenIndex = typeInfo.indexOf('(');
          type = typeInfo.substring(0, parenIndex).trim();
        } else {
          type = typeInfo;
        }
        
        // Normalize type names
        if (type === 'Yes / No' || type === 'Yes/No') {
          type = 'YesNo';
        } else if (type === 'Lookup') {
          warnings.push(`Line ${i + 1}: Lookup fields not yet supported - skipping "${displayName}"`);
          continue;
        } else if (type === 'Choice') {
          warnings.push(`Line ${i + 1}: Choice fields not yet supported - skipping "${displayName}"`);
          continue;
        }
        
        required = false;
        maxLength = null;
        schemaName = generateSchemaName(displayName);
      }
      // Check for manual schema override with "::" notation
      else if (line.includes('::')) {
        const [schema, rest] = line.split('::').map(p => p.trim());
        schemaName = schema;
        const parts = rest.split('|').map(p => p.trim());
        displayName = parts[0] || '';
        type = parts[1] || 'Text';
        required = parts[2] === 'true' || parts[2] === 'yes';
        maxLength = parts[3] ? parseInt(parts[3]) : null;
      }
      // Check for pipe-separated format
      else if (line.includes('|')) {
        const parts = line.split('|').map(p => p.trim());
        
        // If first part looks like a schema name (contains underscore), use legacy format
        if (parts[0].includes('_')) {
          // Legacy format: schemaName|displayName|type|required|maxLength
          schemaName = parts[0];
          displayName = parts[1] || '';
          type = parts[2] || 'Text';
          required = parts[3] === 'true' || parts[3] === 'yes';
          maxLength = parts[4] ? parseInt(parts[4]) : null;
        } else {
          // New format: displayName|type|required|maxLength (auto-generate schema)
          displayName = parts[0];
          type = parts[1] || 'Text';
          required = parts[2] === 'true' || parts[2] === 'yes';
          maxLength = parts[3] ? parseInt(parts[3]) : null;
          schemaName = generateSchemaName(displayName);
        }
      }
      // Simple format: just displayName (defaults to Text)
      else {
        displayName = line.trim();
        type = 'Text';
        required = false;
        maxLength = null;
        schemaName = generateSchemaName(displayName);
      }
      
      // Validate we have required fields
      if (!schemaName || !displayName) {
        alert(`Invalid field definition on line ${i + 1}: ${line}\nMissing schema name or display name`);
        return;
      }
      
      // Apply smart defaults for maxLength
      if (!maxLength) {
        if (type === 'Text' || type === 'String') maxLength = 100;
        else if (type === 'Memo' || type === 'MultilineText') maxLength = 4000;
        else if (type === 'RichText' || type === 'HTML') maxLength = 1048576;
        else if (type === 'URL' || type === 'Url') maxLength = 200;
      }
      
      fields.push({
        schemaName,
        displayName,
        type,
        required,
        maxLength
      });
    }
    
    // Show warnings if any
    if (warnings.length > 0) {
      const warningMsg = warnings.join('\n');
      if (!confirm(`${warnings.length} field(s) will be skipped:\n\n${warningMsg}\n\nContinue with remaining fields?`)) {
        return;
      }
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


  const exampleFields = `# Example field definitions
# BUILD.md format (recommended):
Name: Text
Position Number: Text
Full Time Equivalent: Float
Authorized Date: Date
Is Supervisory: Yes / No
Description: Memo

# Or use simple format:
Customer Full Name
Email Address|URL
Notes|Memo`;


</script>

<div class="field-creator">
  <Header title="Field Creator" description="Mass create fields on Dataverse tables">
    <button class="btn btn-primary" on:click={createFields} disabled={$operationStatus === 'running'}>
      {$operationStatus === 'running' ? '⏳ Creating...' : '▶ Create Fields'}
    </button>
  </Header>

  <!-- Active Settings Indicator -->
  {#if selectedDeployment || selectedEnvironment || publisherPrefix}
    <div class="settings-bar">
      <div class="settings-info">
        {#if selectedDeployment}
          <span class="setting-item">
            <strong>Deployment:</strong> {selectedDeployment}
          </span>
        {/if}
        {#if selectedEnvironment}
          <span class="setting-item">
            <strong>Environment:</strong> {availableEnvironments.find(e => e.key === selectedEnvironment)?.name || selectedEnvironment}
          </span>
        {/if}
        {#if publisherPrefix}
          <span class="setting-item">
            <strong>Prefix:</strong> <code>{publisherPrefix}</code>
          </span>
        {/if}
      </div>
      <button class="btn-link" on:click={() => activeTab = 'settings'}>⚙️ Change Settings</button>
    </div>
  {/if}

  <div class="content">
    <!-- Tab Navigation -->
    <div class="tabs">
      <button 
        class="tab" 
        class:active={activeTab === 'settings'}
        on:click={() => activeTab = 'settings'}
      >
        ⚙️ Settings
      </button>
      <button 
        class="tab" 
        class:active={activeTab === 'create'}
        on:click={() => activeTab = 'create'}
      >
        ✏️ Create Fields
      </button>
      <button 
        class="tab" 
        class:active={activeTab === 'templates'}
        on:click={() => activeTab = 'templates'}
      >
        💾 Templates
      </button>
      <button 
        class="tab" 
        class:active={activeTab === 'help'}
        on:click={() => activeTab = 'help'}
      >
        ℹ️ Help
      </button>
    </div>

    <!-- Settings Tab -->
    {#if activeTab === 'settings'}
      <div class="tab-content">
        <div class="form-container-full">
          <div class="form-section">
            <h3>Target Environment</h3>
            <p class="help-text">Select your deployment and environment. These settings will persist while you create fields across multiple tables.</p>
            
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
          </div>

          <div class="form-section">
            <h3>Publisher Prefix</h3>
            <p class="help-text">This prefix is used to auto-generate schema names from display names. It's saved in your browser for future sessions.</p>
            
            <div class="form-group">
              <label for="publisherPrefix">Publisher Prefix</label>
              <input 
                type="text" 
                id="publisherPrefix" 
                bind:value={publisherPrefix}
                placeholder="e.g., appbase_"
                pattern="[a-z0-9]+_"
              />
              <p class="help-text">Example: With prefix "appbase_", field "Customer Name" becomes "appbase_customername"</p>
            </div>
          </div>

          <div class="info-box success">
            <strong>💡 Next Steps:</strong> After configuring your settings, go to the <button class="btn-link-inline" on:click={() => activeTab = 'create'}>Create Fields</button> tab to start adding fields to tables.
          </div>
        </div>
      </div>
    {/if}

    <!-- Create Fields Tab -->
    {#if activeTab === 'create'}
      <div class="tab-content">
        <div class="form-container-full">
          <div class="form-section">
            <h3>Table Information</h3>
            
            <div class="form-group">
              <label for="tableName">Table Logical Name</label>
              <input 
                type="text" 
                id="tableName" 
                bind:value={tableName}
                placeholder="e.g., contact, appbase_hrposition"
                pattern="[a-z0-9_]+"
              />
              <p class="help-text">Enter the logical name of the target table (lowercase, underscores allowed)</p>
            </div>
          </div>

          <!-- Collapsible Quick Add -->
          <div class="form-section collapsible">
            <button 
              class="section-header-collapsible" 
              type="button"
              on:click={() => showQuickAdd = !showQuickAdd}
            >
              <h3>⚡ Quick Add Field</h3>
              <span class="collapse-icon">{showQuickAdd ? '▼' : '▶'}</span>
            </button>
            
            {#if showQuickAdd}
              <div class="quick-entry-content">
                <div class="quick-entry-grid">
                  <div class="form-group quick-field">
                    <label for="quickDisplayName">Display Name</label>
                    <input 
                      type="text" 
                      id="quickDisplayName" 
                      bind:value={quickDisplayName}
                      bind:this={displayNameInput}
                      on:keydown={handleQuickEntryKeydown}
                      placeholder="e.g., Customer Full Name"
                    />
                    {#if quickDisplayName}
                      <p class="help-text schema-preview">→ {generateSchemaName(quickDisplayName)}</p>
                    {/if}
                  </div>

                  <div class="form-group">
                    <label for="quickType">Type</label>
                    <select id="quickType" bind:value={quickType}>
                      <option value="Text">Text</option>
                      <option value="Memo">Memo (Multiline)</option>
                      <option value="RichText">Rich Text</option>
                      <option value="URL">URL</option>
                      <option value="Integer">Integer</option>
                      <option value="Float">Float</option>
                      <option value="Currency">Currency</option>
                      <option value="Date">Date</option>
                      <option value="DateTime">Date & Time</option>
                      <option value="YesNo">Yes/No</option>
                    </select>
                  </div>

                  <div class="form-group quick-checkbox">
                    <label>
                      <input type="checkbox" bind:checked={quickRequired} />
                      Required
                    </label>
                  </div>

                  <div class="form-group">
                    <label for="quickMaxLength">Max Length</label>
                    <input 
                      type="number" 
                      id="quickMaxLength" 
                      bind:value={quickMaxLength}
                      placeholder="Auto"
                    />
                  </div>

                  <div class="form-group quick-button">
                    <button type="button" class="btn btn-add" on:click={addQuickField}>
                      ➕ Add
                    </button>
                  </div>
                </div>
                
                <p class="help-text">Press Enter in Display Name to quickly add • Schema name auto-generated from Display Name</p>
              </div>
            {/if}
          </div>

          <div class="form-section">
            <div class="section-header">
              <h3>Field Definitions</h3>
              {#if fieldCount > 0}
                <span class="field-count">✓ {fieldCount} field{fieldCount !== 1 ? 's' : ''} ready</span>
              {/if}
            </div>
            
            <div class="form-group">
              <label for="fieldsText">Fields (one per line)</label>
              <textarea 
                id="fieldsText"
                bind:value={fieldsText}
                placeholder={exampleFields}
                rows="20"
              ></textarea>
              <p class="help-text">
                📋 <strong>Copy/paste from BUILD.md:</strong> Bullet points auto-removed • Format: <code>- Name: Type</code> or <code>Display Name: Type</code> • Use <code>#</code> for comments • Lookup/Choice fields skipped with warning
              </p>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Templates Tab -->
    {#if activeTab === 'templates'}
      <div class="tab-content">
        <div class="form-container-full">
          <div class="form-section">
            <h3>💾 Field Templates</h3>
            
            <div class="template-controls">
              <div class="form-group">
                <label for="templateSelect">Load Template</label>
                <div class="template-actions">
                  <select id="templateSelect" bind:value={selectedTemplate}>
                    <option value="">-- Select Template --</option>
                    {#each templates as template}
                      <option value={template.name}>{template.name} ({template.fieldCount} fields)</option>
                    {/each}
                  </select>
                  <button 
                    type="button" 
                    class="btn btn-secondary" 
                    on:click={loadTemplate}
                    disabled={!selectedTemplate}
                  >
                    Load
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-danger" 
                    on:click={deleteTemplate}
                    disabled={!selectedTemplate}
                    title="Delete selected template"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <div class="form-group">
                <button 
                  type="button" 
                  class="btn btn-secondary btn-block"
                  on:click={() => showSaveTemplateForm = !showSaveTemplateForm}
                >
                  {showSaveTemplateForm ? '✖ Cancel' : '💾 Save Current as Template'}
                </button>
              </div>

              {#if showSaveTemplateForm}
                <div class="save-template-form">
                  <div class="form-group">
                    <label for="newTemplateName">Template Name</label>
                    <input 
                      type="text" 
                      id="newTemplateName" 
                      bind:value={newTemplateName}
                      placeholder="e.g., Contact Fields"
                    />
                  </div>

                  <div class="form-group">
                    <label for="newTemplateDescription">Description (optional)</label>
                    <input 
                      type="text" 
                      id="newTemplateDescription" 
                      bind:value={newTemplateDescription}
                      placeholder="Brief description"
                    />
                  </div>

                  <button 
                    type="button" 
                    class="btn btn-primary btn-block"
                    on:click={saveTemplate}
                  >
                    💾 Save Template
                  </button>
                </div>
              {/if}
            </div>

            <div class="info-box">
              <h4>About Templates</h4>
              <p>Templates save your field definitions for reuse across different tables. They include:</p>
              <ul>
                <li>Field display names and types</li>
                <li>Required flags and max lengths</li>
                <li>Your publisher prefix setting</li>
              </ul>
              <p>Use templates to quickly recreate common field sets like "Address Fields", "Contact Info", or "Audit Fields".</p>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Help Tab -->
    {#if activeTab === 'help'}
      <div class="tab-content">
        <div class="form-container-full">
          <div class="form-section">
            <h3>ℹ️ How to Use</h3>
            <ol class="help-list">
              <li>Go to <strong>Settings</strong> tab and select your deployment, environment, and publisher prefix</li>
              <li>Return to <strong>Create Fields</strong> tab</li>
              <li>Enter the table logical name (this changes table-by-table)</li>
              <li><strong>Copy/paste from BUILD.md</strong> or use Quick Add form</li>
              <li>Review and edit field definitions as needed</li>
              <li>Lookup/Choice fields will be skipped (not yet supported)</li>
              <li>Click "Create Fields" and monitor progress</li>
            </ol>
            <div class="info-box success">
              <strong>💡 Tip:</strong> The BUILD.md format (<code>- Name: Type</code>) works great for copy/paste from your documentation! The settings bar at the top shows your active deployment and environment.
            </div>
          </div>

          <div class="form-section">
            <h3>⚠️ Important Notes</h3>
            <ul class="help-list">
              <li>Schema names auto-generated with your prefix</li>
              <li>Schema names cannot be changed after creation</li>
              <li>Review all fields before clicking Create</li>
              <li>Lookup and Choice fields require manual creation</li>
              <li>Smart defaults for max lengths applied automatically</li>
              <li>Always test in a development environment first</li>
            </ul>
          </div>

          <div class="form-section">
            <h3>📋 Supported Field Types</h3>
            <div class="type-grid">
              <div>
                <strong>Text Types:</strong>
                <ul class="type-list-compact">
                  <li>Text - Single line (100)</li>
                  <li>Memo - Multiline (4000)</li>
                  <li>RichText - HTML (1MB)</li>
                  <li>URL - Web link (200)</li>
                </ul>
              </div>
              <div>
                <strong>Number Types:</strong>
                <ul class="type-list-compact">
                  <li>Integer - Whole number</li>
                  <li>Float - Decimal</li>
                  <li>Currency - Money</li>
                </ul>
              </div>
              <div>
                <strong>Other Types:</strong>
                <ul class="type-list-compact">
                  <li>Date - Date only</li>
                  <li>DateTime - Date & time</li>
                  <li>YesNo - Boolean</li>
                </ul>
              </div>
            </div>
            <div class="info-box warning">
              <strong>⚠️ Not Yet Supported:</strong> Lookup, Choice (coming soon)
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .field-creator {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .settings-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 2rem;
    background: #2d2d30;
    border-bottom: 1px solid #3c3c3c;
    font-size: 13px;
  }

  .settings-info {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: center;
  }

  .setting-item {
    color: #cccccc;
  }

  .setting-item strong {
    color: #4fc3f7;
    font-weight: 600;
    margin-right: 0.5rem;
  }

  .setting-item code {
    background: #1e1e1e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #a5d6a7;
    font-size: 12px;
  }

  .btn-link {
    background: transparent;
    color: #4fc3f7;
    border: none;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    border-radius: 4px;
    transition: background 0.2s;
  }

  .btn-link:hover {
    background: rgba(0, 120, 212, 0.1);
  }

  .btn-link-inline {
    background: transparent;
    color: #4fc3f7;
    border: none;
    padding: 0;
    cursor: pointer;
    font-size: inherit;
    font-weight: 600;
    text-decoration: underline;
  }

  .btn-link-inline:hover {
    color: #6ec6ff;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tabs {
    display: flex;
    gap: 0.25rem;
    padding: 1rem 2rem 0 2rem;
    background: #1e1e1e;
    border-bottom: 2px solid #3c3c3c;
  }

  .tab {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: #cccccc;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.2s;
  }

  .tab:hover {
    background: #252526;
    color: #ffffff;
  }

  .tab.active {
    color: #0078d4;
    border-bottom-color: #0078d4;
    background: #252526;
  }

  .tab-content {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
  }

  .form-container-full {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
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



  .type-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    color: #cccccc;
    font-size: 13px;
  }

  .type-grid strong {
    color: #4fc3f7;
    display: block;
    margin-bottom: 0.5rem;
  }

  .type-list-compact {
    margin: 0;
    padding-left: 1.25rem;
    list-style-type: disc;
  }

  .type-list-compact li {
    margin-bottom: 0.25rem;
    color: #cccccc;
  }

  @media (max-width: 768px) {
    .type-grid {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }

  /* Template Styles */
  .info-box {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    margin-top: 1rem;
    color: #cccccc;
    font-size: 13px;
    line-height: 1.6;
  }

  .info-box h4 {
    margin: 0 0 0.75rem 0;
    font-size: 14px;
    color: #4fc3f7;
    font-weight: 600;
  }

  .info-box.success {
    border-left: 4px solid #28a745;
  }

  .info-box.warning {
    border-left: 4px solid #f44336;
  }

  .info-box strong {
    color: #ffffff;
  }

  .info-box code {
    background: #252526;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #4fc3f7;
    font-size: 11px;
  }

  .info-box ul, .info-box p {
    margin: 0.5rem 0;
  }

  .info-box ul {
    padding-left: 1.25rem;
  }

  .info-box li {
    margin-bottom: 0.25rem;
  }

  .help-list {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
    color: #cccccc;
    font-size: 14px;
    line-height: 1.8;
  }

  .help-list li {
    margin-bottom: 0.75rem;
  }

  .help-list strong {
    color: #ffffff;
  }



  @media (max-width: 1200px) {
    .tab-content {
      padding: 1.5rem;
    }
  }



  .collapsible {
    cursor: pointer;
  }

  .section-header-collapsible {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    user-select: none;
    text-align: left;
    color: inherit;
  }

  .section-header-collapsible:hover {
    opacity: 0.8;
  }

  .section-header-collapsible h3 {
    margin: 0;
  }

  .collapse-icon {
    color: #0078d4;
    font-size: 12px;
    transition: transform 0.2s;
  }

  .quick-entry-content {
    padding-top: 1.5rem;
  }

  .quick-entry-grid {
    display: grid;
    grid-template-columns: 2fr 1.5fr auto 1fr auto;
    gap: 0.75rem;
    align-items: end;
  }

  .quick-field {
    min-width: 0;
  }

  .quick-checkbox {
    display: flex;
    align-items: center;
    padding-top: 1.5rem;
  }

  .quick-checkbox label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    cursor: pointer;
    user-select: none;
  }

  .quick-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  .quick-button {
    padding-top: 0;
  }

  .btn-add {
    width: 100%;
    padding: 0.625rem 1rem;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
  }

  .btn-add:hover {
    background: #218838;
  }

  .btn-add:active {
    background: #1e7e34;
  }

  .schema-preview {
    color: #4fc3f7 !important;
    font-family: 'Consolas', 'Courier New', monospace;
    margin-top: 0.25rem !important;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .section-header h3 {
    margin: 0;
  }

  .field-count {
    color: #28a745;
    font-weight: 600;
    font-size: 14px;
  }

  @media (max-width: 900px) {
    .quick-entry-grid {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .quick-checkbox {
      padding-top: 0;
    }

    .quick-button {
      padding-top: 0;
    }
  }

  /* Template Styles */
  .template-controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .template-actions {
    display: flex;
    gap: 0.5rem;
  }

  .template-actions select {
    flex: 1;
  }

  .btn-secondary {
    padding: 0.625rem 1rem;
    background: #555555;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
    white-space: nowrap;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #666666;
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-danger {
    padding: 0.625rem 0.75rem;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
  }

  .btn-danger:hover:not(:disabled) {
    background: #c82333;
  }

  .btn-danger:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-block {
    width: 100%;
  }

  .save-template-form {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    margin-top: 0.5rem;
  }

  .save-template-form .form-group {
    margin-bottom: 1rem;
  }

  .save-template-form .form-group:last-child {
    margin-bottom: 0;
  }
</style>
